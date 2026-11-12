from repository.chunker import CodeChunker


class ContextBuilder:
    """
    Build structured context for an AI coding agent.
    """

    def __init__(
        self,
        repository_path: str,
    ):
        self.chunker = CodeChunker(
            repository_path
        )

    def build_context(
        self,
        retrieved_files: list[str],
        max_chunks: int = 5,
    ) -> list[dict]:
        """
        Build context from retrieved files.

        Only chunks belonging to retrieved files
        are included.
        """

        all_chunks = (
            self.chunker.build_chunks()
        )

        context = []

        for chunk in all_chunks:

            if chunk["file"] in retrieved_files:

                context.append(
                    chunk
                )

        return context[:max_chunks]

    def format_context(
        self,
        context: list[dict],
    ) -> str:
        """
        Convert structured chunks into
        agent-readable context.
        """

        sections = []

        for chunk in context:

            section = (
                f"FILE: {chunk['file']}\n"
                f"SYMBOL: {chunk['name']}\n"
                f"TYPE: {chunk['type']}\n"
                f"LINES: "
                f"{chunk['start_line']}-"
                f"{chunk['end_line']}\n"
                f"\n"
                f"{chunk['content']}"
            )

            sections.append(
                section
            )

        return (
            "\n\n"
            + ("\n\n" + "=" * 70 + "\n\n").join(
                sections
            )
        )


if __name__ == "__main__":

    from pathlib import Path

    project_root = (
        Path(__file__).resolve().parents[2]
    )

    sample_repository = (
        project_root
        / "data"
        / "raw"
        / "sample_repo"
    )

    builder = ContextBuilder(
        str(sample_repository)
    )

    retrieved_files = [
        "calculator.py"
    ]

    context = builder.build_context(
        retrieved_files
    )

    formatted_context = (
        builder.format_context(
            context
        )
    )

    print("\nAGENT CONTEXT")
    print("=" * 70)

    print(
        formatted_context
    )