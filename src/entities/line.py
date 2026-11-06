from dataclasses import dataclass

@dataclass(frozen=True)
class Line:
    id: int
    name: str

    def __post_init__(self) -> None:
        if self.id is None or not self.name:
            raise ValueError("Os campos de Line não podem ser nulos ou vazios.")
