from pathlib import Path


class CodeChunker:
    """
    Split Python source files into structured code chunks.

    Each chunk represents a top-level function,
    class, method, or other meaningful source block.
    """

    def __init__(
        self,
        repository_path: str,
    ):
        self.repository_path = Path(
            repository_path
        )

    def discover_files(self) -> list[Path]:
        """Find Python files in the repository."""

        return list(
            self.repository_path.rglob("*.py")
        )

    def chunk_file(
        self,
        file_path: Path,
    ) -> list[dict]:
        """
        Extract source-code chunks from one Python file.
        """

        source = file_path.read_text(
            encoding="utf-8"
        )

        lines = source.splitlines()

        chunks = []

        current_chunk = []
        current_name = None
        current_type = None
        start_line = None

        for index, line in enumerate(
            lines,
            start=1,
        ):

            stripped = line.strip()

            # --------------------------------------------
            # Function
            # --------------------------------------------

            if (
                stripped.startswith("def ")
                or stripped.startswith("async def ")
            ):

                if current_chunk:

                    chunks.append(
                        self._create_chunk(
                            file_path,
                            current_name,
                            current_type,
                            start_line,
                            index - 1,
                            current_chunk,
                        )
                    )

                current_name = (
                    stripped.split("(")[0]
                    .replace(
                        "async def ",
                        "",
                    )
                    .replace(
                        "def ",
                        "",
                    )
                    .strip()
                )

                current_type = "function"

                start_line = index

                current_chunk = [line]

                continue

            # --------------------------------------------
            # Class
            # --------------------------------------------

            if stripped.startswith("class "):

                if current_chunk:

                    chunks.append(
                        self._create_chunk(
                            file_path,
                            current_name,
                            current_type,
                            start_line,
                            index - 1,
                            current_chunk,
                        )
                    )

                current_name = (
                    stripped.split("(")[0]
                    .replace(
                        "class ",
                        "",
                    )
                    .replace(
                        ":",
                        "",
                    )
                    .strip()
                )

                current_type = "class"

                start_line = index

                current_chunk = [line]

                continue

            # --------------------------------------------
            # Add line to current chunk
            # --------------------------------------------

            if current_chunk:

                current_chunk.append(line)

        # --------------------------------------------
        # Final chunk
        # --------------------------------------------

        if current_chunk:

            chunks.append(
                self._create_chunk(
                    file_path,
                    current_name,
                    current_type,
                    start_line,
                    len(lines),
                    current_chunk,
                )
            )

        # --------------------------------------------
        # If no functions/classes exist
        # --------------------------------------------

        if not chunks and lines:

            chunks.append(
                self._create_chunk(
                    file_path,
                    file_path.stem,
                    "module",
                    1,
                    len(lines),
                    lines,
                )
            )

        return chunks

    def _create_chunk(
        self,
        file_path: Path,
        name: str,
        chunk_type: str,
        start_line: int,
        end_line: int,
        lines: list[str],
    ) -> dict:
        """Create a structured chunk."""

        return {
            "file": file_path.name,
            "name": name,
            "type": chunk_type,
            "start_line": start_line,
            "end_line": end_line,
            "content": "\n".join(lines),
        }

    def build_chunks(self) -> list[dict]:
        """Build chunks for the entire repository."""

        all_chunks = []

        for file_path in self.discover_files():

            chunks = self.chunk_file(
                file_path
            )

            all_chunks.extend(
                chunks
            )

        return all_chunks


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

    chunker = CodeChunker(
        str(sample_repository)
    )

    chunks = chunker.build_chunks()

    print("\nCODE CHUNKS")
    print("=" * 70)

    for index, chunk in enumerate(
        chunks,
        start=1,
    ):

        print(
            f"\nChunk {index}"
        )

        print(
            f"File: {chunk['file']}"
        )

        print(
            f"Name: {chunk['name']}"
        )

        print(
            f"Type: {chunk['type']}"
        )

        print(
            f"Lines: "
            f"{chunk['start_line']}-"
            f"{chunk['end_line']}"
        )

        print("-" * 70)

        print(
            chunk["content"]
        )