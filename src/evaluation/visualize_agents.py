import csv
from pathlib import Path

import matplotlib.pyplot as plt


def load_summary(
    csv_file: Path,
) -> list[dict]:
    """
    Load agent evaluation summary.
    """

    with csv_file.open(
        "r",
        encoding="utf-8",
    ) as file:

        reader = csv.DictReader(file)

        return list(reader)


def get_metric_values(
    rows: list[dict],
    metric: str,
) -> tuple[list[str], list[float]]:
    """
    Extract agent names and metric values.
    """

    agents = []
    values = []

    for row in rows:

        agents.append(
            row["agent"]
        )

        values.append(
            float(row[metric])
        )

    return agents, values


def save_metric_chart(
    rows: list[dict],
    metric: str,
    title: str,
    ylabel: str,
    output_file: Path,
) -> None:
    """
    Create and save a bar chart for one metric.
    """

    agents, values = get_metric_values(
        rows,
        metric,
    )

    plt.figure(
        figsize=(8, 5)
    )

    plt.bar(
        agents,
        values,
    )

    plt.title(title)

    plt.ylabel(ylabel)

    plt.xlabel("Agent")

    plt.ylim(
        0,
        1,
    )

    plt.tight_layout()

    plt.savefig(
        output_file,
        dpi=200,
    )

    plt.close()


def save_tool_call_chart(
    rows: list[dict],
    output_file: Path,
) -> None:
    """
    Create tool-call comparison chart.
    """

    agents = []

    values = []

    for row in rows:

        agents.append(
            row["agent"]
        )

        values.append(
            float(
                row["average_tool_calls"]
            )
        )

    plt.figure(
        figsize=(8, 5)
    )

    plt.bar(
        agents,
        values,
    )

    plt.title(
        "Average Tool Calls"
    )

    plt.ylabel(
        "Average Tool Calls"
    )

    plt.xlabel(
        "Agent"
    )

    plt.tight_layout()

    plt.savefig(
        output_file,
        dpi=200,
    )

    plt.close()


if __name__ == "__main__":

    project_root = (
        Path(__file__).resolve().parents[2]
    )

    summary_file = (
        project_root
        / "results"
        / "metrics"
        / "agent_summary.csv"
    )

    figures_directory = (
        project_root
        / "results"
        / "figures"
    )

    figures_directory.mkdir(
        parents=True,
        exist_ok=True,
    )

    rows = load_summary(
        summary_file
    )

    save_metric_chart(
        rows,
        metric="exact_match_rate",
        title="Agent Exact Match Rate",
        ylabel="Exact Match Rate",
        output_file=(
            figures_directory
            / "agent_exact_match.png"
        ),
    )

    save_metric_chart(
        rows,
        metric="average_precision",
        title="Agent Average Precision",
        ylabel="Precision",
        output_file=(
            figures_directory
            / "agent_precision.png"
        ),
    )

    save_metric_chart(
        rows,
        metric="average_recall",
        title="Agent Average Recall",
        ylabel="Recall",
        output_file=(
            figures_directory
            / "agent_recall.png"
        ),
    )

    save_tool_call_chart(
        rows,
        output_file=(
            figures_directory
            / "agent_tool_calls.png"
        ),
    )

    print("\n")
    print("=" * 70)
    print("AGENT VISUALIZATION COMPLETED")
    print("=" * 70)

    print(
        "\nGenerated figures:"
    )

    print(
        figures_directory
        / "agent_exact_match.png"
    )

    print(
        figures_directory
        / "agent_precision.png"
    )

    print(
        figures_directory
        / "agent_recall.png"
    )

    print(
        figures_directory
        / "agent_tool_calls.png"
    )