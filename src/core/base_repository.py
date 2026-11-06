import os
import logging
from pathlib import Path

class BaseRepository:
    def __init__(self, db_path: Path | str | None = None) -> None:
        """
        Inicializa o repositório base com resolução inteligente de caminhos.
        """
        self.db_local_path = self._resolve_db_path(db_path)
        self._ensure_directory_exists()

    def _resolve_db_path(self, provided_path: Path | str | None) -> Path:
        if provided_path:
            return Path(provided_path)
            
        env_path = os.getenv("SMT_DB_PATH")
        if env_path:
            return Path(env_path)
            
        fallback_path = Path(__file__).resolve().parent.parent.parent / "database"
        return fallback_path

    def _ensure_directory_exists(self) -> None:
        """Garante que a pasta física exista, prevenindo erros ao escrever arquivos."""
        if not self.db_local_path.exists():
            logging.warning(f"[BaseRepository] Diretório de banco de dados não encontrado. Criando em: {self.db_local_path}")
            self.db_local_path.mkdir(parents=True, exist_ok=True)