from pathlib import Path


class LexicalRetriever:
    """
    Simple keyword-based repository retriever.

    Searches Python source files for query terms
    and returns the most relevant files.
    """

    def __init__(
        self,
        repository_path: str,
    ):
        self.repository_path = Path(
            repository_path
        )

    def discover_files(self) -> list[Path]:
        """Find all Python files in the repository."""

        return list(
            self.repository_path.rglob("*.py")
        )

    def search(
        self,
        query: str,
        top_k: int = 5,
    ) -> list[dict]:
        """
        Search repository files using query keywords.
        """

        query_terms = {
            term.lower()
            for term in query.split()
            if term.strip()
        }

        results = []

        for file_path in self.discover_files():

            try:
                content = file_path.read_text(
                    encoding="utf-8"
                )

            except UnicodeDecodeError:
                continue

            content_lower = content.lower()

            score = 0

            for term in query_terms:

                score += content_lower.count(
                    term
                )

            if score > 0:

                results.append(
                    {
                        "file": str(file_path),
                        "score": score,
                    }
                )

        results.sort(
            key=lambda item: item["score"],
            reverse=True,
        )

        return results[:top_k]


class SemanticRetriever:
    """
    Semantic repository retriever using embeddings.

    Converts repository files and user queries
    into vector representations and ranks files
    using cosine similarity.
    """

    def __init__(
        self,
        repository_path: str,
        model_name: str = "all-MiniLM-L6-v2",
    ):
        self.repository_path = Path(
            repository_path
        )

        from sentence_transformers import (
            SentenceTransformer
        )

        self.model = SentenceTransformer(
            model_name
        )

    def discover_files(self) -> list[Path]:
        """Find all Python files."""

        return list(
            self.repository_path.rglob("*.py")
        )

    def build_documents(self) -> list[dict]:
        """
        Convert repository files into documents
        that can be embedded.
        """

        documents = []

        for file_path in self.discover_files():

            try:
                content = file_path.read_text(
                    encoding="utf-8"
                )

            except UnicodeDecodeError:
                continue

            documents.append(
                {
                    "file": str(file_path),
                    "content": content,
                }
            )

        return documents

    def search(
        self,
        query: str,
        top_k: int = 5,
    ) -> list[dict]:
        """
        Retrieve repository files using
        semantic similarity.
        """

        documents = self.build_documents()

        if not documents:
            return []

        query_embedding = self.model.encode(
            query,
            convert_to_tensor=True,
        )

        document_texts = [
            document["content"]
            for document in documents
        ]

        document_embeddings = self.model.encode(
            document_texts,
            convert_to_tensor=True,
        )

        from sentence_transformers.util import (
            cos_sim
        )

        similarities = cos_sim(
            query_embedding,
            document_embeddings,
        )[0]

        results = []

        for index, document in enumerate(
            documents
        ):

            results.append(
                {
                    "file": document["file"],
                    "content": document["content"],
                    "score": float(
                        similarities[index]
                    ),
                }
            )

        results.sort(
            key=lambda item: item["score"],
            reverse=True,
        )

        return results[:top_k]


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

    # ------------------------------------------------
    # Lexical Retrieval Test
    # ------------------------------------------------

    print("\nLEXICAL RETRIEVAL")
    print("=" * 70)

    lexical_retriever = LexicalRetriever(
        str(sample_repository)
    )

    lexical_query = "multiply calculator"

    print(
        f"\nQuery: {lexical_query}"
    )

    lexical_results = (
        lexical_retriever.search(
            lexical_query,
            top_k=3,
        )
    )

    print("\nResults:")
    print("-" * 70)

    for result in lexical_results:

        print(
            f"Score: {result['score']} | "
            f"File: {result['file']}"
        )

    # ------------------------------------------------
    # Semantic Retrieval Test
    # ------------------------------------------------

    print("\n\nSEMANTIC RETRIEVAL")
    print("=" * 70)

    semantic_retriever = SemanticRetriever(
        str(sample_repository)
    )

    semantic_query = (
        "Where is the multiplication "
        "operation implemented?"
    )

    print(
        f"\nQuery: {semantic_query}"
    )

    semantic_results = (
        semantic_retriever.search(
            semantic_query,
            top_k=3,
        )
    )

    print("\nResults:")
    print("-" * 70)

    for result in semantic_results:

        print(
            f"Score: {result['score']:.4f} | "
            f"File: {result['file']}"
        )