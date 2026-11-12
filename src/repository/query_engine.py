
from pathlib import Path

from repository.graph import CodeGraph, GraphNode, build_repository_graph


class GraphQueryEngine:
    """High-level query interface for repository code graphs."""

    def __init__(self, graph: CodeGraph):
        self.graph = graph

    def find_symbol(self, name: str) -> list[GraphNode]:
        """Find graph nodes with a given symbol name."""
        return self.graph.find_nodes(name)

    def who_calls(self, symbol_name: str) -> list[GraphNode]:
        """Find functions or methods that call a symbol."""
        callers = []

        for node in self.find_symbol(symbol_name):
            callers.extend(self.graph.find_callers(node.node_id))

        return callers

    def what_does_call(self, symbol_name: str) -> list[GraphNode]:
        """Find symbols called by a function or method."""
        callees = []

        for node in self.find_symbol(symbol_name):
            callees.extend(self.graph.find_callees(node.node_id))

        return callees

    def file_dependencies(self, file_name: str) -> list[GraphNode]:
        """Find files imported by a given file."""
        file_node = self._find_file(file_name)

        if file_node is None:
            return []

        return self.graph.find_file_dependencies(file_node.node_id)

    def file_dependents(self, file_name: str) -> list[GraphNode]:
        """Find files that import a given file."""
        file_node = self._find_file(file_name)

        if file_node is None:
            return []

        return self.graph.find_file_dependents(file_node.node_id)

    def path_between(
        self,
        start_symbol: str,
        target_symbol: str,
        allowed_relations: set[str] | None = None,
    ) -> list[GraphNode]:
        """
        Find a graph path between two symbols.

        If allowed_relations is provided, traverse only those edge
        types. For example, {"calls"} restricts the path to actual
        function-call relationships.
        """
        start_nodes = self.find_symbol(start_symbol)
        target_nodes = self.find_symbol(target_symbol)

        if not start_nodes or not target_nodes:
            return []

        # Prefer symbol nodes over file nodes if both are returned.
        start_node = next(
            (
                node for node in start_nodes
                if node.node_type != "file"
            ),
            None,
        )
        target_node = next(
            (
                node for node in target_nodes
                if node.node_type != "file"
            ),
            None,
        )

        if start_node is None or target_node is None:
            return []

        path_ids = self.graph.find_path(
            start_node.node_id,
            target_node.node_id,
            allowed_relations=allowed_relations,
        )

        return [
            self.graph.nodes[node_id]
            for node_id in path_ids
            if node_id in self.graph.nodes
        ]

    def _find_file(self, file_name: str) -> GraphNode | None:
        """Find a file node by file name."""
        expected_name = Path(file_name).name

        for node in self.graph.nodes.values():
            if (
                node.node_type == "file"
                and Path(node.name).name == expected_name
            ):
                return node

        return None


if __name__ == "__main__":
    project_root = Path(__file__).resolve().parents[2]
    sample_repository = project_root / "data" / "raw" / "sample_repo"

    graph = build_repository_graph(str(sample_repository))
    engine = GraphQueryEngine(graph)

    print("\nQUERY 1: Who calls multiply?")
    for node in engine.who_calls("multiply"):
        print(f"  {node.name} -> calls -> multiply")

    print("\nQUERY 2: What does run call?")
    for node in engine.what_does_call("run"):
        print(f"  run -> calls -> {node.name}")

    print("\nQUERY 3: main.py dependencies")
    for node in engine.file_dependencies("main.py"):
        print(f"  main.py -> imports -> {node.name}")

    print("\nQUERY 4: Files importing calculator.py")
    for node in engine.file_dependents("calculator.py"):
        print(f"  {node.name} -> imports -> calculator.py")

    print("\nQUERY 5: Call path from run to multiply")
    path = engine.path_between(
        "run",
        "multiply",
        allowed_relations={"calls"},
    )

    for node in path:
        print(f"  [{node.node_type}] {node.name}")
