class DeviceDoesNotExists(Exception):
    def __init__(self) -> None:
        super().__init__('Unable to connect to the _device.')
