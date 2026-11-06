import csv
import logging
from core.base_repository import BaseRepository
from entities.historical_balancing import HistoricalBalancing

class HistoricalBalancingRepository(BaseRepository):
    def __init__(self, delimiter: str = ',') -> None:
        super().__init__()
        self.repos = self.db_local_path / "manual_balancing"
        self.repos.mkdir(parents=True, exist_ok=True)
        self._delimiter = delimiter

    def get_in_path(self, path: str = "manual_balancing.csv") -> HistoricalBalancing | None:
        file_path = self.repos / path
        
        if not file_path.exists():
            logging.error(f"[historical_balancing] O arquivo '{path}' não foi encontrado em {file_path}.")
            return None
                
        count = 0
        duplicate = 0
        
        # Nova tipagem exigida pela sua dataclass: lista de tuplas (product_id, quantity)
        line_allocations: dict[int, list[tuple[int, int]]] = {}
        line_ids: list[int] = []
        
        # Rastreador de sequência para o lado TOP/BOT
        last_product_id = None 

        try:
            with open(file_path, mode='r', encoding='utf-8') as file:
                reader = csv.reader(file, delimiter=self._delimiter)
                
                headers = next(reader, None)
                if not headers:
                    logging.error(f"[historical_balancing] O arquivo '{path}' está vazio ou sem cabeçalho.")
                    return None

                for linha_num, row in enumerate(reader, start=2):
                    if not row or len(row) < 3:
                        continue

                    prod_str = row[0].strip()
                    qty_str = row[1].strip()
                    line_str = row[2].strip()

                    if not (prod_str.isdigit() and qty_str.isdigit() and line_str.isdigit()):
                        logging.warning(f"[historical_balancing] Dados inválidos na linha {linha_num} de '{path}'. Ignorando.")
                        continue

                    product_id = int(prod_str)
                    quantity = int(qty_str)
                    line_id = int(line_str)

                    if line_id not in line_allocations:
                        logging.info(f"[historical_balancing] Mapeando nova linha: {line_id} em '{path}'.")
                        line_allocations[line_id] = []
                        line_ids.append(line_id)

                    # REGRA: Ignora a SEGUNDA aparição consecutiva (Lado BOT do mesmo lote)
                    if product_id == last_product_id:
                        logging.debug(f"[historical_balancing] Ignorando lado BOT do lote atual (Produto {product_id}).")
                        duplicate += 1
                        
                        # Reseta o rastreador. Se a PRÓXIMA linha for o mesmo produto de novo, 
                        # saberemos que é um NOVO LOTE (nova ordem de produção) iniciando seu lado TOP.
                        last_product_id = None 
                        continue

                    # É um lote novo (Lado TOP ou produto de lado único)
                    last_product_id = product_id
                    
                    # Salva a tupla (ID, Quantidade) diretamente na linha
                    line_allocations[line_id].append((product_id, quantity))
                    count += 1
                    
        except Exception as e:
            logging.error(f"[historical_balancing] Falha crítica ao processar '{path}': {e}", exc_info=True)
            return None

        logging.info(f"[historical_balancing] Criados {count} Lotes/OPs reais. Lados BOT ignorados: {duplicate}.")
        
        # Retorna o objeto exatamente com a assinatura da sua dataclass refatorada
        return HistoricalBalancing(
            id=0,
            name=path,
            line_ids=line_ids,
            line_allocations=line_allocations
        )