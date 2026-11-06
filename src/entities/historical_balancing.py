from dataclasses import dataclass

@dataclass(frozen=True)
class HistoricalBalancing:
    id: int
    name: str
    line_ids: list[int]
    line_allocations: dict[int, list[tuple[int, int]]] 

    def __post_init__(self) -> None:
        if self.id is None or not self.name or not self.line_ids or not self.line_allocations:
            raise ValueError("Os campos de HistoricalBalancing não podem ser nulos ou vazios.")
        
        for line_id in self.line_ids:
            if line_id not in self.line_allocations:
                raise ValueError(f"Linha {line_id} não encontrada nas alocações históricas")
            
    def __repr__(self) -> str:
        return f"{self.name} - {self.line_ids}"