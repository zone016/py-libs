class FridaIsAlreadyRunning(Exception):
    def __init__(self, device_name: str) -> None:
        super().__init__(f'frida-server is already running at {device_name}.')
