"""
Entry points:

  # Start the API server
  python main.py serve

  # Ingest a PDF from the command line
  python main.py ingest path/to/doc.pdf

  # Ask a question from the command line
  python main.py ask "What is the document about?"

  # Ask and print the raw retrieved chunks (useful for debugging)
  python main.py ask "What is the document about?" --show-context
"""

import logging
import sys

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)s %(name)s — %(message)s",
)


def serve():
    import uvicorn
    uvicorn.run("src.api.routes:app", host="0.0.0.0", port=8000, reload=True)


def ingest(path: str):
    from src.pipelines.rag import ingest_pdf
    n = ingest_pdf(path)
    print(f"Ingested {n} chunks from {path}")


def ask(question: str, show_context: bool = False):
    from src.pipelines.rag import answer
    result = answer(question)

    if show_context and result["sources"]:
        from src.retrieval.retriever import _get_collection
        collection = _get_collection()
        print("\n--- Retrieved Context ---")
        for i, source in enumerate(result["sources"], 1):
            res = collection.get(
                where={"$and": [{"source": source["source"]}, {"page": source["page"]}]},
                include=["documents"],
            )
            text = res["documents"][0] if res["documents"] else "(not found)"
            print(f"\n[{i}] {source['source']} page {source['page']} (score={source['score']})")
            print(text[:800] + ("..." if len(text) > 800 else ""))
        print("\n--- End Context ---")

    print(f"\nAnswer:\n{result['answer']}")
    if result["sources"]:
        print("\nSources:")
        for s in result["sources"]:
            print(f"  - {s['source']} page {s['page']} (score={s['score']})")


if __name__ == "__main__":
    args = sys.argv[1:]
    if not args:
        print(__doc__)
        sys.exit(1)

    command = args[0]
    if command == "serve":
        serve()
    elif command == "ingest" and len(args) == 2:
        ingest(args[1])
    elif command == "ask" and len(args) >= 2:
        show_ctx = "--show-context" in args
        question_parts = [a for a in args[1:] if a != "--show-context"]
        ask(" ".join(question_parts), show_context=show_ctx)
    else:
        print(__doc__)
        sys.exit(1)
