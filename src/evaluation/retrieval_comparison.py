from pathlib import Path

from repository.retrieval import (
    LexicalRetriever,
    SemanticRetriever,
)


def print_results(
    title: str,
    results: list[dict],
) -> None:
    """Print retrieval results."""

    print(f"\n{title}")
    print("-" * 70)

    if not results:
        print("No results found.")
        return

    for rank, result in enumerate(
        results,
        start=1,
    ):

        print(
            f"{rank}. "
            f"Score: {result['score']:.4f} | "
            f"File: {result['file']}"
        )


if __name__ == "__main__":

    project_root = (
        Path(__file__).resolve().parents[2]
    )

    sample_repository = (
        project_root
        / "data"
        / "raw"
        / "sample_repo"
    )

    print("\nRETRIEVAL COMPARISON")
    print("=" * 70)

    lexical_retriever = LexicalRetriever(
        str(sample_repository)
    )

    semantic_retriever = SemanticRetriever(
        str(sample_repository)
    )

    queries = [
        "multiply calculator",
        "perform multiplication",
        "calculate total",
        "format result",
    ]

    for query in queries:

        print("\n")
        print("=" * 70)
        print(f"QUERY: {query}")
        print("=" * 70)

        lexical_results = (
            lexical_retriever.search(
                query,
                top_k=3,
            )
        )

        semantic_results = (
            semantic_retriever.search(
                query,
                top_k=3,
            )
        )

        print_results(
            "LEXICAL RETRIEVAL",
            lexical_results,
        )

        print_results(
            "SEMANTIC RETRIEVAL",
            semantic_results,
        )