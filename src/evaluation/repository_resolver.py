from pathlib import Path


class RepositoryResolver:
    """
    Resolve benchmark repository IDs
    to local repository paths.
    """

    def __init__(
        self,
        project_root: str,
        repositories: list[dict],
    ):
        self.project_root = Path(
            project_root
        )

        self.repositories = {
            repository["repository_id"]: repository
            for repository in repositories
        }

    def resolve(
        self,
        repository_id: str,
    ) -> Path:
        """
        Return the local path for a repository.
        """

        if repository_id not in self.repositories:
            raise ValueError(
                f"Unknown repository: "
                f"{repository_id}"
            )

        repository = (
            self.repositories[
                repository_id
            ]
        )

        relative_path = Path(
            repository["path"]
        )

        repository_path = (
            self.project_root
            / relative_path
        ).resolve()

        if not repository_path.exists():
            raise FileNotFoundError(
                f"Repository does not exist: "
                f"{repository_path}"
            )

        if not repository_path.is_dir():
            raise NotADirectoryError(
                f"Repository path is not a "
                f"directory: {repository_path}"
            )

        return repository_path


if __name__ == "__main__":

    project_root = (
        Path(__file__).resolve().parents[2]
    )

    from evaluation.benchmark_loader import (
        BenchmarkLoader,
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

    resolver = RepositoryResolver(
        str(project_root),
        repositories,
    )

    path = resolver.resolve(
        "repo001"
    )

    print(
        f"Repository path:\n{path}"
    )