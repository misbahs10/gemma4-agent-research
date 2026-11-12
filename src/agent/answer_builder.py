
from pathlib import Path


def normalize_file_name(file_path: str) -> str:
    """Convert a full file path into a normalized file name."""
    if not file_path:
        return ""

    return Path(str(file_path)).name


def unique_items(items: list[str]) -> list[str]:
    """Remove duplicates while preserving order."""
    result = []

    for item in items:
        if not item:
            continue

        item = str(item).strip()

        if item and item not in result:
            result.append(item)

    return result


def build_structured_answer(
    files: list[str] | None = None,
    symbols: list[str] | None = None,
    relationships: list[str] | None = None,
) -> dict:
    """Build a standardized structured answer."""

    normalized_files = [
        normalize_file_name(file_name)
        for file_name in (files or [])
        if normalize_file_name(file_name)
    ]

    return {
        "files": unique_items(normalized_files),
        "symbols": unique_items(symbols or []),
        "relationships": unique_items(relationships or []),
    }


def extract_symbols_from_context(context: str) -> list[str]:
    """Extract symbols from structured repository context."""
    symbols = []

    if not context:
        return symbols

    for line in context.splitlines():
        line = line.strip()

        if line.startswith("SYMBOL:"):
            symbol = line.split("SYMBOL:", 1)[1].strip()

            if symbol:
                symbols.append(symbol)

    return unique_items(symbols)


def extract_symbols_from_observations(
    observations: list[dict],
) -> list[str]:
    """Extract candidate symbols from search observations."""
    symbols = []

    for observation in observations:
        observation_data = observation.get("observation", {})

        if not isinstance(observation_data, dict):
            continue

        context = observation_data.get("context", "")

        if context:
            symbols.extend(extract_symbols_from_context(context))

    return unique_items(symbols)


def extract_symbols_from_file_content(content: str) -> list[str]:
    """Extract top-level and method function/class names from Python source."""
    import ast

    if not content:
        return []

    try:
        tree = ast.parse(content)
    except SyntaxError:
        return []

    symbols = []

    for node in ast.walk(tree):
        if isinstance(
            node,
            (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef),
        ):
            symbols.append(node.name)

    return unique_items(symbols)


def extract_symbols_from_read_files(
    observations: list[dict],
    selected_file: str | None = None,
) -> list[str]:
    """Extract symbols from read-file observations, optionally filtering by file."""

    symbols = []

    normalized_selected = (
        normalize_file_name(selected_file)
        if selected_file
        else None
    )

    for observation in observations:
        observation_data = observation.get("observation", {})

        if not isinstance(observation_data, dict):
            continue

        content = observation_data.get("content", "")
        observed_file = observation_data.get("file", "")

        if not content:
            continue

        if normalized_selected:
            normalized_observed = normalize_file_name(observed_file)

            if normalized_observed != normalized_selected:
                continue

        symbols.extend(extract_symbols_from_file_content(content))

    return unique_items(symbols)


def extract_relevant_symbols(
    observations: list[dict],
    selected_file: str | None = None,
) -> list[str]:
    """Prefer symbols from the selected, inspected file."""

    read_symbols = extract_symbols_from_read_files(
        observations,
        selected_file=selected_file,
    )

    if read_symbols:
        return read_symbols

    return extract_symbols_from_observations(observations)


def build_answer_from_observations(
    observations: list[dict],
    files: list[str] | None = None,
    relationships: list[str] | None = None,
    selected_file: str | None = None,
) -> dict:
    """Build a structured answer from agent observations."""

    symbols = extract_relevant_symbols(
        observations=observations,
        selected_file=selected_file,
    )

    return build_structured_answer(
        files=files or [],
        symbols=symbols,
        relationships=relationships or [],
    )


if __name__ == "__main__":
    print("\nANSWER BUILDER TEST")
    print("=" * 70)

    sample_context = """
FILE: calculator.py
SYMBOL: add
TYPE: function
LINES: 4-7

FILE: calculator.py
SYMBOL: Calculator
TYPE: class
LINES: 8-9

FILE: calculator.py
SYMBOL: multiply
TYPE: function
LINES: 10-12
"""

    sample_content = """
from utils import format_result

def add(a, b):
    return a + b

class Calculator:
    def multiply(self, a, b):
        return a * b

    def show_result(self, value):
        return format_result(value)
"""

    observations = [
        {
            "step": 1,
            "action": "search_repository",
            "observation": {"context": sample_context},
        },
        {
            "step": 2,
            "action": "read_file",
            "observation": {
                "file": "calculator.py",
                "content": sample_content,
            },
        },
    ]

    print("Context symbols:")
    print(extract_symbols_from_context(sample_context))

    print("\nFile symbols:")
    print(extract_symbols_from_file_content(sample_content))

    print("\nSelected-file symbols:")
    print(
        extract_relevant_symbols(
            observations,
            selected_file="calculator.py",
        )
    )

    print("\nStructured answer:")
    print(
        build_answer_from_observations(
            observations=observations,
            files=["calculator.py"],
            relationships=[],
            selected_file="calculator.py",
        )
    )
