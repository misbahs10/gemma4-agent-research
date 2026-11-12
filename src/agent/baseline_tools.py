from pathlib import Path

from repository.repository_retriever import (
    RepositoryRetriever,
)


class BaselineRepositoryTools:
    """
    Tools available to the baseline coding agent.

    The baseline uses semantic retrieval only.
    """

    def __init__(
        self,
        repository_path: str,
    ):
        self.repository_path = Path(
            repository_path
        )

        self.retriever = (
            RepositoryRetriever(
                str(self.repository_path),
                mode="semantic",
            )
        )

    def search_repository(
        self,
        query: str,
        top_k: int = 3,
    ) -> dict:
        """
        Search the repository and return
        agent-readable context.
        """

        result = self.retriever.retrieve(
            query=query,
            top_k=top_k,
            max_chunks=5,
        )

        return {
            "tool": "search_repository",
            "query": query,
            "files": result[
                "retrieved_files"
            ],
            "context": result[
                "context"
            ],
        }

    def read_file(
        self,
        file_name: str,
    ) -> dict:
        """
        Read a repository file.

        The file must remain inside the
        configured repository directory.
        """

        repository_root = (
            self.repository_path.resolve()
        )

        requested_file = (
            self.repository_path
            / file_name
        ).resolve()

        # --------------------------------------------
        # Security check
        # --------------------------------------------

        try:

            requested_file.relative_to(
                repository_root
            )

        except ValueError:

            raise ValueError(
                "File is outside the repository."
            )

        # --------------------------------------------
        # File existence
        # --------------------------------------------

        if not requested_file.exists():

            return {
                "tool": "read_file",
                "file": file_name,
                "error": "File not found.",
            }

        if not requested_file.is_file():

            return {
                "tool": "read_file",
                "file": file_name,
                "error": "Path is not a file.",
            }

        # --------------------------------------------
        # Read file
        # --------------------------------------------

        try:

            content = (
                requested_file.read_text(
                    encoding="utf-8"
                )
            )

        except UnicodeDecodeError:

            return {
                "tool": "read_file",
                "file": file_name,
                "error": (
                    "File is not UTF-8 text."
                ),
            }

        return {
            "tool": "read_file",
            "file": file_name,
            "content": content,
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

    tools = BaselineRepositoryTools(
        str(sample_repository)
    )

    # ------------------------------------------------
    # Test search
    # ------------------------------------------------

    print("\nSEARCH REPOSITORY")
    print("=" * 70)

    search_result = (
        tools.search_repository(
            "multiplication operation"
        )
    )

    print(
        search_result
    )

    # ------------------------------------------------
    # Test read_file
    # ------------------------------------------------

    print("\nREAD FILE")
    print("=" * 70)

    file_result = tools.read_file(
        "calculator.py"
    )

    print(
        file_result
    )