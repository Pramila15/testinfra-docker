import pytest
import subprocess
from testinfra import get_host

@pytest.fixture(scope="session")
def docker_container(request):
    """
    Starts a Docker container for testing and yields the testinfra host object.

    Provides error handling and retry logic for handling potential issues during
    image pull and container creation.
    """

    image_reference = "image:tag"

    def run_docker_command(cmd):
        try:
            return subprocess.check_output(cmd).decode().strip()
        except subprocess.CalledProcessError as e:
            raise Exception(f"Error running command: {e}")

    def pull_image():
        output = run_docker_command(["docker", "images", "-q", image_reference])
        if not output:
            run_docker_command(["docker", "pull", image_reference])

    def start_container():
        output = run_docker_command(["docker", "run", "-d", image_reference, "sleep", "infinity"])
        return output

    pull_image()

    container_id = start_container()

    try:
        yield get_host(f"docker://{container_id}")
    finally:
        run_docker_command(["docker", "stop", container_id])
        run_docker_command(["docker", "rm", "-f", container_id])

@pytest.mark.usefixtures("docker_container")
def test_packages_installed(docker_container):
    """
    Checks if Python binary is present within the container.
    """
    assert docker_container.exists("/usr/bin/python") or docker_container.exists("/usr/bin/python3")
    assert docker_container.run("python3 -c 'import redis'").succeeded
    assert docker_container.run("python3 -c 'import toolz'").succeeded
    assert docker_container.run("python3 -c 'import jpype'").succeeded
    assert docker_container.run("python3 -c 'import git'").succeeded
    
@pytest.mark.usefixtures("docker_container")
def test_if_file_exists(docker_container):
    """
    Checks if a specific file exists within the Docker container.
    """
    file_path = 'file.py'
    assert docker_container.run(f"test -e {file_path}").succeeded
