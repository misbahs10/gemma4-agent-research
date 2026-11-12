import csv
import json
from pathlib import Path

from repository.ablation_retriever import (
    AblationRetriever,
)

from evaluation.retrieval_metrics import (
    mean_reciprocal_rank,
    precision_at_k,
    recall_at_k,
)


MODES = [
    "semantic",
    "dependencies",
    "dependents",
    "full",
]


def load_ground_truth(
    file_path: Path,
) -> list[dict]:

    with file_path.open(
        "r",
        encoding="utf-8",
    ) as file:

        data = json.load(file)

    return data["queries"]


def evaluate_mode(
    repository_path: Path,
    queries: list[dict],
    mode: str,
    top_k: int = 3,
) -> list[dict]:

    retriever = AblationRetriever(
        str(repository_path),
        mode=mode,
    )

    results = []

    for item in queries:

        query = item["query"]

        relevant_files = item[
            "relevant_files"
        ]

        retrieved = retriever.search(
            query,
            top_k=top_k,
        )

        retrieved_files = [
            result["file"]
            for result in retrieved
        ]

        precision = precision_at_k(
            retrieved_files,
            relevant_files,
            top_k,
        )

        recall = recall_at_k(
            retrieved_files,
            relevant_files,
            top_k,
        )

        mrr = mean_reciprocal_rank(
            retrieved_files,
            relevant_files,
        )

        results.append(
            {
                "mode": mode,
                "query": query,
                "relevant_files":
                    relevant_files,
                "retrieved_files":
                    retrieved_files,
                "precision_at_3":
                    precision,
                "recall_at_3":
                    recall,
                "mrr":
                    mrr,
            }
        )

    return results


def save_results(
    results: list[dict],
    output_file: Path,
) -> None:

    fieldnames = [
        "mode",
        "query",
        "relevant_files",
        "retrieved_files",
        "precision_at_3",
        "recall_at_3",
        "mrr",
    ]

    with output_file.open(
        "w",
        newline="",
        encoding="utf-8",
    ) as file:

        writer = csv.DictWriter(
            file,
            fieldnames=fieldnames,
        )

        writer.writeheader()

        for result in results:

            row = result.copy()

            row["relevant_files"] = (
                ";".join(
                    row["relevant_files"]
                )
            )

            row["retrieved_files"] = (
                ";".join(
                    row["retrieved_files"]
                )
            )

            writer.writerow(row)


def create_summary(
    results: list[dict],
) -> list[dict]:

    summary = []

    for mode in MODES:

        mode_results = [
            result
            for result in results
            if result["mode"] == mode
        ]

        if not mode_results:
            continue

        count = len(
            mode_results
        )

        summary.append(
            {
                "mode": mode,
                "queries": count,
                "mean_precision_at_3": (
                    sum(
                        result[
                            "precision_at_3"
                        ]
                        for result
                        in mode_results
                    )
                    / count
                ),
                "mean_recall_at_3": (
                    sum(
                        result[
                            "recall_at_3"
                        ]
                        for result
                        in mode_results
                    )
                    / count
                ),
                "mean_mrr": (
                    sum(
                        result["mrr"]
                        for result
                        in mode_results
                    )
                    / count
                ),
            }
        )

    return summary


def save_summary(
    summary: list[dict],
    output_file: Path,
) -> None:

    fieldnames = [
        "mode",
        "queries",
        "mean_precision_at_3",
        "mean_recall_at_3",
        "mean_mrr",
    ]

    with output_file.open(
        "w",
        newline="",
        encoding="utf-8",
    ) as file:

        writer = csv.DictWriter(
            file,
            fieldnames=fieldnames,
        )

        writer.writeheader()

        writer.writerows(summary)


if __name__ == "__main__":

    project_root = (
        Path(__file__).resolve().parents[2]
    )

    repository_path = (
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

    metrics_directory = (
        project_root
        / "results"
        / "metrics"
    )

    metrics_directory.mkdir(
        parents=True,
        exist_ok=True,
    )

    queries = load_ground_truth(
        ground_truth_file
    )

    all_results = []

    for mode in MODES:

        print("\n")
        print("=" * 70)
        print(
            f"Running ablation: {mode}"
        )
        print("=" * 70)

        mode_results = evaluate_mode(
            repository_path,
            queries,
            mode,
        )

        all_results.extend(
            mode_results
        )

    detailed_file = (
        metrics_directory
        / "retrieval_ablation_detailed.csv"
    )

    summary_file = (
        metrics_directory
        / "retrieval_ablation_summary.csv"
    )

    save_results(
        all_results,
        detailed_file,
    )

    summary = create_summary(
        all_results
    )

    save_summary(
        summary,
        summary_file,
    )

    print("\n")
    print("=" * 70)
    print("ABLATION COMPLETED")
    print("=" * 70)

    print(
        "\nSummary:"
    )

    for row in summary:

        print(
            f"\nMode: {row['mode']}"
        )

        print(
            f"Precision@3: "
            f"{row['mean_precision_at_3']:.4f}"
        )

        print(
            f"Recall@3: "
            f"{row['mean_recall_at_3']:.4f}"
        )

        print(
            f"MRR: "
            f"{row['mean_mrr']:.4f}"
        )

    print(
        f"\nDetailed results:"
    )

    print(detailed_file)

    print(
        f"\nSummary:"
    )

    print(summary_file)