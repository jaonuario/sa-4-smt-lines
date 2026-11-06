class BaseAppError(Exception):
    message: str

    def __init__(self, message: str | None = None) -> None:
        self.message = message or self.message
        super().__init__(self.message)
