import logging
from dataclasses import dataclass, field
from typing import Dict
from exceptions.smt_invalid_data_error import (
    SMTInvalidDataError,
)


@dataclass(frozen=True)
class OP:
    plan_item_id: int
    product_id: int
    priority: int
    total_time: Dict[int, float]
    solder_paste_id: int
    painel_id: int
    width: float
    temperature_profile_code: str
    oven_transition_costs: Dict[int, float] = field(default_factory=dict)

    def __post_init__(self) -> None:
        erros = []

        # Validação do total_time
        if not self.total_time:
            erros.append(f"total_time está vazio")
        elif any(v <= 0 for v in self.total_time.values()):
            invalidos = [k for k, v in self.total_time.items() if v <= 0]
            erros.append(f"total_time contém valores <= 0 nas chaves: {invalidos}")

        # Validação do oven_transition_costs
        if not self.oven_transition_costs:
            erros.append(f"oven_transition_costs está vazio")
        elif any(v <= 0 for v in self.oven_transition_costs.values()):
            invalidos = [k for k, v in self.oven_transition_costs.items() if v <= 0]
            erros.append(f"oven_transition_costs contém valores <= 0 nas chaves: {invalidos}")

        if erros:
            raise SMTInvalidDataError(
                f"Erro na OP {self.plan_item_id}: " + "; ".join(erros)
            )
        
    def __repr__(self) -> str:
        return f"OP(plan_item_id={self.plan_item_id}, product_id={self.product_id}, priority={self.priority}, total_time={self.total_time}, temperature_profile_code={self.temperature_profile_code})"

    def get_oven_transition_cost(self, temperature_profile_code: str) -> float:
        if temperature_profile_code == self.temperature_profile_code:
            return 0.0
        try:
            return self.oven_transition_costs[temperature_profile_code]
        except KeyError:
            raise SMTInvalidDataError(
                f"[OP {self.product_id}] Falta de transição para {temperature_profile_code}"
            )


@dataclass
class LineAllocation:
    """
    Representa a alocação de uma linha de produção específica no plano.
    Esta classe encapsula o ID da linha e a sequência de OPs alocadas.
    """
    
    plan_line_id: int
    products: list["OP"] = field(default_factory=list) #type: ignore
    pinned_products: list["OP"] = field(default_factory=list) #type: ignore
    availability: float | None = 10080.0
    
    def __post_init__(self) -> None:
        if self.availability is None:
            self.availability = 10080.0
            
        elif self.availability <= 0:
            raise SMTInvalidDataError(
                f"A disponibilidade da linha {self.plan_line_id} contém um valor inválido ({self.availability})."
            )
                
    def copy(self) -> "LineAllocation":
        return LineAllocation(
            plan_line_id=self.plan_line_id,
            products=self.products[:],
            pinned_products=self.pinned_products[:], 
            availability=self.availability
        )
    
    @property
    def total_ops(self) -> int:
        """Retorna a quantidade total de ordens (dinâmicas + fixadas) nesta linha."""
        return len(self.pinned_products) + len(self.products)

    def __repr__(self) -> str:
        return f"LineAllocation(id={self.plan_line_id}, ops_count={self.total_ops})\n{chr(10).join(f'  {op}' for op in self.pinned_products)}  (Pinned)\n{chr(10).join(f'  {op}' for op in self.products)}  (Dynamic)\n"
