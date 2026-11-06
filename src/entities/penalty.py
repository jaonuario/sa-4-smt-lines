from dataclasses import dataclass

@dataclass(frozen=True)
class Penalty:
    PRIORITY_PENALTY: float = 100.0
    INCOMPATIBILITY_PENALTY: float = 1_000_000_000.0
    UNDER_AVAILABILITY_PENALTY: float = 1.0
    OVER_AVAILABILITY_PENALTY: float = 10.0
    UNALLOCATED_OP_PENALTY: float = 100_000.0
    CONVEYOR_PENALTY: float = 5.0
    PANEL_PENALTY: float = 5.0
    PASTE_PENALTY: float = 5.0
    OVEN_PENALTY: float = 1.0
    TYPE_OVEN_PENALTY: float = 5.0

    def __post_init__(self) -> None:
        # Valida dinamicamente se qualquer atributo da instância é menor que 0
        if any(value < 0 for value in self.__dict__.values()):
            raise ValueError("Nenhuma penalidade pode ser negativa.")