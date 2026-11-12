from abc import ABC, abstractmethod


class BaseCodingAgent(ABC):
    """
    Common interface for coding agents.

    Every coding agent must implement run().
    """

    def __init__(self, repository_path: str):
        self.repository_path = repository_path

    @abstractmethod
    def run(self, task: str) -> dict:
        """
        Execute a coding task.

        Parameters
        ----------
        task : str
            Repository-level software engineering task.

        Returns
        -------
        dict
            Agent execution result.
        """
        raise NotImplementedError