import os
import shutil
import tempfile
from pathlib import Path
from unittest import TestCase

from fcache import FileCache


class TestFileCache(TestCase):
    def setUp(self):
        self.cache_dir = tempfile.mkdtemp()
        self.ttl = 10

    def tearDown(self):
        shutil.rmtree(self.cache_dir)

    def test_file_within_ttl(self):
        cache = FileCache(self.cache_dir, self.ttl)
        temp_file = tempfile.NamedTemporaryFile(
            dir=self.cache_dir, delete=False
        )
        temp_file_path = temp_file.name
        temp_file.close()

        cached_path = cache.cache_file(temp_file_path)
        self.assertIsNotNone(cached_path)
        self.assertTrue(Path(temp_file_path).exists())

    def test_file_beyond_ttl(self):
        cache = FileCache(self.cache_dir, self.ttl)
        temp_file = tempfile.NamedTemporaryFile(
            dir=self.cache_dir, delete=False
        )
        temp_file_path = temp_file.name
        temp_file.close()

        old_mtime = os.path.getmtime(temp_file_path) - (self.ttl + 1)
        os.utime(temp_file_path, (old_mtime, old_mtime))

        cached_path = cache.cache_file(temp_file_path)
        self.assertIsNotNone(cached_path)
        self.assertTrue(Path(temp_file_path).exists())
        self.assertGreater(os.path.getmtime(temp_file_path), old_mtime)

    def test_nonexistent_source_file(self):
        cache = FileCache(self.cache_dir, self.ttl)
        with self.assertRaises(FileNotFoundError):
            cache.cache_file("/path/to/nonexistent/file")
