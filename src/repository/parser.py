import ast
from pathlib import Path


class PythonParser:
    """
    Parse Python source files using Python AST
    and extract structural information.
    """

    def __init__(self, file_path: str):
        self.file_path = Path(file_path)

    def parse(self) -> ast.AST:
        """Convert Python source code into an AST."""

        source_code = self.file_path.read_text(
            encoding="utf-8"
        )

        return ast.parse(
            source_code,
            filename=str(self.file_path),
        )

    def extract_imports(
        self,
        tree: ast.AST,
    ) -> list[str]:
        """Extract imported modules and symbols."""

        imports = []

        for node in ast.walk(tree):

            if isinstance(node, ast.Import):

                for alias in node.names:
                    imports.append(alias.name)

            elif isinstance(node, ast.ImportFrom):

                module = node.module or ""

                for alias in node.names:

                    if module:
                        imports.append(
                            f"{module}.{alias.name}"
                        )
                    else:
                        imports.append(
                            alias.name
                        )

        return imports

    def extract_functions(
        self,
        tree: ast.AST,
    ) -> list[dict]:
        """
        Extract top-level functions and
        class methods.
        """

        functions = []

        class FunctionVisitor(ast.NodeVisitor):

            def __init__(self):
                self.current_class = None

            def visit_ClassDef(self, node):

                previous_class = self.current_class

                self.current_class = node.name

                self.generic_visit(node)

                self.current_class = previous_class

            def visit_FunctionDef(self, node):

                functions.append(
                    {
                        "name": node.name,
                        "type": (
                            "method"
                            if self.current_class
                            else "function"
                        ),
                        "class": self.current_class,
                    }
                )

                self.generic_visit(node)

            def visit_AsyncFunctionDef(self, node):

                functions.append(
                    {
                        "name": node.name,
                        "type": (
                            "method"
                            if self.current_class
                            else "function"
                        ),
                        "class": self.current_class,
                    }
                )

                self.generic_visit(node)

        visitor = FunctionVisitor()

        visitor.visit(tree)

        return functions

    def extract_classes(
        self,
        tree: ast.AST,
    ) -> list[str]:
        """Extract class names."""

        classes = []

        for node in ast.walk(tree):

            if isinstance(node, ast.ClassDef):

                classes.append(node.name)

        return classes

    def extract_calls(
        self,
        tree: ast.AST,
    ) -> list[dict]:
        """
        Extract function and method calls.
        """

        calls = []

        class CallVisitor(ast.NodeVisitor):

            def __init__(self):
                self.current_function = None
                self.current_class = None

            def visit_FunctionDef(self, node):

                previous_function = (
                    self.current_function
                )

                self.current_function = node.name

                self.generic_visit(node)

                self.current_function = (
                    previous_function
                )

            def visit_AsyncFunctionDef(
                self,
                node,
            ):

                previous_function = (
                    self.current_function
                )

                self.current_function = node.name

                self.generic_visit(node)

                self.current_function = (
                    previous_function
                )

            def visit_ClassDef(self, node):

                previous_class = self.current_class

                self.current_class = node.name

                self.generic_visit(node)

                self.current_class = (
                    previous_class
                )

            def visit_Call(self, node):

                call_name = None
                object_name = None

                if isinstance(
                    node.func,
                    ast.Name,
                ):

                    call_name = node.func.id

                elif isinstance(
                    node.func,
                    ast.Attribute,
                ):

                    call_name = node.func.attr

                    if isinstance(
                        node.func.value,
                        ast.Name,
                    ):

                        object_name = (
                            node.func.value.id
                        )

                if call_name:

                    calls.append(
                        {
                            "caller": (
                                self.current_function
                            ),
                            "caller_class": (
                                self.current_class
                            ),
                            "callee": call_name,
                            "object": object_name,
                        }
                    )

                self.generic_visit(node)

        visitor = CallVisitor()

        visitor.visit(tree)

        return calls

    def extract_object_types(
        self,
        tree: ast.AST,
    ) -> list[dict]:
        """
        Detect simple object instantiations.

        Example:

            calculator = Calculator()

        Produces:

            calculator -> Calculator
        """

        object_types = []

        class ObjectTypeVisitor(
            ast.NodeVisitor
        ):

            def visit_Assign(self, node):

                if not isinstance(
                    node.value,
                    ast.Call,
                ):
                    self.generic_visit(node)
                    return

                if not isinstance(
                    node.value.func,
                    ast.Name,
                ):
                    self.generic_visit(node)
                    return

                class_name = node.value.func.id

                for target in node.targets:

                    if isinstance(
                        target,
                        ast.Name,
                    ):

                        object_types.append(
                            {
                                "object": target.id,
                                "type": class_name,
                            }
                        )

                self.generic_visit(node)

        visitor = ObjectTypeVisitor()

        visitor.visit(tree)

        return object_types

    def analyze(self) -> dict:
        """Perform complete AST analysis."""

        tree = self.parse()

        return {
            "file": str(self.file_path),
            "imports": self.extract_imports(tree),
            "functions": self.extract_functions(tree),
            "classes": self.extract_classes(tree),
            "calls": self.extract_calls(tree),
            "object_types": self.extract_object_types(
                tree
            ),
        }


if __name__ == "__main__":

    project_root = (
        Path(__file__).resolve().parents[2]
    )

    sample_file = (
        project_root
        / "data"
        / "raw"
        / "sample_repo"
        / "main.py"
    )

    parser = PythonParser(
        str(sample_file)
    )

    result = parser.analyze()

    print("\nAST Analysis")
    print("=" * 60)

    print(
        f"File: {result['file']}"
    )

    print("\nImports:")

    for item in result["imports"]:
        print(f"  - {item}")

    print("\nFunctions / Methods:")

    for item in result["functions"]:

        print(
            f"  - {item['name']} "
            f"[{item['type']}]"
        )

        if item["class"]:
            print(
                f"    Class: {item['class']}"
            )

    print("\nClasses:")

    for item in result["classes"]:
        print(f"  - {item}")

    print("\nCalls:")

    for item in result["calls"]:

        if item["object"]:

            print(
                f"  - "
                f"{item['caller']} "
                f"-> "
                f"{item['object']}."
                f"{item['callee']}"
            )

        else:

            print(
                f"  - "
                f"{item['caller']} "
                f"-> "
                f"{item['callee']}"
            )

    print("\nObject Types:")

    for item in result["object_types"]:

        print(
            f"  - "
            f"{item['object']} "
            f"-> "
            f"{item['type']}"
        )