import csv
import logging
from core.base_repository import BaseRepository

class ProductRateRepository(BaseRepository):
    def __init__(self, file_name: str | None = None, delimiter: str = ',') -> None:
        super().__init__()
        self.file_name = file_name or "scenarios.csv"
        self._delimiter = delimiter

    def _parse_rate(self, val: str) -> float:
        """Centraliza o parseamento seguro de string para float com suporte a decimais com vírgula."""
        val_clean = val.strip().replace(',', '.')
        if not val_clean:
            return 0.0
        try:
            return float(val_clean)
        except ValueError:
            return 0.0

    def _calculate_total_upm(self, top_hours_per_1k: float, bot_hours_per_1k: float) -> float:
        """
        CORREÇÃO FÍSICA: Soma os tempos (horas) de TOP e BOT primeiro.
        Depois converte o tempo total para UPM (Unidades Por Minuto).
        """
        total_hours = top_hours_per_1k + bot_hours_per_1k
        
        if total_hours <= 0:
            return 0.0
            
        # Fórmula: 1000 peças / (Total de Horas * 60 minutos) = Peças por minuto
        return 1000.0 / (total_hours * 60.0)

    def get_all_rates(self) -> dict[int, dict[int, float]]:
        all_rates: dict[int, dict[int, float]] = {}
        file_path = self.db_local_path / self.file_name
        
        try:
            with open(file_path, mode='r', encoding='utf-8') as file:
                reader = csv.reader(file, delimiter=self._delimiter)
                headers = next(reader, None)
                
                if not headers:
                    logging.warning(f"[product_rate_repository] O arquivo '{self.file_name}' está vazio ou sem cabeçalho.")
                    return all_rates
                
                for row in reader:
                    if not row or not row[0].strip().isdigit():
                        continue
                        
                    id_val = int(row[0].strip())
                    
                    top_1 = self._parse_rate(row[1]) if len(row) > 1 else 0.0
                    bot_1 = self._parse_rate(row[2]) if len(row) > 2 else 0.0
                    top_2 = self._parse_rate(row[3]) if len(row) > 3 else 0.0
                    bot_2 = self._parse_rate(row[4]) if len(row) > 4 else 0.0
                    top_3 = self._parse_rate(row[5]) if len(row) > 5 else 0.0
                    bot_3 = self._parse_rate(row[6]) if len(row) > 6 else 0.0

                    rates_sum = {
                        1: self._calculate_total_upm(top_1, bot_1),
                        2: self._calculate_total_upm(top_2, bot_2),
                        3: self._calculate_total_upm(top_3, bot_3)
                    }
                    
                    valid_rates = {k: v for k, v in rates_sum.items() if v > 0}
                    if valid_rates:
                        all_rates[id_val] = valid_rates
                        
        except FileNotFoundError:
            logging.error(f"[product_rate_repository] Arquivo não encontrado: {file_path}")

        logging.info(f"[product_rate_repository] Carregados rates para {len(all_rates)} produtos (get_all_rates).")
        return all_rates
    
    def get_all_rates_full(self, num_lines: int = 3) -> dict[int, dict[int, float]]:
        """
        Relaxamento de Restrições e Escalonamento para Testes.
        """
        if num_lines < 1:
            raise ValueError("O argumento 'num_lines' deve ser maior que zero.")

        all_rates: dict[int, dict[int, float]] = {}
        file_path = self.db_local_path / self.file_name
        
        try:
            with open(file_path, mode='r', encoding='utf-8') as file:
                reader = csv.reader(file, delimiter=self._delimiter)
                headers = next(reader, None)
                
                if not headers:
                    logging.warning(f"[product_rate_repository] O arquivo '{self.file_name}' está vazio ou sem cabeçalho.")
                    return all_rates

                for row in reader:
                    if not row or not row[0].strip().isdigit():
                        continue
                    
                    id_val = int(row[0].strip())
                
                    top_1 = self._parse_rate(row[1]) if len(row) > 1 else 0.0
                    bot_1 = self._parse_rate(row[2]) if len(row) > 2 else 0.0
                    top_2 = self._parse_rate(row[3]) if len(row) > 3 else 0.0
                    bot_2 = self._parse_rate(row[4]) if len(row) > 4 else 0.0
                    top_3 = self._parse_rate(row[5]) if len(row) > 5 else 0.0
                    bot_3 = self._parse_rate(row[6]) if len(row) > 6 else 0.0

                    taxas_fisicas = {
                        1: self._calculate_total_upm(top_1, bot_1),
                        2: self._calculate_total_upm(top_2, bot_2),
                        3: self._calculate_total_upm(top_3, bot_3)
                    }

                    taxas_validas = [r for r in taxas_fisicas.values() if r > 0]
                    
                    if not taxas_validas:
                        continue

                    # Assumimos a MAIOR taxa (UPM mais rápido) como referência para as linhas ausentes
                    taxa_ref = max(taxas_validas) 

                    machine_rates = {}
                    for line_id in range(1, num_lines + 1):
                        real_rate = taxas_fisicas.get(line_id, 0.0)
                        machine_rates[line_id] = real_rate if real_rate > 0 else taxa_ref
                    
                    all_rates[id_val] = machine_rates
                        
        except FileNotFoundError:
            logging.error(f"[product_rate_repository] Arquivo não encontrado: {file_path}")

        logging.info(f"[product_rate_repository] Carregados rates FULL para {len(all_rates)} produtos escalados em {num_lines} linhas.")
        return all_rates