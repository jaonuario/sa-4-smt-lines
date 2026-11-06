import logging
import pandas as pd
from repository.historical_balancing_repository import HistoricalBalancingRepository
from tools.loader import ScenarioBuilder, HISTORICAL_FULL

logging.basicConfig(level=logging.INFO, format='%(message)s')

def validate_product_times(filename: str = 'wk16.csv'):
    print(f"\n" + "="*60)
    print(f" ⏱️ INICIANDO AUDITORIA DE TEMPOS DE PRODUÇÃO: {filename}")
    print("="*60)
    
    try:
        repo = HistoricalBalancingRepository()
        historical_data = repo.get_in_path(filename)
        
        if not historical_data:
            logging.error(f"❌ Falha: Não foi possível carregar os dados de {filename}.")
            return
        
        builder = ScenarioBuilder(full=HISTORICAL_FULL)
        estado_historico, _ = builder.load_historical(historical_data)
        
        dados_produtos = []
        tempo_total_fabrica = 0.0

        for line in estado_historico.get_allocations():
            line_id = line.plan_line_id
            todas_ops = line.pinned_products + line.products
            
            for op in todas_ops:
                tempo_producao = op.total_time.get(line_id, 0.0)
                tempo_total_fabrica += tempo_producao
                
                dados_produtos.append({
                    "ID da OP (Plan Item)": op.plan_item_id,
                    "ID do Produto": op.product_id,
                    "Linha Alocada": f"Linha {line_id}",
                    "Tempo de Produção (Minutos)": round(tempo_producao, 2),
                    "Tempo de Produção (Horas)": round(tempo_producao / 60, 2),
                    "Status": "Alocado Corretamente"
                })

        nao_alocados = estado_historico.get_non_allocations()
        if nao_alocados and nao_alocados.products:
            for op in nao_alocados.products:
                dados_produtos.append({
                    "ID da OP (Plan Item)": op.plan_item_id,
                    "ID do Produto": op.product_id,
                    "Linha Alocada": "N/A",
                    "Tempo de Produção (Minutos)": 0.0,
                    "Tempo de Produção (Horas)": 0.0,
                    "Status": "NÃO ALOCADO / INCOMPATÍVEL"
                })

        df = pd.DataFrame(dados_produtos)

        print("\n📊 RESUMO DE CARGA POR LINHA (Apenas Produção, sem Setup):")
        resumo_linhas = df.groupby("Linha Alocada")["Tempo de Produção (Horas)"].sum().reset_index()
        print(resumo_linhas.to_string(index=False))
        
        print(f"\n⏳ Tempo total líquido de produção da fábrica: {tempo_total_fabrica / 60:.2f} horas")

        csv_name = f"auditoria_tempos_{filename.split('.')[0]}.csv"
        
        df.to_csv(csv_name, index=False, sep=',', decimal=',', encoding='utf-8-sig')
        
        print(f"\n✅ Relatório analítico completo salvo como: {csv_name}")
        print("Abra este arquivo no Excel e verifique se as horas de máquina batem com a realidade da fábrica!")

    except Exception as e:
        logging.exception(f"Erro na auditoria: {e}")

if __name__ == "__main__":
    validate_product_times('wk16.csv')
