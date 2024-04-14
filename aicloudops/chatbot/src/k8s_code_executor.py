from typing import List, Union
from pathlib import Path
from kubernetes import client, config
from kubernetes.client.rest import ApiException
from autogen.coding.base import CodeBlock, CommandLineCodeResult
from autogen.coding.utils import _get_file_name_from_content

from hashlib import md5
import logging
from time import sleep
import uuid
import datetime

from rabbitmq_publisher import RabbitMQPublisher

from autogen.code_utils import _cmd
from autogen.coding.base import CodeExecutor, CodeExtractor
from autogen.coding.markdown_code_extractor import MarkdownCodeExtractor


class K8sCodeExecutor(CodeExecutor):
    def __init__(
        self,
        image: str = "public.ecr.aws/c6w3t1p6/boto3-code-exec:latest",
        namespace: str = "default",
        timeout: int = 60,
        work_dir: Union[Path, str] = Path("/tmp"),
    ):
        super().__init__()
        self._namespace = namespace
        self._work_dir = Path(work_dir)
        self._image = image
        self._timeout = timeout
        # config.load_kube_config()
        # Use in-cluster configuration
        config.load_incluster_config()
        self._api = client.BatchV1Api()
        self._core_api = client.CoreV1Api()
        print(
            f"K8sCodeExecutor initialized with image {image}, namespace {namespace}, timeout {timeout}, work_dir {work_dir}"
        )

    @property
    def code_extractor(self) -> CodeExtractor:
        """(Experimental) Export a code extractor that can be used by an agent."""
        return MarkdownCodeExtractor()

    def execute_code_blocks(
        self, code_blocks: List[CodeBlock]
    ) -> CommandLineCodeResult:
        if len(code_blocks) == 0:
            raise ValueError("No code blocks to execute.")

        print(f"Executing {len(code_blocks)} code blocks...")

        outputs = []
        files = []
        last_exit_code = 0

        for code_block in code_blocks:
            lang = code_block.language
            code = code_block.code

            try:
                # Check if there is a filename comment
                filename = _get_file_name_from_content(code, Path("/tmp"))
                file_uuid = uuid.uuid4()
                if filename.endswith(".py"):
                    filename = filename[:-3]  # Remove the .py extension
                filename = f"{filename}_{file_uuid}.py"  # Append UUID and add .py back
            except ValueError:
                return CommandLineCodeResult(
                    exit_code=1, output="Filename is not in the workspace"
                )

            if filename is None:
                # create a file with an automatically generated name
                code_hash = md5(code.encode()).hexdigest()
                filename = f"tmp_code_{code_hash}.{'py' if lang.startswith('python') else lang}"

            code_path = self._work_dir / filename
            with code_path.open("w", encoding="utf-8") as fout:
                fout.write(code)

            job_name = f"code-exec-{uuid.uuid4()}"
            job = client.V1Job(
                kind="Job",
                metadata=client.V1ObjectMeta(name=job_name),
                spec=client.V1JobSpec(
                    template=client.V1PodTemplateSpec(
                        spec=client.V1PodSpec(
                            containers=[
                                client.V1Container(
                                    name="code-executor",
                                    image=self._image,
                                    command=[
                                        "timeout",
                                        str(self._timeout),
                                        _cmd(lang),
                                        filename,
                                    ],
                                    working_dir="/tmp",
                                    env=[
                                        client.V1EnvVar(
                                            name="AWS_ACCESS_KEY_ID",
                                            value_from=client.V1EnvVarSource(
                                                secret_key_ref=client.V1SecretKeySelector(
                                                    name="chatbot-env",
                                                    key="AWS_ACCESS_KEY_ID",
                                                )
                                            ),
                                        ),
                                        client.V1EnvVar(
                                            name="AWS_SECRET_ACCESS_KEY",
                                            value_from=client.V1EnvVarSource(
                                                secret_key_ref=client.V1SecretKeySelector(
                                                    name="chatbot-env",
                                                    key="AWS_SECRET_ACCESS_KEY",
                                                )
                                            ),
                                        ),
                                    ],
                                    volume_mounts=[
                                        client.V1VolumeMount(
                                            name="code",
                                            mount_path="/tmp",
                                        )
                                    ],
                                )
                            ],
                            volumes=[
                                client.V1Volume(
                                    name="code",
                                    persistent_volume_claim=client.V1PersistentVolumeClaimVolumeSource(
                                        claim_name="ai-code-pvc"
                                    ),
                                    # host_path=client.V1HostPathVolumeSource(path=str(self._work_dir)),
                                )
                            ],
                            service_account_name="code-executor-service-account",
                            restart_policy="Never",
                        )
                    ),
                    backoff_limit=0,
                ),
            )

            # create the job
            try:
                self._api.create_namespaced_job(self._namespace, job)
                print(f"Job {job.metadata.name} created successfully.")
                print("Waiting for job completion...")
            except ApiException as e:
                print(f"Failed to create job: {e}")
                return CommandLineCodeResult(
                    exit_code=1, output=f"Failed to create job: {e}"
                )

            # Wait for job completion and handle errors gracefully
            job_completed_successfully = False
            try:
                while True:
                    job_status = self._api.read_namespaced_job_status(
                        job_name, self._namespace
                    )
                    if job_status.status.succeeded:
                        job_completed_successfully = True
                        print("EXECUTED AT: ", datetime.datetime.now(), "\n")
                        break
                    elif job_status.status.failed:
                        break
                    sleep(3)
            except ApiException as e:
                outputs.append(f"Error checking job status: {e}")
                last_exit_code = 1
                continue  # Skip to the next code block

            # Retrieve pod name
            try:
                pods = self._core_api.list_namespaced_pod(
                    namespace=self._namespace, label_selector=f"job-name={job_name}"
                )
                pod_name = next(
                    (
                        pod.metadata.name
                        for pod in pods.items
                        if pod.metadata.labels["job-name"] == job_name
                    ),
                    None,
                )
            except ApiException as e:
                outputs.append(f"Failed to list pods: {e}")
                last_exit_code = 1
                continue  # Skip to the next code block

            if pod_name is None:
                outputs.append("Failed to find pod for job")
                last_exit_code = 1
                continue  # Skip to the next code block

            # Retrieve logs from the pod, including errors
            try:
                pod_logs = self._core_api.read_namespaced_pod_log(
                    name=pod_name, namespace=self._namespace
                )
                outputs.append(pod_logs)
            except ApiException as e:
                outputs.append(f"Failed to read pod logs: {e}")
                last_exit_code = 1
                continue  # Skip to the next code block

            if not job_completed_successfully:
                last_exit_code = 1

            # Clean up job
            try:
                self._api.delete_namespaced_job(
                    name=job_name,
                    namespace=self._namespace,
                    propagation_policy="Background",
                )
                print("Job deleted successfully")
            except ApiException as e:
                logging.warning(f"Failed to delete job {job_name}: {e}")

        execution_output = "\n".join(outputs)

        with RabbitMQPublisher() as queue:
            queue.log_execution(str(code_path), last_exit_code, execution_output)

        return CommandLineCodeResult(exit_code=last_exit_code, output=execution_output)
