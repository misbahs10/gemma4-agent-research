from pathlib import Path

from repository.retrieval import SemanticRetriever
from repository.graph_retrieval import GraphAugmentedRetriever
from repository.context_builder import ContextBuilder


class RepositoryRetriever:
    """
    Unified repository retrieval pipeline.

    Supports:

    1. Semantic retrieval
    2. Graph-augmented retrieval
    3. Code chunk extraction
    4. Agent-ready context construction
    """

    def __init__(
        self,
        repository_path: str,
        mode: str = "semantic",
    ):
        self.repository_path = Path(
            repository_path
        )

        self.mode = mode

        if mode == "semantic":

            self.retriever = (
                SemanticRetriever(
                    str(self.repository_path)
                )
            )

        elif mode == "graph":

            self.retriever = (
                GraphAugmentedRetriever(
                    str(self.repository_path)
                )
            )

        else:

            raise ValueError(
                "mode must be "
                "'semantic' or 'graph'"
            )

        self.context_builder = (
            ContextBuilder(
                str(self.repository_path)
            )
        )

    def retrieve(
        self,
        query: str,
        top_k: int = 3,
        max_chunks: int = 5,
    ) -> dict:
        """
        Execute the complete retrieval pipeline.
        """

        # ------------------------------------------------
        # Step 1: Retrieve relevant files
        # ------------------------------------------------

        retrieval_results = (
            self.retriever.search(
                query,
                top_k=top_k,
            )
        )

        retrieved_files = [
            Path(
                result["file"]
            ).name
            for result in retrieval_results
        ]

        # Remove duplicates while preserving order
        retrieved_files = list(
            dict.fromkeys(
                retrieved_files
            )
        )

        # ------------------------------------------------
        # Step 2: Build code context
        # ------------------------------------------------

        context = (
            self.context_builder.build_context(
                retrieved_files,
                max_chunks=max_chunks,
            )
        )

        # ------------------------------------------------
        # Step 3: Format agent context
        # ------------------------------------------------

        formatted_context = (
            self.context_builder.format_context(
                context
            )
        )

        return {
            "query": query,
            "mode": self.mode,
            "retrieval_results": (
                retrieval_results
            ),
            "retrieved_files": (
                retrieved_files
            ),
            "chunks": context,
            "context": formatted_context,
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

    query = (
        "Where is the multiplication "
        "operation implemented?"
    )

    # ------------------------------------------------
    # Semantic Pipeline
    # ------------------------------------------------

    print("\nSEMANTIC PIPELINE")
    print("=" * 70)

    semantic_pipeline = (
        RepositoryRetriever(
            str(sample_repository),
            mode="semantic",
        )
    )

    semantic_result = (
        semantic_pipeline.retrieve(
            query,
            top_k=3,
            max_chunks=5,
        )
    )

    print(
        "\nRetrieved Files:"
    )

    for file_name in (
        semantic_result["retrieved_files"]
    ):

        print(
            f"  - {file_name}"
        )

    print(
        "\nAgent Context:"
    )

    print(
        semantic_result["context"]
    )

    # ------------------------------------------------
    # Graph Pipeline
    # ------------------------------------------------

    print("\n\nGRAPH PIPELINE")
    print("=" * 70)

    graph_pipeline = (
        RepositoryRetriever(
            str(sample_repository),
            mode="graph",
        )
    )

    graph_result = (
        graph_pipeline.retrieve(
            query,
            top_k=3,
            max_chunks=5,
        )
    )

    print(
        "\nRetrieved Files:"
    )

    for file_name in (
        graph_result["retrieved_files"]
    ):

        print(
            f"  - {file_name}"
        )

    print(
        "\nAgent Context:"
    )

    print(
        graph_result["context"]
    )