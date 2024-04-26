class AdbIsNotAvailable(Exception):
    def __init__(self) -> None:
        super().__init__("ADB is not available on the system.")
