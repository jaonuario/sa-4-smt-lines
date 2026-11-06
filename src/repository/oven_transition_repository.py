import csv
import logging
from core.base_repository import BaseRepository

class OvenTransitionRepository(BaseRepository):
    def __init__(self, file_name: str | None = None, delimiter: str = ',') -> None:
        super().__init__()
        self.file_name = file_name or "oven_transitions.csv"
        self._delimiter = delimiter
    
    def get_all(self) -> dict[str, dict[str, float]]:
        csv_matrix: dict[str, dict[str, float]] = {}
        file_path = self.db_local_path / self.file_name
        count = 0
        
        try:
            with open(file_path, mode='r', encoding='utf-8') as file:
                reader = csv.reader(file, delimiter=self._delimiter)
                
                headers = next(reader, None)
                if not headers:
                    logging.warning(f"[oven_transition] O arquivo CSV '{self.file_name}' está vazio ou não possui cabeçalho. Nenhuma transição será carregada.")
                    return csv_matrix
                
                codes = [h.strip() for h in headers[1:]]
                csv_matrix = {code: {} for code in codes}
                
                for linha_num, row in enumerate(reader, start=2):
                    if not row:
                        continue
                        
                    from_code = row[0].strip()
                    if from_code not in csv_matrix:
                        csv_matrix[from_code] = {}
                        
                    times = row[1:]                    
                    for i, cost_str in enumerate(times):
                        if i >= len(codes):
                            break
                            
                        to_code = codes[i]
                        if from_code == to_code:
                            continue
                            
                        cost_clean = cost_str.strip()
                        if not cost_clean:
                            continue  # Célula vazia, ignora e segue para a próxima
                            
                        try:
                            cost_val = float(cost_clean.replace(',', '.'))
                            csv_matrix[from_code][to_code] = cost_val
                            count += 1
                        except ValueError:
                            logging.error(f"[oven_transition] Valor inválido '{cost_clean}' na linha {linha_num}, coluna '{to_code}'. Transição ignorada.")
                            
        except FileNotFoundError:
            logging.error(f"[oven_transition] O arquivo '{file_path}' não foi encontrado.")

        logging.info(f"[oven_transition] Total de transições de forno carregadas: {count}")
        return csv_matrix