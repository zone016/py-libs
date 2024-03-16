class DeviceIsNotRooted(Exception):
    def __init__(self, device_name: str) -> None:
        super().__init__(f'Device {device_name} seems to be not rooted.')
