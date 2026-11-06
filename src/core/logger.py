import logging
from pathlib import Path


def configure_logging(log_level: str = "DEBUG") -> None:
    Path("logs").mkdir(exist_ok=True)

    # Converte log_level de string para logging.LEVEL
    level = getattr(logging, log_level.upper(), logging.DEBUG)

    logger = logging.getLogger()
    logger.setLevel(level)

    formatter = logging.Formatter(
        fmt="%(asctime)s %(levelname)s %(message)s", datefmt="%Y-%m-%d %H:%M:%S"
    )

    # Handler de arquivo
    file_handler = logging.FileHandler("logs/app.log", mode="a")
    file_handler.setFormatter(formatter)
    logger.addHandler(file_handler)

    # Handler de console
    console_handler = logging.StreamHandler()
    console_handler.setFormatter(formatter)
    logger.addHandler(console_handler)
