import csv
import logging
from core.base_repository import BaseRepository
from entities.plan_item import PlanItem


class ProductionPlanRepository(BaseRepository):
    def __init__(self, delimiter: str = ',') -> None:
        super().__init__()
        self._delimiter = delimiter

    def get(self, file_name: str) -> list[PlanItem]:
        plan_items: list[PlanItem] = []
        file_path = self.db_local_path / file_name
        
        try:
            with open(file_path, mode='r', encoding='utf-8') as file:
                reader = csv.DictReader(file, delimiter=self._delimiter)
                
                for linha_num, row in enumerate(reader, start=2):
                    plan_id_str = row.get('plan_id', row.get('id do plano', '')).strip()
                    product_id_str = row.get('product_id', row.get('id do produto', '')).strip()
                    
                    if not plan_id_str.isdigit() or not product_id_str.isdigit():
                        continue
                        
                    quantity_str = row.get('quantity', row.get('quantidade', '0')).strip()
                    priority_str = row.get('priority', row.get('prioridade', '0')).strip()
                    
                    try:
                        plan_item = PlanItem(
                            plan_id=int(plan_id_str),
                            product_id=int(product_id_str),
                            quantity=int(quantity_str) if quantity_str else 0,
                            priority=int(priority_str) if priority_str else 0
                        )
                        plan_items.append(plan_item)
                    except ValueError as e:
                        logging.error(f"[production_plan] Erro de valor na linha {linha_num} do arquivo '{file_name}': {e}. Linha ignorada.")
                        continue
                        
        except FileNotFoundError:
            logging.error(f"[production_plan] O arquivo CSV '{file_name}' não foi encontrado no caminho '{file_path}'.")

        logging.info(f"[production_plan] Total de PlanItems carregados de '{file_name}': {len(plan_items)}")
        return plan_items
