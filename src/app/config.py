from pathlib import Path
from pydantic_settings import BaseSettings, SettingsConfigDict

# This file is src/app/config.py → parents[2] is the repo root
# parents[0]=src/app, parents[1]=src, parents[2]=repo root
ROOT = Path(__file__).resolve().parents[2]

class Settings(BaseSettings):
    # model_config configures HOW settings load (it's config, NOT a data field):
    #   env_file          -> file to read values from
    #   env_file_encoding -> how to decode it
    #   extra="ignore"    -> ignore env vars that don't match a field (don't error)
    # Load priority: init args > OS env vars > .env file > field defaults.
    model_config = SettingsConfigDict(
        env_file=ROOT / ".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    # --- Azure OpenAI (field names map to .env keys, case-insensitive) ---
    azure_openai_api_key: str
    azure_openai_endpoint: str
    azure_openai_api_version: str
    azure_openai_chat_deployment: str
    azure_openai_embedding_deployment: str

    # --- Vector store ---
    persist_dir: str = str(ROOT / "chroma_db")
    collection_name: str = "langchain_docs"

    # --- Corpus + chunking + retrieval ---
    corpus_urls_file: str = str(ROOT / "corpus_urls.txt")
    chunk_size: int = 1000
    chunk_overlap: int = 150
    retrieve_k: int = 4

    # --- Web loader ---
    user_agent: str = "verified-rag-assistant/0.1 (docs indexer)"

settings = Settings()