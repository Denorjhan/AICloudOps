from __future__ import annotations
import atexit
from pathlib import Path
from time import sleep
from types import TracebackType
import uuid
from typing import List, Optional, Type, Union
import docker
from docker.models.containers import Container
from docker.errors import ImageNotFound

from autogen.coding.base import CommandLineCodeResult
from autogen.coding import DockerCommandLineCodeExecutor

from autogen.code_utils import TIMEOUT_MSG, _cmd
from autogen.coding.base import CodeBlock, CodeExtractor
from autogen.coding.markdown_code_extractor import MarkdownCodeExtractor
import sys
import os
import datetime
from utils import code_block_to_file, validate_code_blocks, create_msg_body
from code_execution_publisher import CodeExecutionPublisher

if sys.version_info >= (3, 11):
    from typing import Self
else:
    from typing_extensions import Self


def _wait_for_ready(
    container: Container, timeout: int = 60, stop_time: int = 0.1
) -> None:
    elapsed_time = 0
    while container.status != "running" and elapsed_time < timeout:
        sleep(stop_time)
        elapsed_time += stop_time
        container.reload()
    if container.status != "running":
        print(f"Container {container.name} failed to start within {timeout} seconds.")
        raise ValueError("Container failed to start")
    else:
        print("Sandbox environment created...")


class DockerCodeExecutor(DockerCommandLineCodeExecutor):
    def __init__(
        self,
        image: str = "public.ecr.aws/c6w3t1p6/boto3-code-exec:latest",
        container_name: [str] = None,
        timeout: int = 60,
        container_work_dir: Union[Path, str] = Path("/tmp"),
        auto_remove: bool = True,
        stop_container: bool = True,
    ):
        """A custom code executor class that executes code through
        a command line environment in a Docker container, using a container path for volumes.

        Args:
            image (_type_, optional): Docker image to use for code execution.
            container_name (Optional[str], optional): Name of the Docker container which is created. If None, will autogenerate a name. Defaults to None.
            timeout (int, optional): The timeout for code execution. Defaults to 60.
            container_work_dir (Union[Path, str], optional): The working directory inside the container for the code execution. Defaults to Path("/workspace").
            auto_remove (bool, optional): If true, will automatically remove the Docker container when it is stopped. Defaults to True.
            stop_container (bool, optional): If true, will automatically stop the container when stop is called, when the context manager exits, or when the Python process exits with atexit. Defaults to True.
        """

        print("Creating sandbox environment...")

        if timeout < 1:
            raise ValueError("Timeout must be greater than or equal to 1.")

        if isinstance(container_work_dir, str):
            container_work_dir = Path(container_work_dir)

        client = docker.from_env()

        # Check if the image exists
        try:
            client.images.get(image)
        except ImageNotFound:
            print(f"Image {image} not found locally. Attempting to pull...")
            try:
                client.images.pull(image)
                print(f"Successfully pulled image {image}.")
            except ImageNotFound:
                print(f"Failed to pull image {image}. Image not found in registry.")
                raise

        if container_name is None:
            container_name = f"code-exec-{uuid.uuid4()}"

        # identify the shared volume and the mount point
        volume_name = os.getenv("VOLUME_NAME")
        container_work_dir = Path(container_work_dir).absolute()
        creds = {
            "AWS_ACCESS_KEY_ID": os.getenv("AWS_ACCESS_KEY_ID"),
            "AWS_SECRET_ACCESS_KEY": os.getenv("AWS_SECRET_ACCESS_KEY"),
            "AWS_DEFAULT_REGION": os.getenv("AWS_DEFAULT_REGION"),
        }
        self._container = client.containers.create(
            image,
            name=container_name,
            # entrypoint="/bin/sh",
            # tty=True,
            auto_remove=auto_remove,
            volumes={str(volume_name): {"bind": str(container_work_dir), "mode": "rw"}},
            # "~/.aws": {"bind": "/root/.aws", "mode": "ro"}},
            working_dir=str(container_work_dir),
            environment=creds,
        )
        self._container.start()

        _wait_for_ready(self._container)

        def cleanup():
            try:
                container = client.containers.get(container_name)
                container.stop()
            except docker.errors.NotFound:
                pass

            atexit.unregister(cleanup)

        if stop_container:
            atexit.register(cleanup)

        self._cleanup = cleanup

        # Check if the container is running
        if self._container.status != "running":
            raise ValueError(
                f"Failed to start container from image {image}. Logs: {self._container.logs()}"
            )

        self._timeout = timeout
        self._work_dir: Path = container_work_dir

    @property
    def timeout(self) -> int:
        """(Experimental) The timeout for code execution."""
        return self._timeout

    @property
    def work_dir(self) -> Path:
        """(Experimental) The working directory for the code execution."""
        return self._work_dir

    @property
    def code_extractor(self) -> CodeExtractor:
        """(Experimental) Export a code extractor that can be used by an agent."""
        return MarkdownCodeExtractor()

    def execute_code_blocks(
        self, code_blocks: List[CodeBlock]
    ) -> CommandLineCodeResult:
        """(Experimental) Execute the code blocks and return the result.

        Args:
            code_blocks (List[CodeBlock]): The code blocks to execute.

        Returns:
            CommandlineCodeResult: The result of the code execution."""

        validate_code_blocks(code_blocks)
        code_block = code_blocks[0]
        file_path = code_block_to_file(code_block, self._work_dir)

        # execute the file
        command = ["timeout", str(self._timeout), _cmd(code_block.language), file_path]
        print("EXECUTED AT: ", datetime.datetime.now(), "\n")

        # collect the execution result
        execution_result = self._container.exec_run(command)
        exit_code = execution_result.exit_code

        output = execution_result.output.decode("utf-8")
        if exit_code == 124:
            output += "\n"
            output += TIMEOUT_MSG

        # send to logger service to be inserted into the database
        publisher = CodeExecutionPublisher()
        msg = create_msg_body(file_path, exit_code, output)
        publisher.publish(msg)
        publisher.close_connection()

        return CommandLineCodeResult(
            exit_code=exit_code, output=output, code_file=file_path
        )

    def restart(self) -> None:
        """(Experimental) Restart the code executor."""
        self._container.restart()
        if self._container.status != "running":
            raise ValueError(
                f"Failed to restart container. Logs: {self._container.logs()}"
            )

    def stop(self) -> None:
        """(Experimental) Stop the code executor."""
        self._cleanup()

    def __enter__(self) -> Self:
        return self

    def __exit__(
        self,
        exc_type: Optional[Type[BaseException]],
        exc_val: Optional[BaseException],
        exc_tb: Optional[TracebackType],
    ) -> None:
        self.stop()
