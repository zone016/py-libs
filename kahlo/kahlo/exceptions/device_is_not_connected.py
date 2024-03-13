class DeviceIsNotConnceted(Exception):
    def __init__(self) -> None:
        super().__init__(
            'Kahlo is not connceted to the device. Call connect().'
        )
