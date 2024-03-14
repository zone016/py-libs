import unittest
from unittest import TestCase

from py_adb import Adb

from kahlo import Kahlo


@unittest.skipUnless(
    (Adb._is_adb_available() and len(Adb().list_devices()) >= 1),
    'Only run if adb is in available and Whatsapp is installed.',
)
class TestIntegratedKahlo(TestCase):
    def test_validations(self):
        device = Adb().list_devices()[0]
        kahlo = Kahlo(device)

        self.assertTrue(kahlo.is_device_available())

    @unittest.skipUnless(
        Kahlo(Adb().list_devices()[0]).is_device_rooted(),
        'Device is not rooted',
    )
    def test_frida_installation(self):
        pass
