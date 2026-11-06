import logging
import time
from repository.historical_balancing_repository import HistoricalBalancingRepository
from tools.loader import ScenarioBuilder, HISTORICAL_FULL
from tools.state_metrics import StateMetrics

logging.basicConfig(level=logging.INFO, format='%(message)s')

def validate_historical_energy(filename: str = 'wk16.csv'):
    print(f"\n" + "="*60)
    print(f" 🚀 INICIANDO VALIDAÇÃO DO ARQUIVO: {filename}")
    print("="*60)
    
    start_time = time.time()
    
    try:
        repo = HistoricalBalancingRepository()
        historical_data = repo.get_in_path(filename)
        
        builder = ScenarioBuilder(full=HISTORICAL_FULL)
        estado_historico, _ = builder.load_historical(historical_data)
        
        metrics = StateMetrics(estado_historico)
        
        exec_time = time.time() - start_time
        
        print(f"\n 📊 KPIs DO PLANEJAMENTO HISTÓRICO (HUMANO)")
        print("-" * 60)
        print(f" ⚡ Energia Total (Baseline)      : {metrics.total_energy:.2f}")
        print(f" ⏱️ Makespan Máximo (Fim do Turno) : {metrics.max_makespan:.2f} minutos")
        print(f" ⚖️ Desbalanceamento da Carga (σ)  : {metrics.load_imbalance:.2f}")
        print(f" 🔧 Custo Gasto c/ Setup (Trocas)  : {metrics.total_setup_cost:.2f} minutos")
        print(f" ❌ Penalidade de Não Alocados     : {metrics.unallocated_penalty:.2f}")
        print("-" * 60)
        
        print("\n[DIAGNÓSTICO PARA O TCC]")
        if metrics.unallocated_penalty > 0:
            print("⚠️ AVISO: O planejamento humano falhou em alocar todos os produtos corretamente")
            print("   (ou alocou produtos em linhas incompatíveis). Isso gerou penalidade.")
        else:
            print("✅ O planejamento humano alocou todas as ordens em linhas válidas.")
            
        print(f"⏱️ Tempo de processamento da validação: {exec_time:.4f} segundos")
        print(f"\n🎯 OBJETIVO DO ALGORITMO:")
        print(f"A sua Têmpera Simulada tem a missão de rodar e achar um estado final")
        print(f"com Energia estritamente MENOR que {metrics.total_energy:.2f}!\n")

    except Exception as e:
        logging.exception(f"Erro crítico durante a validação: {e}")

if __name__ == "__main__":
    validate_historical_energy('wk16.csv')
