import random
from typing import List
import logging
from entities.smt_entities import OP 

def generate_synthetic_ops(original_ops: List[OP], multiplier: int) -> List[OP]:
    """
    Gera OPs sintéticas baseadas no 'DNA' (domínio de valores) da instância original.
    Mantém o realismo das matrizes assimétricas de setup para os testes de estresse.
    """
    if multiplier <= 1:
        return original_ops[:]
        
    logging.info(f"[algorithm_test] Gerando massa de dados sintética (Multiplicador: {multiplier}x)...")

    # 1. Extração do "DNA" dos dados carregados pelo basic_loader
    valid_pastes = list(set(op.solder_paste_id for op in original_ops))
    valid_panels = list(set(op.painel_id for op in original_ops))
    valid_priorities = list(set(op.priority for op in original_ops))
    valid_product_ids = list(set(op.product_id for op in original_ops))
    
    # Mapeamento do perfil de forno para seus respectivos custos de transição.
    # Isso garante que a OP sintética tenha a matriz de transição correta para o perfil sorteado.
    profile_to_transitions = {
        op.temperature_profile_code: op.oven_transition_costs 
        for op in original_ops
    }
    valid_profiles = list(profile_to_transitions.keys())

    synthetic_ops = []
    target_amount = len(original_ops) * multiplier

    # 2. Geração Randômica Controlada
    for i in range(target_amount):
        synth_profile = random.choice(valid_profiles)
        
        # 3. Simulação de Tempos de Processamento (UPH) com ruído (Jitter)
        # Escolhe uma OP base aleatória para herdar um tempo de produção realista
        base_op = random.choice(original_ops)
        synth_total_time = {}
        
        for line_id, time_val in base_op.total_time.items():
            # Adiciona uma variação aleatória de -10% a +10% no tempo para evitar clones perfeitos
            variation = random.uniform(0.9, 1.1)
            synth_total_time[line_id] = round(time_val * variation, 4)

        # 4. Instanciando a nova OP Sintética
        new_op = OP(
            plan_item_id=9000000 + i, # ID fictício bem alto para não conflitar com o banco de dados
            product_id=random.choice(valid_product_ids),
            priority=random.choice(valid_priorities),
            total_time=synth_total_time,
            solder_paste_id=random.choice(valid_pastes),
            painel_id=random.choice(valid_panels),
            temperature_profile_code=synth_profile,
            oven_transition_costs=profile_to_transitions[synth_profile]
        )
        
        synthetic_ops.append(new_op)

    logging.info(f"[algorithm_test] {len(synthetic_ops)} OPs sintéticas geradas com sucesso.")
    return synthetic_ops