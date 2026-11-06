import logging
import time
import random
import sys
from concurrent.futures import ProcessPoolExecutor, as_completed
from core.base_tester import BaseTester
from core.simulated_annealing import SimulatedAnnealing

def _sa_worker(cenario_tupla):
    metadata, state, kwargs = cenario_tupla
    kwargs = dict(kwargs)
    try:
        idle_flag = kwargs.pop('idle', True)
        seed = kwargs.pop('seed', None)
        if seed is not None:
            random.seed(seed)
        sa = SimulatedAnnealing(**kwargs)
        resposta = sa.run(state, idle=idle_flag)         
        return (metadata, resposta, None)
    except Exception as e:
        error_msg = f"{type(e).__name__}: {str(e)}"
        return (metadata, None, error_msg)


class Runner:
    def __init__(self):
        self._testers: list[BaseTester] = []

    def add_tester(self, tester: BaseTester) -> None:
        self._testers.append(tester)

    def run(self) -> None:
        total_testers = len(self._testers)
        logging.info(f"=== [Runner] Iniciando bateria de {total_testers} testes ===")
        
        try:
            with ProcessPoolExecutor() as executor:
                for i, tester in enumerate(self._testers, 1):
                    logging.info(f"\n--- Preparando Teste {i}/{total_testers}: {tester.test_name} ---")
                    inicio = time.time()
                    
                    try:
                        scenarios = tester.generate_scenarios()

                        total_scenarios = len(scenarios)
                        logging.info(f"[{tester.test_name}] {total_scenarios} cenários gerados. Executando...")
                        
                        futures = {executor.submit(_sa_worker, c): c for c in scenarios}
                        
                        sucessos = []
                        erros = []

                        for future in as_completed(futures):
                            metadata, resposta, erro = future.result()                            
                            if erro is None:
                                sucessos.append((metadata, resposta))
                            else:
                                erros.append((metadata, erro))

                        if erros:
                            logging.warning(f"[{tester.test_name}] Finalizado com {len(erros)} FALHAS em {total_scenarios} cenários.")
                            for meta, err in erros[:5]:
                                logging.error(f"  -> Falha no cenário {meta}: {err}")
                        
                        if sucessos:
                            tester.process_results(sucessos)
                        else:
                            logging.error(f"[{tester.test_name}] Nenhum cenário concluído com sucesso. Nada a salvar.")
                        
                        tempo_gasto = time.time() - inicio
                        logging.info(f"--- Teste {tester.test_name} concluído em {tempo_gasto:.2f}s ---")
                        
                    except Exception as e:
                        logging.error(f"--- FALHA Crítica na orquestração do Teste {tester.test_name}: {e} ---", exc_info=True)
                        
        except KeyboardInterrupt:
            logging.warning("\n[Runner] Execução interrompida manualmente pelo usuário (Ctrl+C). Abortando...")
            sys.exit(1)
