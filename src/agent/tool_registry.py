from collections.abc import Callable


class ToolRegistry:
    """
    Registry for coding-agent tools.

    The registry allows tools to be registered,
    discovered, and executed by name.
    """

    def __init__(self):
        self.tools: dict[str, Callable] = {}

    def register(
        self,
        name: str,
        function: Callable,
    ) -> None:
        """
        Register a tool.
        """

        if name in self.tools:
            raise ValueError(
                f"Tool already registered: {name}"
            )

        self.tools[name] = function

    def execute(
        self,
        name: str,
        **kwargs,
    ):
        """
        Execute a registered tool.
        """

        if name not in self.tools:
            raise ValueError(
                f"Unknown tool: {name}"
            )

        tool = self.tools[name]

        return tool(**kwargs)

    def list_tools(self) -> list[str]:
        """
        Return registered tool names.
        """

        return list(
            self.tools.keys()
        )


if __name__ == "__main__":

    registry = ToolRegistry()

    def example_tool(
        message: str,
    ) -> dict:

        return {
            "message": message
        }

    registry.register(
        "example_tool",
        example_tool,
    )

    print("\nTOOL REGISTRY")
    print("=" * 70)

    print("\nRegistered tools:")

    for tool_name in (
        registry.list_tools()
    ):

        print(
            f"  - {tool_name}"
        )

    result = registry.execute(
        "example_tool",
        message="Tool executed successfully.",
    )

    print("\nResult:")
    print(result)