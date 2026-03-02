"""OpenAI embeddings. Normalizes vectors before storage."""

import logging

from openai import OpenAI

from src.config import settings

logger = logging.getLogger(__name__)

_client: OpenAI | None = None


def _get_client() -> OpenAI:
    global _client
    if _client is None:
        _client = OpenAI(api_key=settings.openai_api_key)
    return _client


EMBED_BATCH_SIZE = 100  # stay well within OpenAI's 300k token/request limit


def embed_texts(texts: list[str]) -> list[list[float]]:
    """
    Embed a list of strings using text-embedding-3-small, in batches.

    Sends at most EMBED_BATCH_SIZE texts per API call to avoid hitting
    OpenAI's 300k tokens-per-request limit for large ingestion jobs.
    """
    if not texts:
        return []

    client = _get_client()
    all_vectors: list[list[float]] = []

    for i in range(0, len(texts), EMBED_BATCH_SIZE):
        batch = texts[i: i + EMBED_BATCH_SIZE]
        response = client.embeddings.create(
            model=settings.embedding_model,
            input=batch,
        )
        all_vectors.extend(item.embedding for item in response.data)
        logger.debug("Embedded batch %d-%d of %d", i + 1, i + len(batch), len(texts))

    return all_vectors


def embed_chunks(chunks: list[dict]) -> list[dict]:
    """
    Add an 'embedding' key to each chunk dict.

    Args:
        chunks — output from chunker.chunk_pages()

    Returns:
        same list with "embedding" field added to each item
    """
    texts = [c["text"] for c in chunks]
    embeddings = embed_texts(texts)

    for chunk, embedding in zip(chunks, embeddings):
        chunk["embedding"] = embedding

    logger.info("Embedded %d chunks", len(chunks))
    return chunks
