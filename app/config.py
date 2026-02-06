from __future__ import annotations

from functools import lru_cache
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    # App
    app_name: str = "literary-essays"
    environment: str = "dev"

    # Database
    database_url: str = "sqlite:///./literary.db"

    # Pinecone
    pinecone_api_key: str | None = None
    pinecone_index: str = "literary-essays"
    pinecone_cloud: str = "aws"
    pinecone_region: str = "us-east-1"

    # OpenAI
    openai_api_key: str | None = None
    openai_embedding_model: str = "text-embedding-3-small"
    openai_chat_model: str = "gpt-5-mini"

    # Gutenberg / Gutendex
    gutenberg_text_url: str = "https://www.gutenberg.org/ebooks/{id}.txt.utf-8"
    gutendex_url: str = "https://gutendex.com/books"

    # Admin
    admin_username: str = "admin"
    admin_password: str = ""

    # Worker
    worker_poll_seconds: int = 3
    max_segment_chars: int = 2000
    top_k_evidence: int = 8
    summary_chunk_size: int = 40
    expand_context_window: int = 3


@lru_cache

def get_settings() -> Settings:
    return Settings()
