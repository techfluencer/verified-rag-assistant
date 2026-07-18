"""Build the vector index: load -> split -> embed -> persist to Chroma.

Run once (re-run any time to rebuild):  uv run python scripts/build_index.py
"""
import os
from pathlib import Path

from app.config import settings

# langchain_community uses this at import time
os.environ.setdefault("USER_AGENT", settings.user_agent)

from bs4 import SoupStrainer
from langchain_community.document_loaders import WebBaseLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_openai import AzureOpenAIEmbeddings
from langchain_chroma import Chroma


def read_urls() -> list[str]:
    lines = Path(settings.corpus_urls_file).read_text().splitlines()
    return [ln.strip() for ln in lines if ln.strip() and not ln.strip().startswith("#")]

def load_and_split():
    urls =  read_urls()
    print(f"Loading {len(urls)} URLs (main content only)...")
    loader = WebBaseLoader(urls, bs_kwargs={"parse_only": SoupStrainer("main")})

    docs = loader.load()

    splitter = RecursiveCharacterTextSplitter(
        chunk_size=settings.chunk_size,
        chunk_overlap=settings.chunk_overlap,
    )

    chunks = splitter.split_documents(docs)

    print(f"{len(docs)} docs -> {len(chunks)} chunks")

    return chunks

def build():
    chunks = load_and_split()

    # Azure creds passed explicitly (pydantic-settings doesn't populate os.environ)
    embeddings = AzureOpenAIEmbeddings(
        azure_endpoint=settings.azure_openai_endpoint,
        api_key=settings.azure_openai_api_key,
        api_version=settings.azure_openai_api_version,
        azure_deployment=settings.azure_openai_embedding_deployment,
    )

    # Idempotent rebuild: drop any existing collection so re-runs don't duplicate
    Chroma(
        collection_name=settings.collection_name,
        embedding_function=embeddings,
        persist_directory=settings.persist_dir,
    ).delete_collection()

    store = Chroma.from_documents(
        documents=chunks,
        embedding=embeddings,
        persist_directory=settings.persist_dir,
        collection_name=settings.collection_name,
    )

    print(f"Persisted {store._collection.count()} vectors to {settings.persist_dir}")

if __name__=="__main__":
    build()





