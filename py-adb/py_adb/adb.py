import os
import subprocess
from typing import List

from commons import CommandResult

from .exceptions import AdbHaveMultipleMatches, AdbIsNotAvailable


class Adb:
    BINARY_NAME = 'adb.exe' if os.name == 'nt' else 'adb'
    BINARY_PATH = None

    def __init__(self):
        if not self._is_adb_available():
            raise AdbIsNotAvailable()

        binaries = self._discover_from_path(self.BINARY_NAME)
        if len(binaries) > 1:
            raise AdbHaveMultipleMatches()

        self.BINARY_PATH = binaries[0]

    def _run_command(
        self, commands: List[str], timeout: int = None
    ) -> CommandResult:
        """
        Executes ADB commands.

        :param commands: List of command strings to be executed.
        :param timeout: Maximum time (in seconds) for command execution.
        :return: A CommandResult object containing the execution details.
        """
        args = [self.BINARY_PATH] + commands
        try:
            result = subprocess.run(
                args,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                timeout=timeout,
                universal_newlines=True,
                shell=True,
                check=True,
            )
            stdout = result.stdout.split('\n') if result.stdout else None
            stderr = result.stderr.split('\n') if result.stderr else None
            return CommandResult(stdout, stderr, result.returncode)
        except subprocess.TimeoutExpired:
            return CommandResult(None, None, 1)
        except subprocess.CalledProcessError as e:
            stderr = e.stderr.split('\n') if e.stderr else None
            return CommandResult(None, stderr, e.returncode)

    @classmethod
    def _discover_from_path(cls, binary_name: str) -> List[str]:
        """
        Searches for a binary listed in the $PATH environment variable.

        :param binary_name: Name of the binary to search for.
        :return: List of full paths where the binary was found.
        """

        paths = os.getenv('PATH').split(os.pathsep)
        found_paths = []

        for path in paths:
            full_path = os.path.join(path, binary_name)

            if os.path.isfile(full_path) and os.access(full_path, os.X_OK):
                found_paths.append(full_path)

        return found_paths

    @classmethod
    def _is_adb_available(cls) -> bool:
        """
        Checks if the adb is available.
        :return: True if the adb is available, False otherwise.
        """
        return len(cls._discover_from_path(cls.BINARY_NAME)) > 0
