import unittest
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
