from unittest import TestCase

from py_adb import Adb
from py_adb.exceptions import AdbIsNotAvailable


class TestAdb(TestCase):
    def test_instance_creation(self):
        with self.assertRaises(AdbIsNotAvailable):
            _ = Adb()
