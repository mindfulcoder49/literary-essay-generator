from __future__ import annotations

import logging
from typing import Any
from logging.handlers import RotatingFileHandler
from pathlib import Path

LOG_DIR = Path(__file__).parent / "logs"
LOG_DIR.mkdir(parents=True, exist_ok=True)


def configure_logging(name: str, filename: str) -> logging.Logger:
    logger = logging.getLogger(name)
    logger.setLevel(logging.INFO)

    if logger.handlers:
        return logger

    formatter = logging.Formatter(
        "%(asctime)s %(levelname)s [%(name)s] %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )

    file_handler = RotatingFileHandler(
        LOG_DIR / filename,
        maxBytes=5 * 1024 * 1024,
        backupCount=3,
    )
    file_handler.setFormatter(formatter)

    stream_handler = logging.StreamHandler()
    stream_handler.setFormatter(formatter)

    logger.addHandler(file_handler)
    logger.addHandler(stream_handler)
    logger.propagate = False
    return logger


def log_startup_config(logger: logging.Logger, settings: Any) -> None:
    def present(val: str | None) -> str:
        return "set" if val else "missing"

    logger.info("startup env check: DATABASE_URL=%s", "set" if getattr(settings, "database_url", None) else "missing")
    logger.info("startup env check: OPENAI_API_KEY=%s", present(getattr(settings, "openai_api_key", None)))
    logger.info("startup env check: PINECONE_API_KEY=%s", present(getattr(settings, "pinecone_api_key", None)))
    logger.info(
        "startup config: pinecone_index=%s cloud=%s region=%s",
        getattr(settings, "pinecone_index", None),
        getattr(settings, "pinecone_cloud", None),
        getattr(settings, "pinecone_region", None),
    )
    logger.info(
        "startup config: models embed=%s chat=%s",
        getattr(settings, "openai_embedding_model", None),
        getattr(settings, "openai_chat_model", None),
    )
