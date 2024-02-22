import os
import tempfile
import unittest
from pathlib import Path
from unittest import TestCase

from py_adb import Adb


@unittest.skipIf(
    not Adb._is_adb_available(), 'Only run if adb is in fact available.'
)
class TestIntegratedAdb(TestCase):
    def test_device_listing_dynamic(self):
        adb = Adb()
        devices = adb.list_devices()
        print(devices)

    def test_device_app_listing_dynamic(self):
        adb = Adb()
        devices = adb.list_devices()

        if len(devices) == 0:
            return

        device = devices[0]
        apps = adb.list_installed_apps(device)
        print(apps)

    def test_device_file_push_and_pull_dynamic(self):
        adb = Adb()
        devices = adb.list_devices()

        if len(devices) == 0:
            return

        device = devices[0]
        with tempfile.NamedTemporaryFile(delete=False) as temp:
            origin_path = temp.name

        file_name = Path(origin_path).name

        destination_path = f'/data/local/tmp/{file_name}'
        adb.push_file(device, origin_path, destination_path)
        adb.pull_file(device, destination_path, file_name)

        self.assertTrue(Path(file_name).is_file())

        os.remove(origin_path)
        os.remove(file_name)
