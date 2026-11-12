from pathlib import Path

from repository.graph import build_repository_graph
from repository.retrieval import SemanticRetriever


class AblationRetriever:
    """
    Retrieval system used for controlled ablation experiments.

    Modes:

        semantic
        dependencies
        dependents
        full
    """

    VALID_MODES = {
        "semantic",
        "dependencies",
        "dependents",
        "full",
    }

    def __init__(
        self,
        repository_path: str,
        mode: str = "semantic",
    ):
        if mode not in self.VALID_MODES:
            raise ValueError(
                f"Invalid mode: {mode}. "
                f"Expected one of: "
                f"{sorted(self.VALID_MODES)}"
            )

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
        source: str,
    ) -> None:

        if file_name not in results:

            results[file_name] = {
                "file": file_name,
                "score": score,
                "source": source,
            }

            return

        if score > results[file_name]["score"]:

            results[file_name]["score"] = score

            results[file_name]["source"] = source

    def _graph_expand(
        self,
        semantic_results: list[dict],
        include_dependencies: bool,
        include_dependents: bool,
    ) -> list[dict]:

        results = {}

        for result in semantic_results:

            file_path = Path(
                result["file"]
            )

            file_name = file_path.name

            semantic_score = float(
                result["score"]
            )

            self._add_result(
                results,
                file_name,
                semantic_score,
                "semantic",
            )

            file_nodes = [
                node
                for node in self.graph.nodes.values()
                if (
                    node.node_type == "file"
                    and node.name == file_name
                )
            ]

            for file_node in file_nodes:

                if include_dependencies:

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
                            "dependency",
                        )

                if include_dependents:

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
                            "dependent",
                        )

        ranked_results = list(
            results.values()
        )

        ranked_results.sort(
            key=lambda item: item["score"],
            reverse=True,
        )

        return ranked_results

    def search(
        self,
        query: str,
        top_k: int = 3,
    ) -> list[dict]:

        semantic_results = (
            self.semantic_retriever.search(
                query,
                top_k=top_k,
            )
        )

        if self.mode == "semantic":

            return [
                {
                    "file": Path(
                        result["file"]
                    ).name,
                    "score": float(
                        result["score"]
                    ),
                    "source": "semantic",
                }
                for result in semantic_results
            ][:top_k]

        if self.mode == "dependencies":

            return self._graph_expand(
                semantic_results,
                include_dependencies=True,
                include_dependents=False,
            )[:top_k]

        if self.mode == "dependents":

            return self._graph_expand(
                semantic_results,
                include_dependencies=False,
                include_dependents=True,
            )[:top_k]

        return self._graph_expand(
            semantic_results,
            include_dependencies=True,
            include_dependents=True,
        )[:top_k]


if __name__ == "__main__":

    project_root = (
        Path(__file__).resolve().parents[2]
    )

    repository = (
        project_root
        / "data"
        / "raw"
        / "sample_repo"
    )

    query = (
        "Find where the multiplication "
        "operation is implemented."
    )

    for mode in [
        "semantic",
        "dependencies",
        "dependents",
        "full",
    ]:

        retriever = AblationRetriever(
            str(repository),
            mode=mode,
        )

        results = retriever.search(
            query,
            top_k=3,
        )

        print("\n")
        print("=" * 70)
        print(
            f"MODE: {mode}"
        )
        print("=" * 70)

        for result in results:

            print(
                f"{result['file']} | "
                f"score={result['score']:.4f} | "
                f"source={result['source']}"
            )