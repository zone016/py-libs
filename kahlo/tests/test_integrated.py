import unittest
from unittest import TestCase

from py_adb import Adb

from kahlo import Kahlo


@unittest.skipIf(
    (
        not Adb._is_adb_available()
        and len(Adb().list_devices()) >= 1
    ),
    'Only run if adb is in available alongside a device and Whatsapp is installed.',
)
class TestIntegratedKahlo(TestCase):
    def test_validations(self):
        device = Adb().list_devices()[0]
        kahlo = Kahlo(device)

        self.assertTrue(kahlo.is_device_available())
