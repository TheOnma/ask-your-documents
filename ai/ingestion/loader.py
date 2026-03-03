"""Document loaders for PDF, DOCX, and TXT files. Extracts text preserving source metadata."""

import logging
from pathlib import Path

from pypdf import PdfReader

logger = logging.getLogger(__name__)


def load_txt(path: str | Path) -> list[dict]:
    """
    Load a plain-text file and return it as a single page dict.

    Args:
        path — path to the .txt file

    Returns:
        list of {"text": str, "metadata": {"source": str, "page": int}}
    """
    path = Path(path)
    if not path.exists():
        raise FileNotFoundError(f"Text file not found: {path}")

    text = path.read_text(encoding="utf-8", errors="replace").strip()
    if not text:
        logger.warning("%s is empty", path.name)
        return []

    logger.info("Loaded text file %s (%d chars)", path.name, len(text))
    return [{"text": text, "metadata": {"source": path.name, "page": 1}}]


def load_docx(path: str | Path) -> list[dict]:
    """
    Load a Word document (.docx) and return its paragraphs grouped into pseudo-pages.

    Every 40 non-empty paragraphs are treated as one page so that the chunker
    receives reasonably-sized text blocks. Documents with fewer than 40 paragraphs
    are returned as a single page.

    Args:
        path — path to the .docx file

    Returns:
        list of {"text": str, "metadata": {"source": str, "page": int}}
    """
    from docx import Document  # lazy import so pypdf isn't penalised if docx absent

    path = Path(path)
    if not path.exists():
        raise FileNotFoundError(f"DOCX file not found: {path}")

    doc = Document(str(path))
    paragraphs = [p.text.strip() for p in doc.paragraphs if p.text.strip()]

    if not paragraphs:
        logger.warning("%s has no extractable text", path.name)
        return []

    PAGE_SIZE = 40
    pages = []
    for page_num, start in enumerate(range(0, len(paragraphs), PAGE_SIZE), 1):
        text = "\n".join(paragraphs[start : start + PAGE_SIZE])
        pages.append({"text": text, "metadata": {"source": path.name, "page": page_num}})

    logger.info("Loaded %d pseudo-pages from %s", len(pages), path.name)
    return pages


def load_pdf(path: str | Path) -> list[dict]:
    """
    Load a PDF and return a list of page dicts.

    Args:
        path — path to the PDF file

    Returns:
        list of {"text": str, "metadata": {"source": str, "page": int}}
    """
    path = Path(path)
    if not path.exists():
        raise FileNotFoundError(f"PDF not found: {path}")

    reader = PdfReader(str(path))
    pages = []

    for i, page in enumerate(reader.pages):
        text = page.extract_text() or ""
        text = text.strip()
        if not text:
            logger.debug("Page %d of %s is empty — skipping", i + 1, path.name)
            continue
        pages.append({
            "text": text,
            "metadata": {
                "source": path.name,
                "page": i + 1,
            },
        })

    logger.info("Loaded %d pages from %s", len(pages), path.name)
    return pages


def load_pdfs_from_dir(directory: str | Path) -> list[dict]:
    """Load all PDFs from a directory."""
    directory = Path(directory)
    all_pages = []
    pdf_files = sorted(directory.glob("*.pdf"))

    if not pdf_files:
        logger.warning("No PDFs found in %s", directory)
        return []

    for pdf_path in pdf_files:
        try:
            all_pages.extend(load_pdf(pdf_path))
        except Exception as e:
            logger.error("Failed to load %s: %s", pdf_path.name, e)

    logger.info("Loaded %d total pages from %d PDFs", len(all_pages), len(pdf_files))
    return all_pages
