from unittest import TestCase
from unittest.mock import MagicMock, patch

from py_adb import Adb
from py_adb.exceptions import AdbHaveMultipleMatches, AdbIsNotAvailable


class TestAdb(TestCase):
    @patch('py_adb.Adb._is_adb_available')
    def test_instance_creation_without_adb(
        self, mock_is_adb_available: MagicMock
    ) -> None:
        mock_is_adb_available.return_value = False

        with self.assertRaises(AdbIsNotAvailable):
            _ = Adb()

    @patch('py_adb.Adb._discover_from_path')
    @patch('py_adb.Adb._is_adb_available')
    def test_instance_creation_with_multiple_entries(
        self,
        mock_is_adb_available: MagicMock,
        mock_discover_from_path: MagicMock,
    ) -> None:
        mock_is_adb_available.return_value = True
        mock_discover_from_path.return_value = ['1', '2']

        with self.assertRaises(AdbHaveMultipleMatches):
            _ = Adb()

    @patch('py_adb.Adb._discover_from_path')
    @patch('py_adb.Adb._is_adb_available')
    def test_instance_creation_with_adb(
        self,
        mock_is_adb_available: MagicMock,
        mock_discover_from_path: MagicMock,
    ) -> None:
        mock_is_adb_available.return_value = True
        mock_discover_from_path.return_value = ['1']

        _ = Adb()
