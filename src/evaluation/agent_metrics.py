def normalize_files(
    files: list[str],
) -> set[str]:
    """
    Normalize file names.
    """

    normalized = set()

    for file_name in files:

        if not file_name:
            continue

        value = (
            str(file_name)
            .split("/")[-1]
            .split("\\")[-1]
            .strip()
            .lower()
        )

        if value:
            normalized.add(value)

    return normalized


def file_recall(
    retrieved_files: list[str],
    expected_files: list[str],
) -> float:
    """
    Calculate recall over expected files.
    """

    expected = normalize_files(
        expected_files
    )

    retrieved = normalize_files(
        retrieved_files
    )

    if not expected:
        return 0.0

    matched = expected.intersection(
        retrieved
    )

    return len(matched) / len(expected)


def file_precision(
    retrieved_files: list[str],
    expected_files: list[str],
) -> float:
    """
    Calculate precision over retrieved files.
    """

    expected = normalize_files(
        expected_files
    )

    retrieved = normalize_files(
        retrieved_files
    )

    if not retrieved:
        return 0.0

    matched = expected.intersection(
        retrieved
    )

    return len(matched) / len(retrieved)


def exact_file_match(
    selected_file: str,
    expected_files: list[str],
) -> bool:
    """
    Check whether the selected primary file
    is one of the expected files.
    """

    if not selected_file:
        return False

    selected = (
        str(selected_file)
        .split("/")[-1]
        .split("\\")[-1]
        .strip()
        .lower()
    )

    expected = normalize_files(
        expected_files
    )

    return selected in expected


def exact_file_set_match(
    predicted_files: list[str],
    expected_files: list[str],
) -> bool:
    """
    Check whether predicted and expected
    file sets are exactly identical.
    """

    predicted = normalize_files(
        predicted_files
    )

    expected = normalize_files(
        expected_files
    )

    return predicted == expected


def symbol_match(
    predicted_symbols: list[str],
    expected_symbols: list[str],
) -> bool:
    """
    Check whether at least one expected
    symbol was correctly identified.
    """

    expected = {
        str(symbol).strip().lower()
        for symbol in expected_symbols
        if symbol
    }

    predicted = {
        str(symbol).strip().lower()
        for symbol in predicted_symbols
        if symbol
    }

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
    Calculate symbol recall.
    """

    expected = {
        str(symbol).strip().lower()
        for symbol in expected_symbols
        if symbol
    }

    predicted = {
        str(symbol).strip().lower()
        for symbol in predicted_symbols
        if symbol
    }

    if not expected:
        return 0.0

    matched = expected.intersection(
        predicted
    )

    return len(matched) / len(expected)


def symbol_precision(
    predicted_symbols: list[str],
    expected_symbols: list[str],
) -> float:
    """
    Calculate symbol precision.
    """

    expected = {
        str(symbol).strip().lower()
        for symbol in expected_symbols
        if symbol
    }

    predicted = {
        str(symbol).strip().lower()
        for symbol in predicted_symbols
        if symbol
    }

    if not predicted:
        return 0.0

    matched = expected.intersection(
        predicted
    )

    return len(matched) / len(predicted)


def exact_symbol_match(
    predicted_symbols: list[str],
    expected_symbols: list[str],
) -> bool:
    """
    Check whether predicted and expected
    symbol sets are exactly identical.
    """

    predicted = {
        str(symbol).strip().lower()
        for symbol in predicted_symbols
        if symbol
    }

    expected = {
        str(symbol).strip().lower()
        for symbol in expected_symbols
        if symbol
    }

    return predicted == expected


def extract_symbols_from_context(
    context: str,
) -> list[str]:
    """
    Extract symbols from structured repository context.
    """

    symbols = []

    if not context:
        return symbols

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


# ==========================================================
# Relationship-Level Metrics
# ==========================================================


def normalize_relationships(
    relationships: list[str],
) -> set[str]:
    """
    Normalize relationship strings
    for reliable comparison.
    """

    normalized = set()

    for relationship in relationships:

        if not relationship:
            continue

        value = (
            " ".join(
                str(relationship)
                .strip()
                .lower()
                .split()
            )
        )

        if value:
            normalized.add(
                value
            )

    return normalized


def relationship_precision(
    predicted_relationships: list[str],
    expected_relationships: list[str],
) -> float:
    """
    Calculate relationship precision.

    Precision =
        correct predicted relationships /
        total predicted relationships
    """

    predicted = normalize_relationships(
        predicted_relationships
    )

    expected = normalize_relationships(
        expected_relationships
    )

    if not predicted:
        return 0.0

    matched = predicted.intersection(
        expected
    )

    return len(matched) / len(predicted)


def relationship_recall(
    predicted_relationships: list[str],
    expected_relationships: list[str],
) -> float:
    """
    Calculate relationship recall.

    Recall =
        correct predicted relationships /
        total expected relationships
    """

    predicted = normalize_relationships(
        predicted_relationships
    )

    expected = normalize_relationships(
        expected_relationships
    )

    if not expected:
        return 0.0

    matched = predicted.intersection(
        expected
    )

    return len(matched) / len(expected)


def relationship_f1(
    predicted_relationships: list[str],
    expected_relationships: list[str],
) -> float:
    """
    Calculate relationship F1 score.
    """

    precision = relationship_precision(
        predicted_relationships,
        expected_relationships,
    )

    recall = relationship_recall(
        predicted_relationships,
        expected_relationships,
    )

    if precision + recall == 0:
        return 0.0

    return (
        2
        * precision
        * recall
        / (precision + recall)
    )


def exact_relationship_match(
    predicted_relationships: list[str],
    expected_relationships: list[str],
) -> bool:
    """
    Return True only when predicted and
    expected relationship sets are identical.
    """

    predicted = normalize_relationships(
        predicted_relationships
    )

    expected = normalize_relationships(
        expected_relationships
    )

    return predicted == expected