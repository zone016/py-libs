import os
import subprocess
from pathlib import Path
from typing import List

from commons import CommandResult

from .exceptions import (
    AdbHaveMultipleMatches,
    AdbIsNotAvailable,
    FileTransferError,
)


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

    def uninstall_app(self, device: str, package: str) -> bool:
        """
        Uninstalls an app from the specified Android device.

        :param device: The ID or serial number of the device.
        :param package: The package name of the app to uninstall.
        :return: True if the app was successfully uninstalled, False otherwise.
        """
        command = ['-s', device, 'uninstall', package]
        result = self._run_command(command)

        return result.exit_code == 0

    def install_split_app(self, device: str, packages: List[str]) -> bool:
        """
        Installs split APKs on a specified device.

        Installs multiple APKs as a single app on the device. Raises a
        FileNotFoundError if any APK file is missing.

        :param device: Device ID or serial number.
        :param packages: List of paths to the APK files.
        :return: True if installation succeeds, False otherwise.
        :raises FileNotFoundError: If an APK file is not found.
        """
        for package in packages:
            if not Path(package).is_file():
                raise FileNotFoundError(package)

        command = ['-s', device, 'install-multiple', '-r'] + packages
        result = self._run_command(command)

        return result.exit_code == 0

    def install_app(self, device: str, package: str) -> bool:
        """
        Installs a single APK on the specified Android device.

        Attempts to install an APK file on a device. If the package file does
        not exist, a FileNotFoundError is raised.

        :param device: The ID or serial number of the target device.
        :param package: The file path to the APK to be installed.
        :return: True if the APK was successfully installed, False otherwise.
        :raises FileNotFoundError: If the APK file cannot be found.
        """
        if not Path(package).is_file():
            raise FileNotFoundError(package)

        command = ['-s', device, 'install', package]
        result = self._run_command(command)

        return result.exit_code == 0

    def get_application_artifacts(
        self, device: str, package_name: str
    ) -> List[str] | None:
        """
        Retrieves the application artifacts of a specified package on the
        designated device.

        :param device: The identifier for the Android device on which the
            search is performed.
        :param package_name: The name of the package for which to retrieve
            the application artifacts.

        :return: A list of application artifacts associated with the package,
            or None if the command fails or no artifacts are found.
        """
        command = ['shell', 'pm', 'path', package_name]
        result = self._run_command(['-s', device] + command)

        if result.exit_code != 0 or not result.stdout:
            return None

        artifacts = []
        for line in result.stdout:
            if not line:
                continue
            artifacts.append(line.replace('package:', ''))

        return artifacts

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

    def search_package(self, device: str, pattern: str) -> List[str]:
        """
        Searches for a specific package on the designated device.

        Executes the 'adb' command to search for a specified package on the
        given device. The list of packages will exactly match the provided
        package name.

        :param device: The identifier for the Android device
        (typically its serial number) on which the search is performed.
        :param pattern: The name of the package to search for on
        the device.

        :return: A list of package names on the device that exactly match the
        provided package name. Returns an empty list if the command fails or
        no matching package is found.
        """
        command = ['shell', 'pm', 'list', 'packages', pattern]
        result = self._run_command(['-s', device] + command)

        if result.exit_code != 0 or not result.stdout:
            return []

        packages = [
            line.replace('package:', '').strip()
            for line in result.stdout
            if line.startswith('package:')
        ]

        return packages

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

    def push_file(
        self,
        device: str,
        origin_file_path: str,
        destination_path: str,
        overwrite: bool = False,
    ) -> None:
        """
        Sends a file from the local filesystem to a specified device.

        Validates the existence of the origin file before attempting to push.
        If 'overwrite' is False and the destination file already exists on
        the device, the operation is aborted to prevent unintended file
        replacement.

        :param device: Device identifier where the file will be sent.
        :param origin_file_path: Path to the file on the local filesystem.
        :param destination_path: Target path on the device for the file.
        :param overwrite: Flag indicating whether to overwrite an existing
            file at the destination. Defaults to False.
        :raises FileNotFoundError: If the origin file does not exist on
            the local filesystem.
        :raises FileExistsError: If 'overwrite' is False and the destination
            file already exists on the device.
        :raises FileTransferError: If the file transfer fails for any reason
            not covered by the other exceptions.

        This method leverages the 'adb push' command for file transfer,
        applying additional logic to handle file existence checks and
        overwrite behavior.
        """
        if not os.path.isfile(origin_file_path):
            raise FileNotFoundError()

        if not overwrite:
            check_cmd = [
                'shell',
                'test',
                '-e',
                destination_path,
                '&&',
                'echo',
                'exists',
            ]
            result = self._run_command(['-s', device] + check_cmd)
            if result.stdout and 'exists' in result.stdout:
                raise FileExistsError()

        push_cmd = ['-s', device, 'push', origin_file_path, destination_path]
        result = self._run_command(push_cmd)
        if result.exit_code != 0:
            raise FileTransferError(origin_file_path, destination_path)

    def pull_file(
        self,
        device: str,
        remote_file_path: str,
        local_path: str,
        overwrite: bool = False,
    ) -> None:
        """
        Retrieves a file from a specified device to the local filesystem.

        Validates the existence of the remote file before attempting to pull.
        If 'overwrite' is False and the destination file already exists on
        the local filesystem, the operation is aborted to prevent unintended
        file replacement.

        :param device: Device identifier from which the file will be retrieved.
        :param remote_file_path: Path to the file on the device.
        :param local_path: Target path on the local filesystem for the file.
        :param overwrite: Flag indicating whether to overwrite an existing
            file at the destination. Defaults to False.
        :raises FileNotFoundError: If the remote file does not exist on
            the device.
        :raises FileExistsError: If 'overwrite' is False and the destination
            file already exists on the local filesystem.
        :raises FileTransferError: If the file transfer fails for any reason
            not covered by the other exceptions.

        This method leverages the 'adb pull' command for file transfer,
        applying additional logic to handle file existence checks and
        overwrite behavior.
        """
        check_cmd = [
            'shell',
            'test',
            '-e',
            remote_file_path,
            '&&',
            'echo',
            'exists',
        ]
        result = self._run_command(['-s', device] + check_cmd)
        if not result.stdout or 'exists' not in result.stdout:
            raise FileNotFoundError()

        if not overwrite and os.path.exists(local_path):
            raise FileExistsError(
                f'Local file {local_path} already exists'
                f'and overwrite is False.'
            )

        pull_cmd = ['-s', device, 'pull', remote_file_path, local_path]
        result = self._run_command(pull_cmd)
        if result.exit_code != 0:
            raise FileTransferError(remote_file_path, local_path)

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
                check=True,
            )
            stdout = result.stdout.splitlines() if result.stdout else None
            stderr = result.stderr.splitlines() if result.stderr else None
            return CommandResult(stdout, stderr, result.returncode)
        except subprocess.TimeoutExpired:
            return CommandResult(None, None, 1)
        except subprocess.CalledProcessError as e:
            stderr = e.stderr.splitlines() if e.stderr else None
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
