import subprocess
from unittest import TestCase
from unittest.mock import MagicMock, patch

from py_adb import Adb
from py_adb.exceptions import AdbHaveMultipleMatches, AdbIsNotAvailable


class TestMockedAdb(TestCase):
    @patch("py_adb.Adb._is_adb_available")
    def test_instance_creation_without_adb(
        self, mock_is_adb_available: MagicMock
    ) -> None:
        mock_is_adb_available.return_value = False

        with self.assertRaises(AdbIsNotAvailable):
            _ = Adb()

    @patch("py_adb.Adb._discover_from_path")
    @patch("py_adb.Adb._is_adb_available")
    def test_instance_creation_with_multiple_entries(
        self,
        mock_is_adb_available: MagicMock,
        mock_discover_from_path: MagicMock,
    ) -> None:
        mock_is_adb_available.return_value = True
        mock_discover_from_path.return_value = ["1", "2"]

        with self.assertRaises(AdbHaveMultipleMatches):
            _ = Adb()

    @patch("py_adb.Adb._discover_from_path")
    @patch("py_adb.Adb._is_adb_available")
    def test_instance_creation_with_adb(
        self,
        mock_is_adb_available: MagicMock,
        mock_discover_from_path: MagicMock,
    ) -> None:
        mock_is_adb_available.return_value = True
        mock_discover_from_path.return_value = ["1"]

        _ = Adb()

    @patch("subprocess.run")
    @patch("py_adb.Adb._discover_from_path")
    @patch("py_adb.Adb._is_adb_available")
    def test_run(
        self,
        mock_is_adb_available: MagicMock,
        mock_discover_from_path: MagicMock,
        mock_run: MagicMock,
    ) -> None:
        mock_is_adb_available.return_value = True
        mock_discover_from_path.return_value = ["1"]
        mock_run.return_value = subprocess.CompletedProcess(
            args="adb devices",
            returncode=0,
            stdout="dummy stdout",
            stderr="dummy stderr",
        )

        adb = Adb()
        command_result = adb._run_command(["devices"])
        self.assertEqual(len(command_result.stderr), 1)
        self.assertEqual(len(command_result.stdout), 1)
        self.assertEqual(command_result.exit_code, 0)

    @patch("subprocess.run")
    @patch("py_adb.Adb._discover_from_path")
    @patch("py_adb.Adb._is_adb_available")
    def test_list_devices(
        self,
        mock_is_adb_available: MagicMock,
        mock_discover_from_path: MagicMock,
        mock_run: MagicMock,
    ) -> None:
        mock_is_adb_available.return_value = True
        mock_discover_from_path.return_value = ["1"]
        mock_run.return_value = subprocess.CompletedProcess(
            args="adb devices",
            returncode=0,
            stdout=(
                "List of devices attached\nemulator-5554\tdevice\n"
                "emulator-5555\tdevice\nemulator-5556\tdevice\n"
            ),
            stderr=None,
        )

        adb = Adb()
        devices = adb.get_devices()
        self.assertEqual(len(devices), 3)
        self.assertEqual(devices, ["emulator-5554", "emulator-5555", "emulator-5556"])

    @patch("subprocess.run")
    @patch("py_adb.Adb._discover_from_path")
    @patch("py_adb.Adb._is_adb_available")
    def test_list_devices_with_invalid_exit_code(
        self,
        mock_is_adb_available: MagicMock,
        mock_discover_from_path: MagicMock,
        mock_run: MagicMock,
    ) -> None:
        mock_is_adb_available.return_value = True
        mock_discover_from_path.return_value = ["1"]
        mock_run.return_value = subprocess.CompletedProcess(
            args="adb devices", returncode=0, stdout=None, stderr=None
        )

        adb = Adb()
        devices = adb.get_devices()
        self.assertEqual(len(devices), 0)
