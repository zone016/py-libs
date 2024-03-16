import os
import shutil
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
        devices = adb.get_devices()
        print(devices)

    def test_device_app_search_and_get_path_dynamic(self):
        adb = Adb()
        devices = adb.get_devices()

        if len(devices) == 0:
            return

        device = devices[0]
        packages = adb.search_package(device, 'a')
        self.assertTrue(len(packages) > 1)
        package = packages[0]
        print(f'Package: {package}')

        artifacts = adb.get_package_artifacts(device, package)
        print(f'Artifact(s): {artifacts}')
        self.assertTrue(len(artifacts) >= 1)

    def test_device_app_listing_dynamic(self):
        adb = Adb()
        devices = adb.get_devices()

        if len(devices) == 0:
            return

        device = devices[0]
        apps = adb.get_apps(device)
        print(apps)

    def test_device_file_push_and_pull_dynamic(self):
        adb = Adb()
        devices = adb.get_devices()

        if len(devices) == 0:
            return

        device = devices[0]
        with tempfile.NamedTemporaryFile(delete=False) as temp:
            origin_path = temp.name

        file_name = Path(origin_path).name

        destination_path = f'/data/local/tmp/{file_name}'
        adb.push(device, origin_path, destination_path)
        adb.pull(device, destination_path, file_name)

        self.assertTrue(Path(file_name).is_file())

        os.remove(origin_path)
        os.remove(file_name)


class TestAppManagement(TestCase):
    @unittest.skipUnless(
        (
                Adb._is_adb_available()
                and len(Adb().get_devices()) > 1
                and len(Adb().search_package(Adb().get_devices()[0], 'whatsapp'))
                >= 1
        ),
        'Only run if adb is in fact available and WhatsApp is installed.',
    )
    def test_uninstall_and_install_whatsapp(self):
        adb = Adb()
        device = adb.get_devices()[0]

        apps = adb.search_package(device, 'whatsapp')
        self.assertTrue(len(apps) == 1)

        whatsapp = apps[0]
        whatsapp_artifacts = adb.get_package_artifacts(device, whatsapp)
        self.assertTrue(len(whatsapp_artifacts) > 0)

        output = tempfile.mkdtemp()
        for artifact in whatsapp_artifacts:
            artifact_path = Path(output) / Path(artifact).name
            adb.pull(device, artifact, str(artifact_path))

        is_uninstalled = adb.uninstall_package(device, whatsapp)
        self.assertTrue(is_uninstalled)

        apps = adb.search_package(device, 'whatsapp')
        self.assertTrue(len(apps) == 0)

        if len(whatsapp_artifacts) == 1:
            pacakge = Path(output) / Path(whatsapp_artifacts[0]).name
            is_installed = adb.install_package(device, str(pacakge))

            self.assertTrue(is_installed)
        else:
            packages = []
            for artifact in whatsapp_artifacts:
                package = Path(output) / Path(artifact).name
                packages.append(str(package))

            is_installed = adb.install_split_package(device, packages)
            self.assertTrue(is_installed)

        apps = adb.search_package(device, 'whatsapp')
        self.assertTrue(len(apps) == 1)

        shutil.rmtree(output)

    def test_pidof(self):
        adb = Adb()
        device = adb.get_devices()[0]

        pids = adb.pgrep(device, 'a')
        self.assertTrue(len(pids) > 1)

    @unittest.skipUnless(
        (
                Adb._is_adb_available()
                and len(Adb().get_devices()) > 0
                and len(Adb().search_package(Adb().get_devices()[0], 'chrome'))
                == 1
                and Adb().file_exists(Adb().get_devices()[0], '/system/xbin/su')
        ),
        'Only run if adb is in fact available and Chrome is installed.',
    )
    def test_spawn_and_kill(self):
        adb = Adb()
        device = adb.get_devices()[0]

        chrome_pid = adb.pidof(device, 'com.android.chrome')
        if chrome_pid != 0:
            is_chrome_killed = adb.kill(device, chrome_pid, True)
            self.assertTrue(is_chrome_killed)

        chrome_pid = adb.spawn(device, 'com.android.chrome')
        self.assertFalse(0, chrome_pid)
        is_chrome_killed = adb.kill(device, chrome_pid, True)
        self.assertTrue(is_chrome_killed)

    @unittest.skipUnless(
        Adb().file_exists(Adb().get_devices()[0], '/system/xbin/su'),
        'Emulator does not have su executable',
    )
    def test_root_detection(self):
        adb = Adb()
        device = adb.get_devices()[0]
        self.assertTrue(adb.is_rooted(device))
