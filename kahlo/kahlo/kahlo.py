import frida
from frida.core import Device
from py_adb import Adb

from .exceptions import (
    DeviceDoesNotExists,
    DeviceIsNotConnceted,
    DeviceIsNotRooted,
    FridaIsAlreadyRunning,
    FridaIsNotRunning
)


class Kahlo:
    def __init__(self, device_name: str):
        """
        Initialize the Kahlo wrapper with a specific device.

        :param device_name: The identifier of the device to be used.
        """
        self.device_name: str = device_name
        self._sessions = set()
        self._device: Device | None = None
        self._is_connected: bool = False
        self._adb: Adb = Adb()

    def kill_frida_server(self) -> None:
        self._enforce_dependencies()
        if not self.is_frida_server_running():
            raise FridaIsNotRunning(self.device_name)

        # TODO: Literally kill the frida-server proccess as root.

    def is_frida_server_running(self) -> bool:
        self._enforce_device_connection()

        pids = self._adb.pgrep(self.device_name, 'frida-server')
        return len(pids) >= 1

    def is_device_rooted(self) -> bool:
        self._enforce_device_availability()
        return self._adb.is_device_rooted(self.device_name)

    def connect(self) -> None:
        self._enforce_dependencies()
        self._device = frida.get_device(self.device_name)

    def is_device_available(self) -> bool:
        devices = self._adb.list_devices()
        return self.device_name in devices

    def _enforce_dependencies(self):
        self._enforce_device_availability()
        self._enforce_device_is_rooted()

    def _enforce_device_is_rooted(self) -> None:
        if self._adb.is_device_rooted(self.device_name):
            return

        raise DeviceIsNotRooted

    def _enforce_device_availability(self) -> None:
        if self.is_device_available():
            return

        raise DeviceDoesNotExists

    def _enforce_device_connection(self) -> None:
        if self._is_connected:
            return

        raise DeviceIsNotConnceted
