import os
from typing import List

from .exceptions import AdbHaveMultipleMatches, AdbIsNotAvailable


class Adb:
    BINARY_NAME = 'adb.exe' if os.name == 'nt' else 'adb'

    def __init__(self):
        if not self.is_adb_available():
            raise AdbIsNotAvailable()

        binaries = self.discover_from_path(self.BINARY_NAME)
        if len(binaries) > 1:
            raise AdbHaveMultipleMatches()

    @classmethod
    def discover_from_path(cls, binary_name: str) -> List[str]:
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
    def is_adb_available(cls) -> bool:
        """
        Checks if the adb is available.
        :return: True if the adb is available, False otherwise.
        """
        return len(cls.discover_from_path(cls.BINARY_NAME)) > 0
