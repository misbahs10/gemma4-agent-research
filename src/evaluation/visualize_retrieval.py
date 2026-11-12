import csv
from pathlib import Path

import matplotlib.pyplot as plt


def load_results(
    file_path: Path,
) -> list[dict]:
    """Load retrieval summary CSV."""

    with file_path.open(
        "r",
        encoding="utf-8",
    ) as file:

        reader = csv.DictReader(file)

        return list(reader)


def create_metric_chart(
    results: list[dict],
    metric_column: str,
    title: str,
    output_path: Path,
) -> None:
    """Create a bar chart for one metric."""

    methods = [
        row["method"]
        for row in results
    ]

    values = [
        float(row[metric_column])
        for row in results
    ]

    plt.figure(figsize=(9, 6))

    plt.bar(
        methods,
        values,
    )

    plt.title(title)

    plt.ylabel("Score")

    plt.xlabel("Retrieval Method")

    plt.ylim(0, 1)

    plt.xticks(
        rotation=15
    )

    plt.tight_layout()

    output_path.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    plt.savefig(
        output_path,
        dpi=300,
        bbox_inches="tight",
    )

    plt.close()


if __name__ == "__main__":

    project_root = (
        Path(__file__).resolve().parents[2]
    )

    results_file = (
        project_root
        / "results"
        / "metrics"
        / "retrieval_summary.csv"
    )

    figures_directory = (
        project_root
        / "results"
        / "figures"
    )

    print("\nRETRIEVAL VISUALIZATION")
    print("=" * 70)

    # ------------------------------------------------
    # Load results
    # ------------------------------------------------

    results = load_results(
        results_file
    )

    print(
        f"\nLoaded {len(results)} methods."
    )

    # ------------------------------------------------
    # Precision@3
    # ------------------------------------------------

    precision_path = (
        figures_directory
        / "precision_at_3.png"
    )

    create_metric_chart(
        results=results,
        metric_column="precision_at_3",
        title="Retrieval Precision@3",
        output_path=precision_path,
    )

    print(
        f"Created: {precision_path}"
    )

    # ------------------------------------------------
    # Recall@3
    # ------------------------------------------------

    recall_path = (
        figures_directory
        / "recall_at_3.png"
    )

    create_metric_chart(
        results=results,
        metric_column="recall_at_3",
        title="Retrieval Recall@3",
        output_path=recall_path,
    )

    print(
        f"Created: {recall_path}"
    )

    # ------------------------------------------------
    # MRR
    # ------------------------------------------------

    mrr_path = (
        figures_directory
        / "mrr.png"
    )

    create_metric_chart(
        results=results,
        metric_column="mrr",
        title="Mean Reciprocal Rank (MRR)",
        output_path=mrr_path,
    )

    print(
        f"Created: {mrr_path}"
    )

    print("\nVisualization complete.")