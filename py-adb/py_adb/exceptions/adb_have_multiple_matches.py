class AdbHaveMultipleMatches(Exception):
    def __init__(self) -> None:
        super().__init__("ADB have multiple matches from your $PATH.")
