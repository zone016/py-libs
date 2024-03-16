class FridaIsNotRunning(Exception):
    def __init__(self, device_name: str) -> None:
        super().__init__(
            f'frida-server appears to be not running at {device_name}.'
        )
