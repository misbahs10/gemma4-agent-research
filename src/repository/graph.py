from dataclasses import dataclass, field
from pathlib import Path
import re

from repository.parser import PythonParser


@dataclass
class GraphNode:
    node_id: str
    node_type: str
    name: str
    file_path: str


@dataclass
class GraphEdge:
    source: str
    target: str
    relation: str


@dataclass
class CodeGraph:
    nodes: dict[str, GraphNode] = field(default_factory=dict)
    edges: list[GraphEdge] = field(default_factory=list)

    def add_node(
        self,
        node_id: str,
        node_type: str,
        name: str,
        file_path: str,
    ) -> None:
        if node_id not in self.nodes:
            self.nodes[node_id] = GraphNode(
                node_id=node_id,
                node_type=node_type,
                name=name,
                file_path=file_path,
            )

    def add_edge(
        self,
        source: str,
        target: str,
        relation: str,
    ) -> None:
        edge = GraphEdge(
            source=source,
            target=target,
            relation=relation,
        )
        if edge not in self.edges:
            self.edges.append(edge)

    def find_nodes(self, name: str) -> list[GraphNode]:
        """Find graph nodes by exact symbol or file name."""
        return [node for node in self.nodes.values() if node.name == name]

    def find_callers(self, node_id: str) -> list[GraphNode]:
        """Find functions/methods that call the given node."""
        return [
            self.nodes[edge.source]
            for edge in self.edges
            if edge.target == node_id
            and edge.relation == "calls"
            and edge.source in self.nodes
        ]

    def find_callees(self, node_id: str) -> list[GraphNode]:
        """Find functions/methods called by the given node."""
        return [
            self.nodes[edge.target]
            for edge in self.edges
            if edge.source == node_id
            and edge.relation == "calls"
            and edge.target in self.nodes
        ]

    def find_file_dependencies(self, file_node_id: str) -> list[GraphNode]:
        """Find files imported by the given file node."""
        return [
            self.nodes[edge.target]
            for edge in self.edges
            if edge.source == file_node_id
            and edge.relation == "imports"
            and edge.target in self.nodes
        ]

    def find_file_dependents(self, file_node_id: str) -> list[GraphNode]:
        """Find files that import the given file node."""
        return [
            self.nodes[edge.source]
            for edge in self.edges
            if edge.target == file_node_id
            and edge.relation == "imports"
            and edge.source in self.nodes
        ]

    def find_path(
        self,
        start_node_id: str,
        target_node_id: str,
        allowed_relations: set[str] | None = None,
    ) -> list[str]:
        """Find a shortest path; optionally restrict which edge types are traversed."""
        if start_node_id not in self.nodes or target_node_id not in self.nodes:
            return []

        queue: list[tuple[str, list[str]]] = [(start_node_id, [start_node_id])]
        visited: set[str] = set()

        while queue:
            current, path = queue.pop(0)
            if current in visited:
                continue
            visited.add(current)

            if current == target_node_id:
                return path

            for edge in self.edges:
                if edge.source != current:
                    continue
                if allowed_relations is not None and edge.relation not in allowed_relations:
                    continue
                if edge.target not in visited:
                    queue.append((edge.target, path + [edge.target]))

        return []

    def display(self) -> None:
        """Print all nodes, edges, and graph counts."""
        print("\nREPOSITORY CODE GRAPH")
        print("=" * 70)
        print("\nNodes:")
        print("-" * 70)
        for node in self.nodes.values():
            print(f"  [{node.node_type}] {node.name}")
            print(f"      ID: {node.node_id}")
            print(f"      File: {node.file_path}")

        print("\nEdges:")
        print("-" * 70)
        for edge in self.edges:
            source = self.nodes.get(edge.source)
            target = self.nodes.get(edge.target)
            source_label = f"{source.file_path}:{source.name}" if source else edge.source
            target_label = f"{target.file_path}:{target.name}" if target else edge.target
            print(f"  {source_label} --{edge.relation}--> {target_label}")

        print("\nGraph Summary:")
        print("-" * 70)
        print(f"  Total Nodes: {len(self.nodes)}")
        print(f"  Total Edges: {len(self.edges)}")


def discover_python_files(repository_path: str) -> list[Path]:
    """Discover Python files, excluding common environment/cache folders."""
    root = Path(repository_path)
    excluded_directories = {".venv", "venv", "__pycache__", ".git"}
    if not root.exists() or not root.is_dir():
        return []

    python_files = []
    for path in root.rglob("*.py"):
        if any(part in excluded_directories for part in path.parts):
            continue
        python_files.append(path)
    return sorted(python_files)


