import csv
import json
from pathlib import Path

from repository.retrieval import (
    LexicalRetriever,
    SemanticRetriever,
)

from repository.graph_retrieval import (
    GraphAugmentedRetriever,
)

from evaluation.retrieval_metrics import (
    precision_at_k,
    recall_at_k,
    mean_reciprocal_rank,
)


def load_ground_truth(
    file_path: Path,
) -> list[dict]:
    """Load retrieval evaluation dataset."""

    with file_path.open(
        "r",
        encoding="utf-8",
    ) as file:

        data = json.load(file)

    return data["queries"]


def extract_file_name(
    file_path: str,
) -> str:
    """Return only the file name."""

    return Path(file_path).name


def evaluate_retriever(
    retriever,
    queries: list[dict],
    k: int = 3,
) -> dict:
    """
    Evaluate one retrieval system.

    Metrics:
    - Precision@K
    - Recall@K
    - MRR
    """

    precision_scores = []
    recall_scores = []
    mrr_scores = []

    query_results = []

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

        query_results.append(
            {
                "query": query,
                "relevant_files": (
                    relevant_files
                ),
                "retrieved_files": (
                    retrieved_files
                ),
                "precision_at_3": precision,
                "recall_at_3": recall,
                "mrr": mrr,
            }
        )

    return {
        "metrics": {
            "precision_at_3": (
                sum(precision_scores)
                / len(precision_scores)
            ),
            "recall_at_3": (
                sum(recall_scores)
                / len(recall_scores)
            ),
            "mrr": (
                sum(mrr_scores)
                / len(mrr_scores)
            ),
        },
        "queries": query_results,
    }


def save_json(
    output_path: Path,
    results: dict,
) -> None:
    """Save experiment results as JSON."""

    output_path.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    with output_path.open(
        "w",
        encoding="utf-8",
    ) as file:

        json.dump(
            results,
            file,
            indent=4,
        )


def save_csv(
    output_path: Path,
    results: dict,
) -> None:
    """Save summary metrics as CSV."""

    output_path.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    rows = []

    for method, data in results.items():

        rows.append(
            {
                "method": method,
                "precision_at_3": (
                    data["metrics"][
                        "precision_at_3"
                    ]
                ),
                "recall_at_3": (
                    data["metrics"][
                        "recall_at_3"
                    ]
                ),
                "mrr": (
                    data["metrics"]["mrr"]
                ),
            }
        )

    with output_path.open(
        "w",
        newline="",
        encoding="utf-8",
    ) as file:

        writer = csv.DictWriter(
            file,
            fieldnames=[
                "method",
                "precision_at_3",
                "recall_at_3",
                "mrr",
            ],
        )

        writer.writeheader()

        writer.writerows(rows)


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

    results_directory = (
        project_root
        / "results"
        / "metrics"
    )

    queries = load_ground_truth(
        ground_truth_file
    )

    print("\nRETRIEVAL EXPERIMENT")
    print("=" * 70)

    # ------------------------------------------------
    # Initialize retrievers
    # ------------------------------------------------

    print(
        "\nInitializing retrievers..."
    )

    lexical_retriever = LexicalRetriever(
        str(sample_repository)
    )

    semantic_retriever = SemanticRetriever(
        str(sample_repository)
    )

    graph_retriever = GraphAugmentedRetriever(
        str(sample_repository)
    )

    # ------------------------------------------------
    # Run experiments
    # ------------------------------------------------

    print(
        "Running Lexical Retrieval..."
    )

    lexical_results = evaluate_retriever(
        lexical_retriever,
        queries,
        k=3,
    )

    print(
        "Running Semantic Retrieval..."
    )

    semantic_results = evaluate_retriever(
        semantic_retriever,
        queries,
        k=3,
    )

    print(
        "Running Graph-Augmented Retrieval..."
    )

    graph_results = evaluate_retriever(
        graph_retriever,
        queries,
        k=3,
    )

    # ------------------------------------------------
    # Combine results
    # ------------------------------------------------

    all_results = {
        "lexical": lexical_results,
        "semantic": semantic_results,
        "graph_augmented": graph_results,
    }

    # ------------------------------------------------
    # Save JSON
    # ------------------------------------------------

    json_path = (
        results_directory
        / "retrieval_results.json"
    )

    save_json(
        json_path,
        all_results,
    )

    # ------------------------------------------------
    # Save CSV
    # ------------------------------------------------

    csv_path = (
        results_directory
        / "retrieval_summary.csv"
    )

    save_csv(
        csv_path,
        all_results,
    )

    # ------------------------------------------------
    # Print final comparison
    # ------------------------------------------------

    print("\n\nFINAL RESULTS")
    print("=" * 70)

    print(
        f"{'Method':<25}"
        f"{'Precision@3':<15}"
        f"{'Recall@3':<15}"
        f"{'MRR':<15}"
    )

    print("-" * 70)

    for method, data in all_results.items():

        metrics = data["metrics"]

        print(
            f"{method:<25}"
            f"{metrics['precision_at_3']:<15.4f}"
            f"{metrics['recall_at_3']:<15.4f}"
            f"{metrics['mrr']:<15.4f}"
        )

    print("\nResults saved:")
    print(
        f"JSON: {json_path}"
    )

    print(
        f"CSV:  {csv_path}"
    )