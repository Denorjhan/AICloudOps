from __future__ import annotations
import atexit
from hashlib import md5
import logging
from pathlib import Path
from time import sleep
from types import TracebackType
import uuid
from typing import List, Optional, Type, Union
import docker
from docker.models.containers import Container
from docker.errors import ImageNotFound

from autogen.coding.utils import _get_file_name_from_content
from autogen.coding.base import CommandLineCodeResult
from autogen.coding import DockerCommandLineCodeExecutor

from autogen.code_utils import TIMEOUT_MSG, _cmd
from autogen.coding.base import CodeBlock, CodeExecutor, CodeExtractor
from autogen.coding.markdown_code_extractor import MarkdownCodeExtractor
import sys
import datetime
import os
from .queue_producer import RabbitMQPublisher

if sys.version_info >= (3, 11):
    from typing import Self
else:
    from typing_extensions import Self

def _wait_for_ready(container: Container, timeout: int = 60, stop_time: int = 0.1) -> None:
    elapsed_time = 0
    while container.status != "running" and elapsed_time < timeout:
        sleep(stop_time)
        elapsed_time += stop_time
        container.reload()
        continue
    if container.status != "running":
        raise ValueError("Container failed to start")

# def get_volume_name():
#     name = os.getenv("VOLUME_NAME")
#     return f"project_{name}" if name else "ai_code"
    

__all__ = ("ContainerPathDockerExecutor",)


class ContainerPathDockerExecutor(DockerCommandLineCodeExecutor):
    def __init__(
        self,
        image: str = "python:3-slim",
        container_name: Optional[str] = None,
        timeout: int = 60,
        container_work_dir: Union[Path, str] = Path("/tmp"),
        auto_remove: bool = True,
        stop_container: bool = True,

    ):
        """A custom code executor class that executes code through
        a command line environment in a Docker container, using a container path for volumes.

        Args:
            image (_type_, optional): Docker image to use for code execution. Defaults to "python:3-slim".
            container_name (Optional[str], optional): Name of the Docker container which is created. If None, will autogenerate a name. Defaults to None.
            timeout (int, optional): The timeout for code execution. Defaults to 60.
            container_work_dir (Union[Path, str], optional): The working directory inside the container for the code execution. Defaults to Path("/workspace").
            auto_remove (bool, optional): If true, will automatically remove the Docker container when it is stopped. Defaults to True.
            stop_container (bool, optional): If true, will automatically stop the container when stop is called, when the context manager exits, or when the Python process exits with atexit. Defaults to True.
        """

        print("Creating execution container...")

        if timeout < 1:
            raise ValueError("Timeout must be greater than or equal to 1.")

        if isinstance(container_work_dir, str):
            container_work_dir = Path(container_work_dir)

        client = docker.from_env()

        # Check if the image exists
        try:
            client.images.get(image)
        except ImageNotFound:
            logging.info(f"Pulling image {image}...")
            # Let the docker exception escape if this fails.
            client.images.pull(image)

        if container_name is None:
            container_name = f"code-exec-{uuid.uuid4()}"

        # identiy the shared volume and the mount point
        volume_name = os.getenv("VOLUME_NAME")
        print(volume_name)
        container_work_dir = Path(container_work_dir).absolute()
        creds = {
            "AWS_ACCESS_KEY_ID": os.getenv("AWS_ACCESS_KEY_ID"),
            "AWS_SECRET_ACCESS_KEY": os.getenv("AWS_SECRET_ACCESS_KEY"),
            "AWS_DEFAULT_REGION": os.getenv("AWS_DEFAULT_REGION")
        }
        print(container_work_dir)
        
        self._container = client.containers.create(
            image,
            name=container_name,
            entrypoint="/bin/sh",
            tty=True,
            auto_remove=auto_remove,
            volumes={str(volume_name):{"bind": str(container_work_dir), "mode": "rw"}},
            working_dir=str(container_work_dir),
            environment=creds,        
        )
        self._container.start()
        print("Execution container started...")
 
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
            raise ValueError(f"Failed to start container from image {image}. Logs: {self._container.logs()}")

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

    def execute_code_blocks(self, code_blocks: List[CodeBlock]) -> CommandLineCodeResult:
        """(Experimental) Execute the code blocks and return the result.

        Args:
            code_blocks (List[CodeBlock]): The code blocks to execute.

        Returns:
            CommandlineCodeResult: The result of the code execution."""

        if len(code_blocks) == 0:
            raise ValueError("No code blocks to execute.")

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
                if filename.endswith('.py'):
                    filename = filename[:-3]  # Remove the .py extension
                filename = f"{filename}_{file_uuid}.py"  # Append UUID and add .py back
            except ValueError:
                return CommandLineCodeResult(exit_code=1, output="Filename is not in the workspace")

            if filename is None:
                # create a file with an automatically generated name
                code_hash = md5(code.encode()).hexdigest()
                filename = f"tmp_code_{code_hash}.{'py' if lang.startswith('python') else lang}"

            code_path = self._work_dir / filename
            with code_path.open("w", encoding="utf-8") as fout:
                fout.write(code)

            command = ["timeout", str(self._timeout), _cmd(lang), filename]

            result = self._container.exec_run(command)
            exit_code = result.exit_code
            output = result.output.decode("utf-8")
            if exit_code == 124:
                output += "\n"
                output += TIMEOUT_MSG

            outputs.append(output)
            files.append(code_path)

            last_exit_code = exit_code
            if exit_code != 0:
                break
            
        code_file = str(files[0]) if files else None
        code_output = "".join(outputs)
        
        exec_result = CommandLineCodeResult(exit_code=last_exit_code, output=code_output, code_file=code_file)
        
        # print("***************", type(last_exit_code), type(code_output), type(code_file), type(exec_result))
        # print("\n#############", exec_result)
        print("EXECUTED AT: ", datetime.datetime.now(), "\n")
        
        # with RabbitMQPublisher() as queue:
        #     queue.log_execution(code_file, last_exit_code, code_output)
        
        return exec_result

    def restart(self) -> None:
        """(Experimental) Restart the code executor."""
        self._container.restart()
        if self._container.status != "running":
            raise ValueError(f"Failed to restart container. Logs: {self._container.logs()}")

    def stop(self) -> None:
        """(Experimental) Stop the code executor."""
        self._cleanup()

    def __enter__(self) -> Self:
        return self

    def __exit__(
        self, exc_type: Optional[Type[BaseException]], exc_val: Optional[BaseException], exc_tb: Optional[TracebackType]
    ) -> None:
        self.stop()

