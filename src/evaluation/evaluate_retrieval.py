import json
from pathlib import Path

from repository.retrieval import (
    LexicalRetriever,
    SemanticRetriever,
)

from evaluation.retrieval_metrics import (
    precision_at_k,
    recall_at_k,
    mean_reciprocal_rank,
)


def load_ground_truth(
    file_path: Path,
) -> list[dict]:
    """Load retrieval ground-truth queries."""

    with file_path.open(
        "r",
        encoding="utf-8",
    ) as file:

        data = json.load(file)

    return data["queries"]


def extract_file_name(
    file_path: str,
) -> str:
    """Extract only the file name."""

    return Path(file_path).name


def evaluate_retriever(
    retriever,
    queries: list[dict],
    k: int = 3,
) -> dict:
    """
    Evaluate a retrieval system using
    Precision@K, Recall@K and MRR.
    """

    precision_scores = []
    recall_scores = []
    mrr_scores = []

    for item in queries:

        query = item["query"]
        relevant_files = item[
            "relevant_files"
        ]

        results = retriever.search(
            query,
            top_k=k,
        )

        retrieved_files = [
            extract_file_name(
                result["file"]
            )
            for result in results
        ]

        precision = precision_at_k(
            retrieved_files,
            relevant_files,
            k,
        )

        recall = recall_at_k(
            retrieved_files,
            relevant_files,
            k,
        )

        mrr = mean_reciprocal_rank(
            retrieved_files,
            relevant_files,
        )

        precision_scores.append(
            precision
        )

        recall_scores.append(
            recall
        )

        mrr_scores.append(
            mrr
        )

        print("\nQuery:")
        print(query)

        print(
            f"Expected: {relevant_files}"
        )

        print(
            f"Retrieved: {retrieved_files}"
        )

        print(
            f"Precision@{k}: "
            f"{precision:.4f}"
        )

        print(
            f"Recall@{k}: "
            f"{recall:.4f}"
        )

        print(
            f"MRR: "
            f"{mrr:.4f}"
        )

    return {
        "precision_at_k": (
            sum(precision_scores)
            / len(precision_scores)
        ),
        "recall_at_k": (
            sum(recall_scores)
            / len(recall_scores)
        ),
        "mrr": (
            sum(mrr_scores)
            / len(mrr_scores)
        ),
    }


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

    ground_truth_file = (
        project_root
        / "data"
        / "processed"
        / "retrieval_ground_truth.json"
    )

    queries = load_ground_truth(
        ground_truth_file
    )

    print("\nRETRIEVAL EVALUATION")
    print("=" * 70)

    # ------------------------------------------------
    # Lexical Retrieval
    # ------------------------------------------------

    print("\n\nLEXICAL RETRIEVAL")
    print("=" * 70)

    lexical_retriever = LexicalRetriever(
        str(sample_repository)
    )

    lexical_metrics = evaluate_retriever(
        lexical_retriever,
        queries,
        k=3,
    )

    # ------------------------------------------------
    # Semantic Retrieval
    # ------------------------------------------------

    print("\n\nSEMANTIC RETRIEVAL")
    print("=" * 70)

    semantic_retriever = SemanticRetriever(
        str(sample_repository)
    )

    semantic_metrics = evaluate_retriever(
        semantic_retriever,
        queries,
        k=3,
    )

    # ------------------------------------------------
    # Final Comparison
    # ------------------------------------------------

    print("\n\nFINAL COMPARISON")
    print("=" * 70)

    print(
        f"\n{'Metric':<20}"
        f"{'Lexical':<15}"
        f"{'Semantic':<15}"
    )

    print("-" * 50)

    print(
        f"{'Precision@3':<20}"
        f"{lexical_metrics['precision_at_k']:<15.4f}"
        f"{semantic_metrics['precision_at_k']:<15.4f}"
    )

    print(
        f"{'Recall@3':<20}"
        f"{lexical_metrics['recall_at_k']:<15.4f}"
        f"{semantic_metrics['recall_at_k']:<15.4f}"
    )

    print(
        f"{'MRR':<20}"
        f"{lexical_metrics['mrr']:<15.4f}"
        f"{semantic_metrics['mrr']:<15.4f}"
    )