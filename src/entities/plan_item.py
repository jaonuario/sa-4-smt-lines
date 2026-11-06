from dataclasses import dataclass

@dataclass(frozen=True)
class PlanItem:
    plan_id: int
    product_id: int
    quantity: int
    priority: int

    def __post_init__(self) -> None:
        if self.quantity <= 0:
            raise ValueError(f"A quantidade do plano {self.plan_id} deve ser maior que zero.")
        
    def __repr__(self) -> str:
        return f"PlanItem(plan_id={self.plan_id}, product_id={self.product_id}, quantity={self.quantity}, priority={self.priority})"
