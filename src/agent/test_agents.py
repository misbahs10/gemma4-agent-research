from pathlib import Path

from agent.baseline_agent import (
    BaselineCodingAgent,
)

from agent.graph_agent import (
    GraphAugmentedCodingAgent,
)


def run_agent_test(agent, task: str) -> None:

    print("\n")
    print("=" * 70)

    print(
        f"AGENT: {agent.__class__.__name__}"
    )

    print("=" * 70)

    result = agent.run(task)

    print("\nStatus:")
    print(result.get("status"))

    print("\nTask:")
    print(result.get("task"))

    print("\nResult:")

    if "selected_file" in result:
        print(
            f"Selected File: "
            f"{result['selected_file']}"
        )

    if "primary_file" in result:
        print(
            f"Primary File: "
            f"{result['primary_file']}"
        )

    if "retrieved_files" in result:
        print(
            "Retrieved Files:"
        )

        for file_name in result[
            "retrieved_files"
        ]:
            print(
                f"  - {file_name}"
            )

    if "graph_dependencies" in result:
        print(
            "\nGraph Dependencies:"
        )

        for dependency in result[
            "graph_dependencies"
        ]:
            print(
                f"  - {dependency['name']}"
            )


if __name__ == "__main__":

    project_root = (
        Path(__file__).resolve().parents[2]
    )

    repository = (
        project_root
        / "data"
        / "raw"
        / "sample_repo"
    )

    task = (
        "Find where the multiplication "
        "operation is implemented."
    )

    baseline_agent = BaselineCodingAgent(
        str(repository)
    )

    graph_agent = GraphAugmentedCodingAgent(
        str(repository)
    )

    run_agent_test(
        baseline_agent,
        task,
    )

    run_agent_test(
        graph_agent,
        task,
    )