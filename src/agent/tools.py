from pathlib import Path

from repository.graph import build_repository_graph
from repository.query_engine import GraphQueryEngine


class GraphQueryTools:
    """
    Agent-facing interface for repository graph queries.

    This class converts graph queries into simple,
    structured results that an AI agent can consume.
    """

    def __init__(
        self,
        repository_path: str,
    ):
        self.repository_path = (
            repository_path
        )

        self.graph = build_repository_graph(
            repository_path
        )

        self.engine = GraphQueryEngine(
            self.graph
        )

    def find_symbol(
        self,
        symbol_name: str,
    ) -> list[dict]:
        """
        Find symbols in the repository.
        """

        nodes = self.engine.find_symbol(
            symbol_name
        )

        return [
            {
                "name": node.name,
                "type": node.node_type,
                "file": node.file_path,
                "id": node.node_id,
            }
            for node in nodes
        ]

    def find_callers(
        self,
        symbol_name: str,
    ) -> list[dict]:
        """
        Find functions or methods that call
        the requested symbol.
        """

        callers = self.engine.who_calls(
            symbol_name
        )

        return [
            {
                "name": node.name,
                "type": node.node_type,
                "file": node.file_path,
                "id": node.node_id,
            }
            for node in callers
        ]

    def find_callees(
        self,
        symbol_name: str,
    ) -> list[dict]:
        """
        Find functions or methods called
        by the requested symbol.
        """

        callees = self.engine.what_does_call(
            symbol_name
        )

        return [
            {
                "name": node.name,
                "type": node.node_type,
                "file": node.file_path,
                "id": node.node_id,
            }
            for node in callees
        ]

    def find_dependencies(
        self,
        file_name: str,
    ) -> list[dict]:
        """
        Find files imported by a file.
        """

        dependencies = (
            self.engine.file_dependencies(
                file_name
            )
        )

        return [
            {
                "name": node.name,
                "type": node.node_type,
                "file": node.file_path,
                "id": node.node_id,
            }
            for node in dependencies
        ]

    def find_dependents(
        self,
        file_name: str,
    ) -> list[dict]:
        """
        Find files that import a file.
        """

        dependents = (
            self.engine.file_dependents(
                file_name
            )
        )

        return [
            {
                "name": node.name,
                "type": node.node_type,
                "file": node.file_path,
                "id": node.node_id,
            }
            for node in dependents
        ]

    def find_path(
        self,
        start_symbol: str,
        target_symbol: str,
    ) -> list[dict]:
        """
        Find a graph path between two symbols.
        """

        path = self.engine.path_between(
            start_symbol,
            target_symbol,
        )

        return [
            {
                "name": node.name,
                "type": node.node_type,
                "file": node.file_path,
                "id": node.node_id,
            }
            for node in path
        ]


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

    tools = GraphQueryTools(
        str(sample_repository)
    )

    print("\nGRAPH QUERY TOOLS")
    print("=" * 70)

    print("\n1. Find Symbol")
    print("-" * 70)

    result = tools.find_symbol(
        "multiply"
    )

    for item in result:
        print(item)

    print("\n2. Find Callers")
    print("-" * 70)

    result = tools.find_callers(
        "multiply"
    )

    for item in result:
        print(item)

    print("\n3. Find Callees")
    print("-" * 70)

    result = tools.find_callees(
        "run"
    )

    for item in result:
        print(item)

    print("\n4. Find Dependencies")
    print("-" * 70)

    result = tools.find_dependencies(
        "main.py"
    )

    for item in result:
        print(item)

    print("\n5. Find Dependents")
    print("-" * 70)

    result = tools.find_dependents(
        "calculator.py"
    )

    for item in result:
        print(item)

    print("\n6. Find Path")
    print("-" * 70)

    result = tools.find_path(
        "run",
        "multiply",
    )

    for item in result:
        print(item)