def _parse_import_entry(import_name: str) -> tuple[str, str | None]:
    """Return (module_name, imported_symbol) for common parser import formats.

    Supported examples:
      - 'calculator.add' -> ('calculator', 'add')
      - 'from calculator import add' -> ('calculator', 'add')
      - 'calculator' -> ('calculator', None)
    """
    value = str(import_name).strip()
    if not value:
        return "", None

    from_match = re.match(
        r"^from\s+([\w.]+)\s+import\s+([\w*]+)$",
        value,
    )
    if from_match:
        return from_match.group(1).split(".")[0], from_match.group(2)

    # The current parser may encode "from module import symbol" as module.symbol.
    parts = value.split(".")
    if len(parts) >= 2:
        return parts[0], parts[1]
    return value, None


def build_repository_graph(repository_path: str) -> CodeGraph:
    """Build a repository graph with file, definition, import, and call edges."""
    repository = Path(repository_path).resolve()
    graph = CodeGraph()
    python_files = discover_python_files(str(repository))

    print("\nRepository Analysis")
    print("=" * 70)
    print(f"Repository: {repository}")
    print(f"Python files found: {len(python_files)}")

    # File nodes
    file_nodes: dict[str, str] = {}
    for file_path in python_files:
        relative_key = file_path.relative_to(repository).as_posix()
        file_node_id = f"file:{relative_key}"
        file_nodes[relative_key] = file_node_id
        graph.add_node(file_node_id, "file", file_path.name, relative_key)

    # Parse source files
    analyses = {}
    for file_path in python_files:
        relative_path = file_path.relative_to(repository).as_posix()
        try:
            parser = PythonParser(str(file_path))
            analyses[relative_path] = parser.analyze()
        except Exception as error:
            print(f"Could not parse {file_path}: {error}")

    # Symbol table: (relative path, symbol name, kind) -> node ID
    symbol_nodes: dict[tuple[str, str, str], str] = {}

    for relative_path, analysis in analyses.items():
        file_node_id = file_nodes[relative_path]

        for class_name in analysis.get("classes", []):
            class_node_id = f"class:{relative_path}:{class_name}"
            symbol_nodes[(relative_path, class_name, "class")] = class_node_id
            graph.add_node(class_node_id, "class", class_name, relative_path)
            graph.add_edge(file_node_id, class_node_id, "defines")

        for function in analysis.get("functions", []):
            function_name = function["name"]
            function_type = function.get("type", "function")
            parent_class = function.get("class")

            if parent_class:
                function_node_id = f"method:{relative_path}:{parent_class}:{function_name}"
                symbol_nodes[(relative_path, parent_class, function_name)] = function_node_id
                class_node_id = symbol_nodes.get((relative_path, parent_class, "class"))
                if class_node_id:
                    graph.add_edge(class_node_id, function_node_id, "defines")
            else:
                function_node_id = f"function:{relative_path}:{function_name}"
                symbol_nodes[(relative_path, function_name, "function")] = function_node_id
                graph.add_edge(file_node_id, function_node_id, "defines")

            graph.add_node(function_node_id, function_type, function_name, relative_path)

    # Import map. Each entry tracks both imported module/file and optional symbol.
    import_map: dict[str, list[dict[str, str | None]]] = {}
    for relative_path, analysis in analyses.items():
        import_map[relative_path] = []
        for raw_import in analysis.get("imports", []):
            module_name, imported_symbol = _parse_import_entry(raw_import)
            if not module_name:
                continue

            for candidate_path in file_nodes:
                candidate = Path(candidate_path)
                if candidate.stem == module_name:
                    entry = {
                        "module": module_name,
                        "file": candidate_path,
                        "symbol": imported_symbol,
                    }
                    if entry not in import_map[relative_path]:
                        import_map[relative_path].append(entry)
                    break

    # File-level import edges
    for relative_path, imports in import_map.items():
        source_file_node = file_nodes[relative_path]
        for imported in imports:
            target_file_node = file_nodes[imported["file"]]
            graph.add_edge(source_file_node, target_file_node, "imports")

    # Infer local/imported object types for method calls
    object_types: dict[str, dict[str, str]] = {}
    for relative_path, analysis in analyses.items():
        object_types[relative_path] = {}
        for item in analysis.get("object_types", []):
            object_types[relative_path][item["object"]] = item["type"]

    resolved_types: dict[str, dict[str, dict[str, str]]] = {}
    for relative_path, analysis in analyses.items():
        resolved_types[relative_path] = {}
        local_classes = set(analysis.get("classes", []))

        for object_name, type_name in object_types[relative_path].items():
            if type_name in local_classes:
                resolved_types[relative_path][object_name] = {
                    "type": type_name,
                    "file": relative_path,
                }
                continue

            for imported in import_map.get(relative_path, []):
                imported_file = imported["file"]
                target_analysis = analyses.get(imported_file, {})
                if type_name in target_analysis.get("classes", []):
                    resolved_types[relative_path][object_name] = {
                        "type": type_name,
                        "file": imported_file,
                    }
                    class_node_id = symbol_nodes.get((imported_file, type_name, "class"))
                    if class_node_id:
                        graph.add_edge(file_nodes[relative_path], class_node_id, "uses")
                    break

    # Resolve calls, including imported free functions.
    for relative_path, analysis in analyses.items():
        for call in analysis.get("calls", []):
            caller_name = call.get("caller")
            caller_class = call.get("caller_class")
            callee_name = call.get("callee")
            object_name = call.get("object")

            if not caller_name or not callee_name:
                continue

            if caller_class:
                caller_node_id = symbol_nodes.get((relative_path, caller_class, caller_name))
            else:
                caller_node_id = symbol_nodes.get((relative_path, caller_name, "function"))
            if caller_node_id is None:
                continue

            # Object method calls, including instances of imported classes.
            if object_name:
                resolved_object = resolved_types.get(relative_path, {}).get(object_name)
                if resolved_object:
                    method_node_id = symbol_nodes.get(
                        (resolved_object["file"], resolved_object["type"], callee_name)
                    )
                    if method_node_id:
                        graph.add_edge(caller_node_id, method_node_id, "calls")
                        continue

            # Same-file function.
            local_function_node_id = symbol_nodes.get(
                (relative_path, callee_name, "function")
            )
            if local_function_node_id:
                graph.add_edge(caller_node_id, local_function_node_id, "calls")
                continue

            # Same-class method.
            if caller_class:
                local_method_node_id = symbol_nodes.get(
                    (relative_path, caller_class, callee_name)
                )
                if local_method_node_id:
                    graph.add_edge(caller_node_id, local_method_node_id, "calls")
                    continue

            # Imported free function, e.g. main.py imports add from calculator.py.
            for imported in import_map.get(relative_path, []):
                if imported.get("symbol") != callee_name:
                    continue
                imported_file = imported["file"]
                imported_function_node_id = symbol_nodes.get(
                    (imported_file, callee_name, "function")
                )
                if imported_function_node_id:
                    graph.add_edge(caller_node_id, imported_function_node_id, "calls")
                    break

    return graph


