import csv
import logging
from typing import Any

from core.simulated_annealing import Response
from algorithm.smt_state import SMTState
from entities.smt_entities import LineAllocation
    

def table_responses(results: list[tuple[dict[str, Any], Response]], save_path: str = 'responses_table.csv') -> None:
    if not results:
        logging.warning("[table_responses] A lista de resultados está vazia. Tabela não gerada.")
        return

    headers = [
        "Cenário",
        "Energia Inicial",
        "Melhor Energia",
        "Ganho Absoluto",
        "Melhoria (%)",
        "Coef. Congelamento",
        "Temp. de Parada",
        "Iterações Totais",
        "Tempo Execução (s)",
        "Velocidade (Iter/s)",
        "Linhas Ativas",
        "OPs Não Alocadas"
    ]

    try:
        with open(save_path, mode='w', newline='', encoding='utf-8-sig') as file:
            writer = csv.writer(file, delimiter=',') 
            writer.writerow(headers)

            for metadata, resp in results:
                melhoria_abs = resp.initial_energy - resp.best_energy
                melhoria_pct = (melhoria_abs / resp.initial_energy) * 100 if resp.initial_energy != 0 else 0
                iter_por_seg = resp.iterations / resp.execution_time if resp.execution_time > 0 else 0
                
                state = resp.best_state
                linhas_ativas = sum(1 for line in state.get_allocations() if line.total_ops > 0)
                
                non_alloc = state.get_non_allocations()
                ops_nao_alocadas = len(non_alloc.products) if non_alloc else 0

                writer.writerow([
                    str(metadata["name"]),
                    round(resp.initial_energy, 2),
                    round(resp.best_energy, 2),
                    round(melhoria_abs, 2),
                    f"{round(melhoria_pct, 2)}%",
                    resp.freezing_coef,
                    round(resp.temperature, 6),
                    resp.iterations,
                    round(resp.execution_time, 4),
                    round(iter_por_seg, 2),
                    linhas_ativas,
                    ops_nao_alocadas
                ])
                
        logging.info(f"[table_responses] Tabela de resultados detalhada gerada em: {save_path}")
    except Exception as e:
        logging.error(f"[table_responses] Erro ao salvar a tabela: {e}")

def smts_table(states = list[SMTState], save_path: str = 'smt_table.csv')->None:
    if not states:
        logging.warning("[states_table] A lista de estados está vazia.")
        return

    headers = [
        "id",
        "Energia",
        "alocacao 1",
        "alocacao 2",
        "alocacao 3",
        "nao alocados"
    ]
    
    def pegar_item(lista, indice, padrao=LineAllocation(plan_line_id=-1, products=[], pinned_products=[])) -> LineAllocation:
        if indice < len(lista):
            padrao = lista[indice]
        return [p.product_id for p in padrao.products]
    
    try:
        with open(save_path, mode='w', newline='', encoding='utf-8') as file:
            writer = csv.writer(file, delimiter=',')
            writer.writerow(headers)
            i = 1
            for s in states:
                writer.writerow([
                    round(i, 4),
                    round(s.energy, 4),
                    pegar_item(s.get_allocations(), 0),
                    pegar_item(s.get_allocations(), 1),
                    pegar_item(s.get_allocations(), 2),
                    s.get_non_allocations().products
                ])
                i += 1
        
        logging.info(f"[smt table] Tabela de comparação gerada em: {save_path}")
    except Exception as e:
        logging.error(f"[smt table] Erro ao salvar a tabela: {e}")
