import csv
import logging
from core.base_repository import BaseRepository
from entities.product_setup import ProductSetup

class ProductSetupRepository(BaseRepository):
    def __init__(self, file_name: str | None = None, delimiter: str = ',') -> None:
        super().__init__()
        self.file_name = file_name or "smd-subassemblies.csv"
        self._delimiter = delimiter

    def get_all(self) -> dict[int, ProductSetup]:
        setups: dict[int, ProductSetup] = {}
        file_path = self.db_local_path / self.file_name
        
        try:
            with open(file_path, mode='r', encoding='utf-8') as file:
                reader = csv.reader(file, delimiter=self._delimiter)
                headers = next(reader, None)
                if not headers:
                    logging.warning(f"[product_setup] O arquivo CSV '{self.file_name}' está vazio ou não possui cabeçalho.")
                    return setups

                for linha_num, row in enumerate(reader, start=2): 
                    if not row:
                        continue                    
                    try:
                        id_val = int(row[0].strip())
                        
                        width_str = row[5].strip()
                        painel_str = row[6].strip()
                        
                        setups[id_val] = ProductSetup(
                            product_id=id_val,
                            paste=row[2].strip() or None,
                            oven_profile=row[3].strip() or None,
                            width=float(width_str.replace(',', '.')) if width_str else None,
                            painel=int(painel_str) if painel_str else None
                        )
                    except (IndexError, ValueError) as e:
                        logging.error(f"[product_setup] Erro ao processar linha {linha_num} do arquivo '{self.file_name}': {e}. Linha ignorada.")
                        continue
                        
        except FileNotFoundError:
            logging.error(f"[product_setup] O arquivo '{file_path}' não foi encontrado.")
            
        logging.info(f"[product_setup] Total de ProductSetups carregados: {len(setups)}")
        return setups
