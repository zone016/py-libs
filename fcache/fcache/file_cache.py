import time
from pathlib import Path
from shutil import copy2


class FileCache:
    """
    Implements a file caching system with time-to-live (TTL) control.
    """

    def __init__(self, root_directory: str, ttl: int) -> None:
        """
        Initialize the file cache system.
        :param root_directory: The root directory for cached files.
        :param ttl: Time-to-live for cached files in seconds.
        :raise NotADirectoryError: If the root_directory does not exist.
        """
        self.root_directory = Path(root_directory)
        if not self.root_directory.is_dir():
            raise NotADirectoryError('Root directory does not exist')
        self.ttl = ttl

    def cache_file(self, source_path: str) -> Path | None:
        """
        Ensure a file is in the cache, returning its path in the cache.

        If the file does not exist in the cache or is beyond its TTL,
        it's copied into the cache. If already in cache and within TTL,
        returns the existing path.

        :param source_path: Path to the source file to be cached.
        :return: The Path to the cached file, or None if the file
                 cannot be cached.
        :raise FileNotFoundError: If the source file does not exist.
        """
        source = Path(source_path)
        if not source.exists():
            raise FileNotFoundError('Source file does not exist')

        cache_path = self.root_directory / source.name

        if source.resolve() == cache_path.resolve():
            cache_path.touch()
            return cache_path

        if not cache_path.exists() or not self._is_file_within_ttl(cache_path):
            copy2(source, cache_path)
            cache_path.touch()  # Update file's modification time

        return cache_path

    def _is_file_within_ttl(self, file_path: Path) -> bool:
        """
        Check if a file is within its TTL.

        :param file_path: The Path to the file being checked.
        :return: True if the file is within TTL, False otherwise.
        """
        current_time = time.time()
        file_mod_time = file_path.stat().st_mtime
        return (current_time - file_mod_time) <= self.ttl
