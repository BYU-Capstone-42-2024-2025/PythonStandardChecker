import ast
from typing import NamedTuple, Any

class FunctionSummary(NamedTuple):
    function_name: str
    return_hint_missing: bool
    params_missing_hints: list[str]
    params_with_mutable_defaults: list[str]
    has_docstring: bool
    docstring: str

class ClassSummary(NamedTuple):
    class_name: str
    bases: list[str]
    func_summaries: list[FunctionSummary]
    has_docstring: bool
    docstring: str

def is_mutable_default(node:Any) -> bool:
    """Checks if default value is mutable (e.g., list, dict, set)."""
    return isinstance(node, (ast.List, ast.Dict, ast.Set))

def create_function_summary(node: ast.FunctionDef) -> FunctionSummary:
    """Checks for type hints, mutable defaults, and docstring presence in a function."""
    params_missing_hints =  [
        arg.arg for arg in node.args.args
        if (arg.arg not in {'self', 'cls'}) and (arg.annotation is None)
    ]
    return_hint_missing = node.returns is None
    mutable_defaults = [arg.arg for arg, default in zip(node.args.args, node.args.defaults) if is_mutable_default(default)]
    has_docstring = ast.get_docstring(node) is not None
    docstring = ast.get_docstring(node) if has_docstring else ''
    return FunctionSummary(node.name, return_hint_missing, params_missing_hints, mutable_defaults, has_docstring, docstring)

def create_class_summary(node: ast.ClassDef) -> ClassSummary:
    """Checks for bases, functions, and docstring presence in a class."""
    bases = [base.id for base in node.bases if isinstance(base, ast.Name)]
    functions = [create_function_summary(f) for f in node.body if isinstance(f, ast.FunctionDef)]
    has_docstring = ast.get_docstring(node) is not None
    docstring = ast.get_docstring(node) if has_docstring else ''
    return ClassSummary(node.name, bases, functions, has_docstring, docstring)

def identify_class_problems(class_sum: ClassSummary) -> list[str]:
    """Creates a list of problems with the class, if any."""
    problems = []
    class_name = class_sum.class_name
    if not class_sum.has_docstring:
        problems.append(f'Class {class_name} is missing a docstring.')
    for func_sum in class_sum.func_summaries:
        for func_problem in identify_func_problems(func_sum):
            problems.append(func_problem)
    return problems

def identify_func_problems(func_sum: FunctionSummary) -> list[str]:
    """Creates a list of problems with the function, if any."""
    problems = []
    func_name = func_sum.function_name
    for param in func_sum.params_missing_hints:
        problems.append(f'Function {func_name} needs type annotation for the parameter {param}.')
    for param in func_sum.params_with_mutable_defaults:
        problems.append(f'Function {func_name}\'s parameter {param} defaults to a mutable object.')
    if not func_sum.has_docstring:
        problems.append(f'Function {func_name} is missing a docstring.')
    return problems

def main(filename: str):
    """Checks the classes (and their functions) and the functions in a file."""
    with open(filename, 'r', encoding='utf-8') as file:
        tree = ast.parse(file.read())
    for node in tree.body:
        if isinstance(node, ast.ClassDef):
            class_sum = create_class_summary(node)
            class_problems = identify_class_problems(class_sum)
            print(class_problems)
            print()
        elif isinstance(node, ast.FunctionDef):
            func_sum = create_function_summary(node)
            func_problems = identify_func_problems(func_sum)
            print(func_problems)
            print()

# Specify the Python file to check
main("replacement.py")