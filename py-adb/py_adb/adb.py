import os
import subprocess
from typing import List

from commons import CommandResult

from .exceptions import AdbHaveMultipleMatches, AdbIsNotAvailable


class Adb:
    BINARY_NAME = 'adb.exe' if os.name == 'nt' else 'adb'
    BINARY_PATH = None

    def __init__(self):
        """
        Initializes the Adb instance by locating the adb binary.

        This method checks for the adb binary's availability in
        the system's PATH. It raises exceptions if the adb binary
        is not found or if multiple instances are discovered to
        ensure clarity in which adb instance is used.

        Raises:
            AdbIsNotAvailable: If no adb binary is found in the system's PATH.
            AdbHaveMultipleMatches: If more than one adb binary is found.
        """
        if not self._is_adb_available():
            raise AdbIsNotAvailable()

        binaries = self._discover_from_path(self.BINARY_NAME)
        if len(binaries) > 1:
            raise AdbHaveMultipleMatches()

        self.BINARY_PATH = binaries[0]

    def list_devices(self) -> List[str]:
        """
        Retrieves a list of connected devices via ADB.

        Executes 'adb devices' to list devices connected to the ADB server.
        Parses the output, excluding the header and non-device lines,
        to produce a list of device identifiers.

        :return: A list of device identifiers if successful,
                 otherwise an empty list.
        """
        result = self._run_command(['devices'])
        if result.exit_code != 0 or not result.stdout:
            return []

        return [
            line.split('\t')[0]
            for line in result.stdout
            if line.strip() and "List of devices attached" not in line
        ]

    def list_installed_apps(
        self, device: str, include_system_apps: bool = False
    ) -> List[str]:
        """
        Retrieves a list of installed applications on the specified device.

        Executes the 'adb' command to list all applications installed on
        the given device. Can be configured to exclude system applications
        from the returned list.

        :param device: The identifier for the device from which to list apps.
        :param include_system_apps: If False, the list will exclude
            system apps, otherwise, it includes all apps. Defaults to False.
        :return: A list of strings where each string is the package name of an
            installed application. Returns an empty list if the command
            fails or if no apps are found.
        """
        command = ['shell', 'pm', 'list', 'packages']
        if not include_system_apps:
            command.append('-3')

        result = self._run_command(['-s', device] + command)
        if result.exit_code != 0 or not result.stdout:
            return []

        apps = [
            line.replace('package:', '').strip()
            for line in result.stdout
            if line.strip()
        ]

        return apps

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
