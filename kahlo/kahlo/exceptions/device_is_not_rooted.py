class DeviceIsNotRooted(Exception):
    def __init__(self, device_name: str) -> None:
        super().__init__(f'Unable to connect to the device {device_name}.')
