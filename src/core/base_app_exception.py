class BaseAppError(Exception):
    """Base para exceções de domínio da aplicação."""

    message: str

    def __init__(self, message: str | None = None) -> None:
        self.message = message or self.message
        super().__init__(self.message)