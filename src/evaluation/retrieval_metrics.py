def precision_at_k(
    retrieved_files: list[str],
    relevant_files: list[str],
    k: int,
) -> float:
    """
    Calculate Precision@K.

    Precision@K =
    relevant retrieved files / K
    """

    retrieved = retrieved_files[:k]

    if not retrieved:
        return 0.0

    relevant_count = sum(
        1
        for file_name in retrieved
        if file_name in relevant_files
    )

    return relevant_count / len(retrieved)


def recall_at_k(
    retrieved_files: list[str],
    relevant_files: list[str],
    k: int,
) -> float:
    """
    Calculate Recall@K.

    Recall@K =
    relevant retrieved files / total relevant files
    """

    if not relevant_files:
        return 0.0

    retrieved = retrieved_files[:k]

    relevant_count = sum(
        1
        for file_name in retrieved
        if file_name in relevant_files
    )

    return relevant_count / len(
        relevant_files
    )


def mean_reciprocal_rank(
    retrieved_files: list[str],
    relevant_files: list[str],
) -> float:
    """
    Calculate Reciprocal Rank.

    Returns 1/rank of the first relevant result.
    """

    for rank, file_name in enumerate(
        retrieved_files,
        start=1,
    ):

        if file_name in relevant_files:
            return 1 / rank

    return 0.0


if __name__ == "__main__":

    retrieved = [
        "main.py",
        "calculator.py",
        "utils.py",
    ]

    relevant = [
        "calculator.py",
    ]

    print("\nRETRIEVAL METRICS")
    print("=" * 70)

    p_at_3 = precision_at_k(
        retrieved,
        relevant,
        3,
    )

    r_at_3 = recall_at_k(
        retrieved,
        relevant,
        3,
    )

    mrr = mean_reciprocal_rank(
        retrieved,
        relevant,
    )

    print(
        f"\nPrecision@3: {p_at_3:.4f}"
    )

    print(
        f"Recall@3: {r_at_3:.4f}"
    )

    print(
        f"MRR: {mrr:.4f}"
    )