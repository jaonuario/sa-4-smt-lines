from core.base_app_exception import BaseAppError

class SMTIncompatibleLineError(BaseAppError):
    message = "Incompatibilidade crítica: Produto não possui linhas permitidas para produção."

class SMTInvalidDataError(BaseAppError):
    message = "Dados de entrada inválidos para o cálculo de balanceamento."

class SMTTransitionError(BaseAppError):
    message = "Erro no mapeamento de transição de setup."

class OvenProfileNotMappedError(SMTTransitionError):
    message = "Perfil térmico de forno não localizado na matriz de transição."
