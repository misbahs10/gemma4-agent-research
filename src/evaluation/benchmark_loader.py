import json
from pathlib import Path


class BenchmarkLoader:
    """
    Load benchmark repositories and tasks.
    """

    def __init__(
        self,
        benchmark_root: str,
    ):
        self.benchmark_root = Path(
            benchmark_root
        )

    def load_tasks(self) -> list[dict]:
        """
        Load benchmark tasks.
        """

        task_file = (
            self.benchmark_root
            / "tasks"
            / "benchmark_tasks.json"
        )

        with task_file.open(
            "r",
            encoding="utf-8",
        ) as file:

            data = json.load(file)

        return data["tasks"]

    def load_repositories(self) -> list[dict]:
        """
        Load repository metadata.
        """

        repository_file = (
            self.benchmark_root
            / "metadata"
            / "repositories.json"
        )

        with repository_file.open(
            "r",
            encoding="utf-8",
        ) as file:

            data = json.load(file)

        return data["repositories"]

    def get_repository(
        self,
        repository_id: str,
    ) -> dict | None:
        """
        Find repository metadata by ID.
        """

        repositories = (
            self.load_repositories()
        )

        for repository in repositories:

            if (
                repository["repository_id"]
                == repository_id
            ):
                return repository

        return None

    def get_tasks_for_repository(
        self,
        repository_id: str,
    ) -> list[dict]:
        """
        Return all tasks belonging to a repository.
        """

        tasks = self.load_tasks()

        return [
            task
            for task in tasks
            if task["repository_id"]
            == repository_id
        ]


if __name__ == "__main__":

    project_root = (
        Path(__file__).resolve().parents[2]
    )

    benchmark_root = (
        project_root
        / "benchmark"
    )

    loader = BenchmarkLoader(
        str(benchmark_root)
    )

    repositories = (
        loader.load_repositories()
    )

    tasks = loader.load_tasks()

    print("\n")
    print("=" * 70)
    print("BENCHMARK")
    print("=" * 70)

    print(
        f"\nRepositories: "
        f"{len(repositories)}"
    )

    print(
        f"Tasks: "
        f"{len(tasks)}"
    )

    for repository in repositories:

        repository_id = (
            repository["repository_id"]
        )

        repository_tasks = (
            loader.get_tasks_for_repository(
                repository_id
            )
        )

        print(
            f"\nRepository: "
            f"{repository_id}"
        )

        print(
            f"Name: "
            f"{repository['name']}"
        )

        print(
            f"Tasks: "
            f"{len(repository_tasks)}"
        )

        for task in repository_tasks:

            print(
                f"  - "
                f"{task['task_id']}: "
                f"{task['task']}"
            )