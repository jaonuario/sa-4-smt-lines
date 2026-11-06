from dataclasses import dataclass

@dataclass(frozen=True)
class ProductSetup:
    product_id: int
    paste: str
    painel: str  
    oven_profile: str
    width: float

    def __post_init__(self) -> None:
        if None in (self.product_id, self.paste, self.painel, self.oven_profile, self.width):
            raise ValueError(f"Setup do produto {self.product_id} possui campos nulos.")

        if not self.paste.strip() or not self.oven_profile.strip():
            raise ValueError(f"Setup do produto {self.product_id} possui textos em branco.")
            
        if self.width <= 0:
            raise ValueError(f"A largura do produto {self.product_id} deve ser maior que zero.")
        
    def __repr__(self) -> str:
        return (
            f"ProductSetup( product_id: {self.product_id:<8} | "
            f"paste: {self.paste:<8} | "
            f"panel: {self.painel:<10} | "
            f"profile_code: {self.oven_profile:<20} | "
            f"width: {self.width:<5} )\n"
        )