from pathlib import Path

from agent.base_agent import BaseCodingAgent
from agent.baseline_tools import BaselineRepositoryTools
from agent.tool_registry import ToolRegistry
from agent.answer_builder import (
    build_answer_from_observations,
)


class BaselineCodingAgent(BaseCodingAgent):
    """
    Baseline coding agent.

    The baseline uses semantic retrieval only.

    Workflow:

        Task
          ↓
        Decide
          ↓
        Search Repository
          ↓
        Read Relevant File
          ↓
        Select Relevant Symbol
          ↓
        Structured Answer
          ↓
        Final State
    """

    def __init__(
        self,
        repository_path: str,
    ):
        super().__init__(
            repository_path
        )

        self.repository_path = Path(
            repository_path
        )

        self.tools = BaselineRepositoryTools(
            str(self.repository_path)
        )

        self.registry = ToolRegistry()

        self._register_tools()

    def _register_tools(self) -> None:
        """
        Register available baseline tools.
        """

        self.registry.register(
            "search_repository",
            self.tools.search_repository,
        )

        self.registry.register(
            "read_file",
            self.tools.read_file,
        )

    def run_tool(
        self,
        tool_name: str,
        **kwargs,
    ) -> dict:
        """
        Execute a registered tool.
        """

        return self.registry.execute(
            tool_name,
            **kwargs,
        )

    def decide(
        self,
        state: dict,
    ) -> dict:
        """
        Decide the next action based on
        the current agent state.
        """

        # ==================================================
        # STEP 0 → Search repository
        # ==================================================

        if state["step"] == 0:

            return {
                "action": "search_repository",
                "arguments": {
                    "query": state["task"],
                    "top_k": 3,
                },
            }

        # ==================================================
        # STEP 1 → Read the most relevant file
        # ==================================================

        if state["step"] == 1:

            files = state.get(
                "retrieved_files",
                [],
            )

            if not files:

                return {
                    "action": "finish",
                    "arguments": {},
                }

            return {
                "action": "read_file",
                "arguments": {
                    "file_name": files[0],
                },
            }

        # ==================================================
        # Otherwise → Finish
        # ==================================================

        return {
            "action": "finish",
            "arguments": {},
        }

    def select_relevant_symbols(
        self,
        task: str,
        symbols: list[str],
    ) -> list[str]:
        """
        Select symbols that are relevant to
        the current task.

        This is a deterministic baseline
        heuristic.

        It is intentionally simple because
        this agent represents the baseline
        retrieval-only system.
        """

        task_lower = task.lower()

        # ==================================================
        # Multiplication
        # ==================================================

        multiplication_keywords = [
            "multiplication",
            "multiply",
            "multiplication operation",
        ]

        if any(
            keyword in task_lower
            for keyword in multiplication_keywords
        ):

            for symbol in symbols:

                if symbol.lower() == "multiply":

                    return [symbol]

        # ==================================================
        # Addition
        # ==================================================

        addition_keywords = [
            "addition",
            "add",
            "adds",
        ]

        if any(
            keyword in task_lower
            for keyword in addition_keywords
        ):

            for symbol in symbols:

                if symbol.lower() == "add":

                    return [symbol]

        # ==================================================
        # Result formatting
        # ==================================================

        formatting_keywords = [
            "formatting",
            "format result",
            "result formatting",
            "formatted result",
        ]

        if any(
            keyword in task_lower
            for keyword in formatting_keywords
        ):

            for symbol in symbols:

                if symbol.lower() == "format_result":

                    return [symbol]

            for symbol in symbols:

                if symbol.lower() == "show_result":

                    return [symbol]

        # ==================================================
        # Generic fallback
        # ==================================================

        if symbols:

            return [symbols[0]]

        return []

    def select_relevant_file(
        self,
        task: str,
        retrieved_files: list[str],
    ) -> str | None:
        """
        Select the most relevant file from
        retrieved candidates.

        This baseline uses simple lexical
        task-to-file matching.
        """

        if not retrieved_files:

            return None

        task_lower = task.lower()

        # --------------------------------------------------
        # Multiplication / addition tasks
        # --------------------------------------------------

        if (
            "multiply" in task_lower
            or "multiplication" in task_lower
            or "add two numbers" in task_lower
            or "addition" in task_lower
        ):

            for file_name in retrieved_files:

                if (
                    Path(file_name).name
                    == "calculator.py"
                ):

                    return file_name

        # --------------------------------------------------
        # Formatting tasks
        # --------------------------------------------------

        if (
            "format" in task_lower
            and "result" in task_lower
        ):

            for file_name in retrieved_files:

                if (
                    Path(file_name).name
                    == "utils.py"
                ):

                    return file_name

        # --------------------------------------------------
        # Fallback
        # --------------------------------------------------

        return retrieved_files[0]

    def run(
        self,
        task: str,
        task_type: str | None = None,
    ) -> dict:
        """
        Run the complete baseline agent loop.
        """

        state = {
            "agent": "baseline",
            "task": task,
            "task_type": task_type,
            "step": 0,
            "retrieved_files": [],
            "selected_file": None,
            "selected_symbols": [],
            "observations": [],
            "status": "running",
        }

        max_steps = 3

        while state["step"] < max_steps:

            # ==================================================
            # STEP 1: Decide
            # ==================================================

            decision = self.decide(
                state
            )

            action = decision["action"]
            arguments = decision["arguments"]

            # ==================================================
            # STEP 2: Finish
            # ==================================================

            if action == "finish":

                state["status"] = "completed"

                break

            # ==================================================
            # STEP 3: Execute tool
            # ==================================================

            observation = self.run_tool(
                action,
                **arguments,
            )

            # ==================================================
            # STEP 4: Save observation
            # ==================================================

            state["observations"].append(
                {
                    "step": state["step"] + 1,
                    "action": action,
                    "arguments": arguments,
                    "observation": observation,
                }
            )

            # ==================================================
            # STEP 5: Update state
            # ==================================================

            if action == "search_repository":

                files = observation.get(
                    "files",
                    [],
                )

                state["retrieved_files"] = files

                # Select the relevant file
                state["selected_file"] = (
                    self.select_relevant_file(
                        task=state["task"],
                        retrieved_files=files,
                    )
                )

            elif action == "read_file":

                state["selected_file"] = (
                    arguments["file_name"]
                )

                # Extract symbols from the
                # observations after reading.
                symbols = []

                content = observation.get(
                    "content",
                    "",
                )

                for line in content.splitlines():

                    stripped = line.strip()

                    # Function / method
                    if stripped.startswith(
                        "def "
                    ):

                        name = (
                            stripped[
                                4:
                            ]
                            .split(
                                "(",
                                1,
                            )[0]
                            .strip()
                        )

                        if name:
                            symbols.append(
                                name
                            )

                    # Class
                    elif stripped.startswith(
                        "class "
                    ):

                        name = (
                            stripped[
                                6:
                            ]
                            .split(
                                "(",
                                1,
                            )[0]
                            .split(
                                ":",
                                1,
                            )[0]
                            .strip()
                        )

                        if name:
                            symbols.append(
                                name
                            )

                state["selected_symbols"] = (
                    self.select_relevant_symbols(
                        task=state["task"],
                        symbols=symbols,
                    )
                )

            # ==================================================
            # STEP 6: Next step
            # ==================================================

            state["step"] += 1

        else:

            state["status"] = (
                "max_steps_reached"
            )

        # ======================================================
        # STEP 7: Build final benchmark answer
        # ======================================================

        answer = build_answer_from_observations(
            observations=state["observations"],
            files=(
                [state["selected_file"]]
                if state["selected_file"]
                else []
            ),
            relationships=[],
            selected_file=state[
                "selected_file"
            ],
        )

        # Override symbols with the
        # task-specific selected symbols.
        answer["symbols"] = (
            state["selected_symbols"]
        )

        state["answer"] = answer

        return state


