from pathlib import Path

from repository.graph import build_repository_graph
from repository.retrieval import SemanticRetriever


class GraphAugmentedRetriever:
    """
    Graph-augmented repository retriever.

    Combines semantic retrieval with code-graph
    relationships and produces a combined relevance score.
    """

    def __init__(
        self,
        repository_path: str,
    ):
        self.repository_path = Path(
            repository_path
        )

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
        """
        Add or update a retrieval result.
        """

        if file_name not in results:

            results[file_name] = {
                "file": file_name,
                "score": score,
                "source": source,
            }

        else:

            if score > results[file_name]["score"]:

                results[file_name][
                    "score"
                ] = score

                results[file_name][
                    "source"
                ] = source

    def search(
        self,
        query: str,
        top_k: int = 3,
    ) -> list[dict]:
        """
        Perform semantic retrieval followed by
        graph-based context expansion.
        """

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

            # ----------------------------------------
            # Direct semantic result
            # ----------------------------------------

            self._add_result(
                results=results,
                file_name=file_name,
                score=semantic_score,
                source="semantic",
            )

            # ----------------------------------------
            # Find corresponding graph file node
            # ----------------------------------------

            file_nodes = [
                node
                for node in self.graph.nodes.values()
                if (
                    node.node_type == "file"
                    and node.name == file_name
                )
            ]

            for file_node in file_nodes:

                # ------------------------------------
                # File dependencies
                # ------------------------------------

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
                        results=results,
                        file_name=dependency.name,
                        score=graph_score,
                        source="graph_dependency",
                    )

                # ------------------------------------
                # File dependents
                # ------------------------------------

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
                        results=results,
                        file_name=dependent.name,
                        score=graph_score,
                        source="graph_dependent",
                    )

        ranked_results = list(
            results.values()
        )

        ranked_results.sort(
            key=lambda item: item["score"],
            reverse=True,
        )

        return ranked_results


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

    retriever = GraphAugmentedRetriever(
        str(sample_repository)
    )

    query = (
        "Where is the multiplication "
        "operation implemented?"
    )

    print("\nGRAPH-AUGMENTED RETRIEVAL")
    print("=" * 70)

    print(
        f"\nQuery: {query}"
    )

    results = retriever.search(
        query,
        top_k=3,
    )

    print("\nRanked Results:")
    print("-" * 70)

    for rank, result in enumerate(
        results,
        start=1,
    ):

        print(
            f"{rank}. "
            f"File: {result['file']} | "
            f"Score: {result['score']:.4f} | "
            f"Source: {result['source']}"
        )