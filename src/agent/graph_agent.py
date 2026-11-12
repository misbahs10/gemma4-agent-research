
import re
from pathlib import Path

from agent.base_agent import BaseCodingAgent
from agent.tool_registry import ToolRegistry
from agent.answer_builder import build_structured_answer
from repository.graph import build_repository_graph
from repository.repository_retriever import RepositoryRetriever
from repository.query_engine import GraphQueryEngine


class GraphAugmentedCodingAgent(BaseCodingAgent):
    """Graph-augmented repository reasoning agent."""

    SYMBOL_ALIASES = {
        "multiply": ("multiplication", "multiply_numbers", "product"),
        "add": (
            "addition",
            "add_numbers",
            "adds two numbers",
            "add two numbers",
            "sum two numbers",
            "sum of two numbers",
        ),
        "format_result": (
            "format_output",
            "format_answer",
            "result formatting",
            "formatting functionality",
            "format the result",
        ),
        "run": ("main", "run_app"),
    }

    PATH_RELATIONS = {"calls"}

    def __init__(self, repository_path, *args, **kwargs):
        """Initialize the graph-augmented agent."""
        super().__init__(repository_path, *args, **kwargs)

        self.repository_path = Path(repository_path).resolve()
        self.graph = build_repository_graph(
            str(self.repository_path)
        )
        self.query_engine = GraphQueryEngine(self.graph)
        self.retriever = RepositoryRetriever(
            str(self.repository_path)
        )
        self.tool_registry = ToolRegistry()

    def _task_symbols(self, task):
        """Extract repository symbols mentioned in a task."""
        text = str(task)

        available_symbols = {
            node.name
            for node in self.graph.nodes.values()
            if getattr(node, "node_type", None) != "file"
        }

        found = []
        seen = set()

        # Preserve the order in which symbols appear in the task.
        matches = []

        for symbol in available_symbols:
            if not symbol:
                continue

            pattern = rf"(?<!\w){re.escape(symbol)}(?!\w)"
            match = re.search(
                pattern,
                text,
                flags=re.IGNORECASE,
            )

            if match:
                matches.append((match.start(), symbol))

        for _, symbol in sorted(
            matches,
            key=lambda item: item[0],
        ):
            key = symbol.lower()

            if key not in seen:
                found.append(symbol)
                seen.add(key)

        lower_text = text.lower()

        for canonical, aliases in self.SYMBOL_ALIASES.items():
            if canonical.lower() in seen:
                continue

            if any(alias.lower() in lower_text for alias in aliases):
                if canonical in available_symbols:
                    found.append(canonical)
                    seen.add(canonical.lower())

        return found

    def _find_symbol_nodes(self, symbol):
        """Find graph nodes matching a symbol name."""
        return [
            node
            for node in self.graph.nodes.values()
            if getattr(node, "node_type", None) != "file"
            and node.name.lower() == symbol.lower()
        ]

    @staticmethod
    def _node_file(node):
        """Return the filename associated with a graph node."""
        file_path = getattr(node, "file_path", None)
        return Path(file_path).name if file_path else None

    def _path_endpoints(self, task):
        """Extract source and target symbols from a call-chain question."""
        text = str(task)
        lower = text.lower()

        # Explicit paths, e.g. "from run in main.py to apply_discount".
        match = re.search(
            r"\bfrom\s+([a-zA-Z_]\w*)\b"
            r".*?\bto\s+([a-zA-Z_]\w*)\b",
            lower,
            flags=re.IGNORECASE,
        )

        if match:
            return match.group(1), match.group(2)

        # Delegation, e.g. "calculate_total delegates ... to apply_discount".
        match = re.search(
            r"\b(?:delegates?|calls?|invokes?)\b"
            r".{0,160}?\bto\s+([a-zA-Z_]\w*)\b",
            lower,
            flags=re.IGNORECASE,
        )

        if match:
            target = match.group(1)
            verb_position = match.start()

            candidates = []

            for symbol in self._task_symbols(text):
                position = lower.rfind(
                    symbol.lower(),
                    0,
                    verb_position,
                )

                if position >= 0:
                    candidates.append((position, symbol))

            if candidates:
                source = max(
                    candidates,
                    key=lambda item: item[0],
                )[1]

                if source.lower() != target.lower():
                    return source, target

        symbols = self._task_symbols(text)

        chain_phrases = (
            "function-call chain",
            "function call chain",
            "complete call chain",
            "order-processing flow",
            "call chain",
            "execution flow",
            "trace the flow",
            "trace how",
        )

        if len(symbols) >= 2 and any(
            phrase in lower for phrase in chain_phrases
        ):
            entry = re.search(
                r"\b(?:from|starting at|starting from)\s+"
                r"([a-zA-Z_]\w*)\b",
                lower,
            )

            if entry:
                start = entry.group(1)
                target = symbols[-1]

                if start.lower() != target.lower():
                    return start, target

            return symbols[0], symbols[-1]

        if len(symbols) >= 2:
            return symbols[0], symbols[-1]

        return None, None

    def _find_call_path(self, source, target):
        """Find a path restricted to function-call relationships."""
        if not source or not target:
            return []

        path = self.query_engine.path_between(
            source,
            target,
            allowed_relations=self.PATH_RELATIONS,
        )

        return [
            node
            for node in (path or [])
            if getattr(node, "node_type", None) != "file"
        ]

    def _get_call_edges(self, source_node, target_node):
        """Read direct edge relations from the graph representation."""
        relations = set()
        edges = getattr(self.graph, "edges", None)

        if isinstance(edges, list):
            for edge in edges:
                if (
                    getattr(edge, "source", None)
                    == source_node.node_id
                    and getattr(edge, "target", None)
                    == target_node.node_id
                ):
                    relation = getattr(edge, "relation", None)

                    if relation:
                        relations.add(relation)

        adjacency = getattr(self.graph, "adjacency", None)

        if isinstance(adjacency, dict):
            neighbors = adjacency.get(source_node.node_id, {})

            if isinstance(neighbors, dict):
                for target_id, edge_data in neighbors.items():
                    if target_id != target_node.node_id:
                        continue

                    if isinstance(edge_data, dict):
                        relation = (
                            edge_data.get("relation")
                            or edge_data.get("type")
                        )

                        if relation:
                            relations.add(relation)

                    elif isinstance(edge_data, list):
                        for item in edge_data:
                            if isinstance(item, dict):
                                relation = (
                                    item.get("relation")
                                    or item.get("type")
                                )

                                if relation:
                                    relations.add(relation)

        return relations

    def _is_direct_call(self, source_node, target_node):
        """Check for an actual direct function-call edge."""
        return "calls" in self._get_call_edges(
            source_node,
            target_node,
        )

    def _select_answer_files(self, task):
        """Select files containing requested symbols and call-chain nodes."""
        selected_files = []
        seen_files = set()

        def add_file(file_path):
            if not file_path:
                return

            path = Path(file_path)

            if not path.is_absolute():
                path = self.repository_path / path

            try:
                resolved = path.resolve()
                resolved.relative_to(self.repository_path)
            except (ValueError, OSError):
                return

            if not resolved.is_file():
                return

            key = str(resolved).lower()

            if key not in seen_files:
                selected_files.append(resolved)
                seen_files.add(key)

        for symbol in self._task_symbols(task):
            for node in self._find_symbol_nodes(symbol):
                add_file(getattr(node, "file_path", None))

        source, target = self._path_endpoints(task)

        if source and target:
            for node in self._find_call_path(source, target):
                add_file(getattr(node, "file_path", None))

        if not selected_files:
            try:
                retrieved = self.retriever.retrieve(str(task))
            except (AttributeError, TypeError):
                retrieved = []

            if isinstance(retrieved, (list, tuple)):
                for item in retrieved:
                    if isinstance(item, (str, Path)):
                        add_file(item)
                    else:
                        add_file(
                            getattr(item, "file_path", None)
                            or getattr(item, "path", None)
                        )

        return selected_files

    def build_relationships(self, task):
        """Build verified direct function-call relationships."""
        relationships = []
        seen = set()

        source, target = self._path_endpoints(task)

        if not source or not target:
            return relationships

        path = self._find_call_path(source, target)

        for source_node, target_node in zip(path, path[1:]):
            if not self._is_direct_call(source_node, target_node):
                continue

            source_file = self._node_file(source_node)
            target_file = self._node_file(target_node)

            relationship = (
                f"{source_file}:{source_node.name} -> "
                f"{target_file}:{target_node.name}"
            )

            key = (
                source_node.name.lower(),
                target_node.name.lower(),
                (source_file or "").lower(),
                (target_file or "").lower(),
            )

            if key not in seen:
                relationships.append(relationship)
                seen.add(key)

        return relationships

    def run(self, task: str, task_type: str | None = None):
        """Answer a repository question with structured graph evidence."""
        task = str(task).strip()

        if not task:
            answer = build_structured_answer()
            answer['task_type'] = task_type
            return answer

        selected_files = self._select_answer_files(task)
        file_names = [path.name for path in selected_files]
        symbols = self._task_symbols(task)
        relationships = self.build_relationships(task)

        answer = build_structured_answer(
            files=file_names,
            symbols=symbols,
            relationships=relationships,
        )
        answer["task_type"] = task_type
        return answer