if __name__ == "__main__":
    project_root = Path(__file__).resolve().parents[2]
    sample_repository = project_root / "data" / "raw" / "sample_repo"
    code_graph = build_repository_graph(str(sample_repository))
    code_graph.display()

    print("\n\nQUERY 1")
    print("=" * 70)
    print("Who calls Calculator.multiply?")
    for node in code_graph.find_nodes("multiply"):
        for caller in code_graph.find_callers(node.node_id):
            print(f"  {caller.file_path}:{caller.name} -> calls -> {node.file_path}:{node.name}")

    print("\n\nQUERY 2")
    print("=" * 70)
    print("What is defined in calculator.py?")
    for node in code_graph.nodes.values():
        if node.file_path == "calculator.py":
            print(f"  [{node.node_type}] {node.name}")

    print("\n\nQUERY 3")
    print("=" * 70)
    print("What does main.py depend on?")
    main_file = code_graph.nodes.get("file:main.py")
    if main_file:
        for dependency in code_graph.find_file_dependencies(main_file.node_id):
            print(f"  main.py -> imports -> {dependency.name}")

    print("\n\nQUERY 4")
    print("=" * 70)
    print("Which files import calculator.py?")
    calculator_file = code_graph.nodes.get("file:calculator.py")
    if calculator_file:
        for dependent in code_graph.find_file_dependents(calculator_file.node_id):
            print(f"  {dependent.name} -> imports -> calculator.py")

    print("\n\nQUERY 5")
    print("=" * 70)
    print("Path from run to Calculator.multiply:")
    run_nodes = code_graph.find_nodes("run")
    multiply_nodes = code_graph.find_nodes("multiply")
    if run_nodes and multiply_nodes:
        path = code_graph.find_path(
            run_nodes[0].node_id,
            multiply_nodes[0].node_id,
            allowed_relations={"calls"},
        )
        for node_id in path:
            node = code_graph.nodes.get(node_id)
            if node:
                print(f"  [{node.node_type}] {node.file_path}:{node.name}")
