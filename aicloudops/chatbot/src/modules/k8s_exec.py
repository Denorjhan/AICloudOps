from kubernetes import client, config
from kubernetes.client.rest import ApiException
import uuid

class K8sCronJobExecutor:
    def __init__(self, image: str, schedule: str, command: list, env_vars: dict, volume_mounts: list, volumes: list):
        self.image = image
        self.schedule = schedule
        self.command = command
        self.env_vars = env_vars
        self.volume_mounts = volume_mounts
        self.volumes = volumes
        self.job_name = f"code-exec-{uuid.uuid4()}"
        config.load_kube_config()  # Load config from .kube/config

    def create_cron_job(self):
        batch_v1_beta = client.BatchV1beta1Api()
        cron_job = client.V1beta1CronJob(
            api_version="batch/v1beta1",
            kind="CronJob",
            metadata=client.V1ObjectMeta(name=self.job_name),
            spec=client.V1beta1CronJobSpec(
                schedule=self.schedule,
                job_template=client.V1beta1JobTemplateSpec(
                    spec=client.V1JobSpec(
                        template=client.V1PodTemplateSpec(
                            spec=client.V1PodSpec(
                                containers=[client.V1Container(
                                    name=self.job_name,
                                    image=self.image,
                                    command=self.command,
                                    env=[client.V1EnvVar(name=k, value=v) for k, v in self.env_vars.items()],
                                    volume_mounts=self.volume_mounts
                                )],
                                restart_policy="OnFailure",
                                volumes=self.volumes
                            )
                        )
                    )
                )
            )
        )
        try:
            batch_v1_beta.create_namespaced_cron_job(namespace="default", body=cron_job)
            print(f"CronJob {self.job_name} created")
        except ApiException as e:
            print(f"Exception when creating cron job: {e}")

    def delete_cron_job(self):
        batch_v1_beta = client.BatchV1beta1Api()
        try:
            batch_v1_beta.delete_namespaced_cron_job(name=self.job_name, namespace="default")
            print(f"CronJob {self.job_name} deleted")
        except ApiException as e:
            print(f"Exception when deleting cron job: {e}")