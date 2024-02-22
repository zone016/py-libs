class FileTransferError(Exception):
    def __init__(self, from_path: str, destination_path: str):
        self.destination_path = destination_path
        self.from_path = from_path

        super().__init__(
            f'Unable to transfer file from {from_path} to {destination_path}.'
        )