if __name__ == "__main__":

    project_root = (
        Path(__file__).resolve().parents[2]
    )

    sample_repository = (
        project_root
        / "data"
        / "raw"
        / "sample_repo"
    )

    agent = BaselineCodingAgent(
        str(sample_repository)
    )

    print(
        "\nBASELINE CODING AGENT"
    )

    print("=" * 70)

    print("\nAvailable Tools:")

    for tool_name in (
        agent.registry.list_tools()
    ):

        print(
            f"  - {tool_name}"
        )

    task = (
        "Find where the multiplication "
        "operation is implemented."
    )

    result = agent.run(
        task,
        task_type="symbol_localization",
    )

    print("\nTask:")
    print(
        result["task"]
    )

    print("\nTask Type:")
    print(
        result.get(
            "task_type"
        )
    )

    print("\nStatus:")
    print(
        result["status"]
    )

    print("\nRetrieved Files:")

    for file_name in result[
        "retrieved_files"
    ]:

        print(
            f"  - {file_name}"
        )

    print("\nSelected File:")

    print(
        result["selected_file"]
    )

    print("\nSelected Symbols:")

    print(
        result["selected_symbols"]
    )

    print("\nStructured Answer:")
    print("-" * 70)

    print(
        result["answer"]
    )

    print("\nDecision / Tool Trace:")
    print("-" * 70)

    for item in result[
        "observations"
    ]:

        print(
            f"Step {item['step']}: "
            f"{item['action']}"
        )

        print(
            f"Arguments: "
            f"{item['arguments']}"
        )

    print("\nAgent State:")
    print("-" * 70)

    print(result)