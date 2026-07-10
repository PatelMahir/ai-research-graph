"""Application configuration loaded from environment variables."""

from functools import lru_cache
from typing import Literal

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    app_env: Literal["development", "staging", "production"] = "development"
    log_level: str = "INFO"
    api_port: int = 8000

    # PostgreSQL
    database_url: str = (
        "postgresql+asyncpg://argraph:change-me@localhost:5432/ai_research_graph"
    )

    # Redis
    redis_url: str = "redis://localhost:6379/0"

    # Vector store
    vector_backend: Literal["qdrant", "pinecone", "weaviate"] = "qdrant"
    qdrant_url: str = "http://localhost:6333"
    qdrant_collection: str = "research_chunks"
    pinecone_api_key: str | None = None
    pinecone_index: str = "research-graph"
    weaviate_url: str | None = None

    # Embeddings / LLM — default to a local, no-API-key setup so the stack runs offline.
    # Set embedding_provider=openai / llm_provider=openai (+ openai_api_key) to opt in.
    embedding_provider: Literal["local", "openai"] = "local"
    embedding_dim: int = 384
    llm_provider: Literal["none", "openai"] = "none"
    openai_api_key: str | None = None
    embedding_model: str = "text-embedding-3-small"
    llm_model: str = "gpt-4o-mini"

    # Chunking
    chunk_size: int = 800
    chunk_overlap: int = 120


@lru_cache
def get_settings() -> Settings:
    return Settings()
