from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8")

    # API keys
    openai_api_key: str

    # LLM
    llm_model: str = "gpt-4o"

    # Embeddings
    embedding_model: str = "text-embedding-3-small"

    # Vector store
    chroma_persist_dir: str = "./data/chroma"
    collection_name: str = "documents"

    # RAG settings
    chunk_size: int = 512
    chunk_overlap: int = 64
    top_k: int = 5
    relevance_threshold: float = 0.3


settings = Settings()
