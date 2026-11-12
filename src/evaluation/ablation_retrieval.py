import csv
import json
from pathlib import Path

from repository.graph import build_repository_graph
from repository.retrieval import SemanticRetriever

from evaluation.retrieval_metrics import (
    precision_at_k,
    recall_at_k,
    mean_reciprocal_rank,
)


class AblationRetriever:
    """
    Retrieval system used for ablation experiments.

    Modes:

    semantic
        Semantic retrieval only.

    dependencies
        Semantic retrieval + file dependencies.

    dependents
        Semantic retrieval + file dependents.

    full
        Semantic retrieval + dependencies + dependents.
    """

    def __init__(
        self,
        repository_path: str,
        mode: str,
    ):
        self.repository_path = Path(
            repository_path
        )

        self.mode = mode

        self.semantic_retriever = (
            SemanticRetriever(
                str(self.repository_path)
            )
        )

        self.graph = build_repository_graph(
            str(self.repository_path)
        )

    def _add_result(
        self,
        results: dict,
        file_name: str,
        score: float,
    ) -> None:
        """Add a file to the result set."""

        if file_name not in results:

            results[file_name] = {
                "file": file_name,
                "score": score,
            }

        else:

            if score > results[file_name]["score"]:

                results[file_name]["score"] = score

    def search(
        self,
        query: str,
        top_k: int = 3,
    ) -> list[dict]:
        """Run retrieval according to the selected mode."""

        semantic_results = (
            self.semantic_retriever.search(
                query,
                top_k=top_k,
            )
        )

        results = {}

        for semantic_result in semantic_results:

            file_path = Path(
                semantic_result["file"]
            )

            file_name = file_path.name

            semantic_score = float(
                semantic_result["score"]
            )

            # ------------------------------------------------
            # Semantic result
            # ------------------------------------------------

            self._add_result(
                results,
                file_name,
                semantic_score,
            )

            # ------------------------------------------------
            # Find graph file node
            # ------------------------------------------------

            file_nodes = [
                node
                for node in self.graph.nodes.values()
                if (
                    node.node_type == "file"
                    and node.name == file_name
                )
            ]

            for file_node in file_nodes:

                # ------------------------------------------------
                # Dependencies
                # ------------------------------------------------

                if self.mode in {
                    "dependencies",
                    "full",
                }:

                    dependencies = (
                        self.graph.find_file_dependencies(
                            file_node.node_id
                        )
                    )

                    for dependency in dependencies:

                        graph_score = (
                            semantic_score * 0.80
                        )

                        self._add_result(
                            results,
                            dependency.name,
                            graph_score,
                        )

                # ------------------------------------------------
                # Dependents
                # ------------------------------------------------

                if self.mode in {
                    "dependents",
                    "full",
                }:

                    dependents = (
                        self.graph.find_file_dependents(
                            file_node.node_id
                        )
                    )

                    for dependent in dependents:

                        graph_score = (
                            semantic_score * 0.70
                        )

                        self._add_result(
                            results,
                            dependent.name,
                            graph_score,
                        )

        ranked_results = list(
            results.values()
        )

        ranked_results.sort(
            key=lambda item: item["score"],
            reverse=True,
        )

        return ranked_results[:top_k]


def load_ground_truth(
    file_path: Path,
) -> list[dict]:
    """Load retrieval ground truth."""

    with file_path.open(
        "r",
        encoding="utf-8",
    ) as file:

        data = json.load(file)

    return data["queries"]


def evaluate_mode(
    retriever,
    queries: list[dict],
    k: int = 3,
) -> dict:
    """Evaluate one ablation configuration."""

    precision_scores = []
    recall_scores = []
    mrr_scores = []

    for item in queries:

        query = item["query"]

        relevant_files = (
            item["relevant_files"]
        )

        results = retriever.search(
            query,
            top_k=k,
        )

        retrieved_files = [
            Path(
                result["file"]
            ).name
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

    return {
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
    }


def save_results(
    output_path: Path,
    results: dict,
) -> None:
    """Save ablation results as CSV."""

    output_path.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    with output_path.open(
        "w",
        newline="",
        encoding="utf-8",
    ) as file:

        writer = csv.writer(file)

        writer.writerow(
            [
                "configuration",
                "precision_at_3",
                "recall_at_3",
                "mrr",
            ]
        )

        for configuration, metrics in (
            results.items()
        ):

            writer.writerow(
                [
                    configuration,
                    metrics["precision_at_3"],
                    metrics["recall_at_3"],
                    metrics["mrr"],
                ]
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

    ground_truth_file = (
        project_root
        / "data"
        / "processed"
        / "retrieval_ground_truth.json"
    )

    output_file = (
        project_root
        / "results"
        / "metrics"
        / "retrieval_ablation.csv"
    )

    queries = load_ground_truth(
        ground_truth_file
    )

    configurations = {
        "semantic": "Semantic Only",
        "dependencies": (
            "Semantic + Dependencies"
        ),
        "dependents": (
            "Semantic + Dependents"
        ),
        "full": (
            "Semantic + Dependencies + Dependents"
        ),
    }

    results = {}

    print("\nRETRIEVAL ABLATION STUDY")
    print("=" * 70)

    for mode, label in configurations.items():

        print(
            f"\nRunning: {label}"
        )

        retriever = AblationRetriever(
            str(sample_repository),
            mode,
        )

        metrics = evaluate_mode(
            retriever,
            queries,
            k=3,
        )

        results[label] = metrics

    # ------------------------------------------------
    # Save results
    # ------------------------------------------------

    save_results(
        output_file,
        results,
    )

    # ------------------------------------------------
    # Display results
    # ------------------------------------------------

    print("\n\nABLATION RESULTS")
    print("=" * 90)

    print(
        f"{'Configuration':<45}"
        f"{'Precision@3':<15}"
        f"{'Recall@3':<15}"
        f"{'MRR':<10}"
    )

    print("-" * 90)

    for configuration, metrics in (
        results.items()
    ):

        print(
            f"{configuration:<45}"
            f"{metrics['precision_at_3']:<15.4f}"
            f"{metrics['recall_at_3']:<15.4f}"
            f"{metrics['mrr']:<10.4f}"
        )

    print("\nResults saved to:")
    print(output_file)