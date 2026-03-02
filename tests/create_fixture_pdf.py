"""
One-off script to generate tests/fixtures/sample.pdf.

Run once, then commit the generated PDF:
    python tests/create_fixture_pdf.py
    git add tests/fixtures/sample.pdf
"""

from pathlib import Path
from fpdf import FPDF

PAGES = [
    (
        "Artificial Intelligence and Machine Learning",
        "Artificial intelligence (AI) refers to the simulation of human intelligence "
        "processes by computer systems. Machine learning is a subset of AI that enables "
        "systems to learn and improve from experience without being explicitly programmed. "
        "Deep learning uses multi-layer neural networks to learn hierarchical representations "
        "of data. These technologies power applications such as image recognition, natural "
        "language processing, and autonomous systems.",
    ),
    (
        "Python Programming Best Practices",
        "Python is a high-level interpreted programming language known for its readability "
        "and simplicity. Best practices include writing clear docstrings, using type hints "
        "for static analysis, following PEP 8 style guidelines, and writing automated tests. "
        "Virtual environments isolate project dependencies from the system Python installation. "
        "Package management is handled with pip and requirements.txt or pyproject.toml.",
    ),
    (
        "Software Engineering Principles",
        "Software engineering applies systematic and disciplined approaches to the development "
        "of software systems. Core principles include modularity, separation of concerns, the "
        "DRY principle (Don't Repeat Yourself), and SOLID design patterns. Code review and "
        "continuous integration are standard practices in professional software development. "
        "Testing at unit, integration, and end-to-end levels ensures correctness and reliability.",
    ),
]


def create_fixture_pdf(output_path: Path) -> None:
    output_path.parent.mkdir(parents=True, exist_ok=True)
    pdf = FPDF()
    for title, body in PAGES:
        pdf.add_page()
        pdf.set_font("Helvetica", "B", 14)
        pdf.multi_cell(0, 8, title)
        pdf.ln(3)
        pdf.set_font("Helvetica", size=11)
        pdf.multi_cell(0, 7, body)
    pdf.output(str(output_path))
    print(f"Created {output_path} ({output_path.stat().st_size} bytes, {len(PAGES)} pages)")


if __name__ == "__main__":
    out = Path(__file__).parent / "fixtures" / "sample.pdf"
    create_fixture_pdf(out)
