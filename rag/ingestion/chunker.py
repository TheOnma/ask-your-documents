"""Recursive character text splitter. Splits pages into overlapping chunks."""

import logging

from rag.config import settings

logger = logging.getLogger(__name__)


def split_text(text: str, chunk_size: int, chunk_overlap: int) -> list[str]:
    """
    Recursively split text using a hierarchy of separators.

    Tries to split on paragraph boundaries first, then sentences, then words.
    """
    separators = ["\n\n", "\n", ". ", " ", ""]

    def _split(text: str, separators: list[str]) -> list[str]:
        if len(text) <= chunk_size or not separators:
            return [text] if text.strip() else []

        sep = separators[0]
        remaining_seps = separators[1:]

        parts = text.split(sep) if sep else list(text)
        chunks = []
        current = ""

        for part in parts:
            candidate = current + (sep if current else "") + part
            if len(candidate) <= chunk_size:
                current = candidate
            else:
                if current.strip():
                    chunks.append(current.strip())
                if len(part) > chunk_size:
                    chunks.extend(_split(part, remaining_seps))
                    current = ""
                else:
                    current = part

        if current.strip():
            chunks.append(current.strip())

        return chunks

    raw_chunks = _split(text, separators)

    # Apply overlap by prepending the tail of the previous chunk
    if chunk_overlap <= 0 or len(raw_chunks) <= 1:
        return raw_chunks

    overlapped = [raw_chunks[0]]
    for i in range(1, len(raw_chunks)):
        prev_tail = raw_chunks[i - 1][-chunk_overlap:]
        overlapped.append(prev_tail + " " + raw_chunks[i])

    return overlapped


PAGE_SPLIT_THRESHOLD = 4000  # chars; only sub-chunk pages longer than this


def chunk_pages(pages: list[dict]) -> list[dict]:
    """
    Emit one chunk per PDF page where possible, falling back to character
    splitting only for unusually long pages (> PAGE_SPLIT_THRESHOLD chars).

    Keeping pages whole prevents numbered lists and multi-paragraph answers
    from being sliced across chunk boundaries, which hurts retrieval accuracy.

    Args:
        pages — output from loader.load_pdf()

    Returns:
        list of {"text": str, "metadata": {"source", "page", "chunk"}}
    """
    chunks = []

    for page in pages:
        text = page["text"]
        if len(text) <= PAGE_SPLIT_THRESHOLD:
            # Page fits within the embedding model's context — keep it whole
            chunks.append({"text": text, "metadata": {**page["metadata"], "chunk": 0}})
        else:
            # Unusually long page — fall back to character splitting
            sub_chunks = split_text(text, settings.chunk_size, settings.chunk_overlap)
            for j, chunk_text in enumerate(sub_chunks):
                chunks.append({"text": chunk_text, "metadata": {**page["metadata"], "chunk": j}})

    logger.info("Created %d chunks from %d pages", len(chunks), len(pages))
    return chunks
