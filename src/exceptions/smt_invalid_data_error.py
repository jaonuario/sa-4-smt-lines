from core.base_app_exception import BaseAppError

class SMTIncompatibleLineError(BaseAppError):
    """Lançada quando um produto não pode ser alocado em nenhuma linha disponível."""
    message = "Incompatibilidade crítica: Produto não possui linhas permitidas para produção."

class SMTInvalidDataError(BaseAppError):
    """Lançada quando há dados matematicamente impossíveis (ex: UPH zero)."""
    message = "Dados de entrada inválidos para o cálculo de balanceamento."

class SMTTransitionError(BaseAppError):
    """Lançada quando há uma falha no cálculo de transição entre processos."""
    message = "Erro no mapeamento de transição de setup."

class OvenProfileNotMappedError(SMTTransitionError):
    """Lançada quando um prefixo de forno (R1, R3, etc) não existe na matriz de custos."""
    message = "Perfil térmico de forno não localizado na matriz de transição."
