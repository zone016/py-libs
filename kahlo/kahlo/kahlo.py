import frida
from frida.core import Device
from py_adb import Adb

from .exceptions import DeviceDoesNotExists, DeviceIsNotConnceted


class Kahlo:
    def __init__(self, device_name: str):
        """
        Initialize the Kahlo wrapper with a specific _device.

        :param device_name: The identifier of the _device to be used.
        """
        self.device_name: str = device_name
        self._sessions = set()
        self._device: Device | None = None
        self._is_connected: bool = False

    def is_frida_server_running(self) -> bool:
        if not self._is_connected:
            raise DeviceIsNotConnceted

        return False

    def connect(self):
        self._enforce_device_availability()
        self._device = frida.get_device(self.device_name)

    def is_device_available(self) -> bool:
        devices = Adb().list_devices()
        return self.device_name in devices

    def _enforce_device_availability(self) -> None:
        if self.is_device_available():
            return

        raise DeviceDoesNotExists
