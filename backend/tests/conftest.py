"""Shared pytest fixtures and test environment defaults.

Sets safe dummy env vars so importing app modules never requires real credentials
or a live database during unit tests.
"""

import os

os.environ.setdefault("APP_ENV", "development")
os.environ.setdefault(
    "DATABASE_URL", "postgresql+asyncpg://test:test@localhost:5432/test_db"
)
os.environ.setdefault("REDIS_URL", "redis://localhost:6379/0")
os.environ.setdefault("OPENAI_API_KEY", "sk-test-dummy")
os.environ.setdefault("VECTOR_BACKEND", "qdrant")
