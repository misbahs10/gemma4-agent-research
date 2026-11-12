from pathlib import Path


def normalize_name(name: str) -> str:
    """
    Normalize a symbol name for comparison.
    """

    return name.strip().lower()


def normalize_files(
    files: list[str],
) -> set[str]:
    """
    Normalize repository file names.
    """

    normalized = set()

    for file_name in files:

        name = (
            Path(file_name).name
        )

        normalized.add(
            normalize_name(name)
        )

    return normalized


def normalize_symbols(
    symbols: list[str],
) -> set[str]:
    """
    Normalize symbol names.
    """

    return {
        normalize_name(symbol)
        for symbol in symbols
        if symbol
    }


def symbol_match(
    predicted_symbols: list[str],
    expected_symbols: list[str],
) -> bool:
    """
    Return True when at least one expected
    symbol is correctly identified.
    """

    expected = normalize_symbols(
        expected_symbols
    )

    predicted = normalize_symbols(
        predicted_symbols
    )

    if not expected:
        return False

    return bool(
        expected.intersection(
            predicted
        )
    )


def symbol_recall(
    predicted_symbols: list[str],
    expected_symbols: list[str],
) -> float:
    """
    Calculate recall over expected symbols.
    """

    expected = normalize_symbols(
        expected_symbols
    )

    predicted = normalize_symbols(
        predicted_symbols
    )

    if not expected:
        return 0.0

    matched = expected.intersection(
        predicted
    )

    return len(matched) / len(expected)


def extract_symbols_from_context(
    context: str,
) -> list[str]:
    """
    Extract simple symbol names from the
    structured context produced by ContextBuilder.

    This is a lightweight development parser,
    not the final semantic evaluator.
    """

    symbols = []

    for line in context.splitlines():

        line = line.strip()

        if line.startswith(
            "SYMBOL:"
        ):

            symbol = (
                line.split(
                    "SYMBOL:",
                    1,
                )[1]
                .strip()
            )

            if symbol:
                symbols.append(
                    symbol
                )

    return symbols