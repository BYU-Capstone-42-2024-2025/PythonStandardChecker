import os
import re
import ast
from typing import NamedTuple, Any
from functools import lru_cache

class FunctionSummary(NamedTuple):
    """Represents details of a function's adherence to standards."""
    function_name: str
    return_hint_missing: bool
    params_missing_hints: list[str]
    params_with_mutable_defaults: list[str]
    has_docstring: bool
    docstring: str

class ClassSummary(NamedTuple):
    """Represents details of a class's adherence to standards."""
    class_name: str
    func_summaries: list[FunctionSummary]
    has_docstring: bool
    docstring: str

    def Random(sjd:str):
        pass

def is_mutable_default(node:Any) -> bool:
    """Checks if default value is mutable (e.g., list, dict, set)."""
    return isinstance(node, (ast.List, ast.Dict, ast.Set))

def create_function_summary(node:ast.FunctionDef) -> FunctionSummary:
    """Creates a summary of a class's adherence to standards, including all said class's methods, if any."""
    params_missing_hints =  [
        arg.arg for arg in node.args.args
        if (arg.arg not in {'self', 'cls', '*args', '**kwargs'}) and (arg.annotation is None)
    ]
    return_hint_missing = node.returns is None
    mutable_defaults = [arg.arg for arg, default in zip(node.args.args, node.args.defaults) if is_mutable_default(default)]
    has_docstring = ast.get_docstring(node) is not None
    docstring = ast.get_docstring(node) if has_docstring else ''
    return FunctionSummary(node.name, return_hint_missing, params_missing_hints, mutable_defaults, has_docstring, docstring)

def create_class_summary(node: ast.ClassDef) -> ClassSummary:
    """Creates a summary of a class's adherence to standards, including all said class's methods, if any."""
    functions = [create_function_summary(f) for f in node.body if isinstance(f, ast.FunctionDef)]
    has_docstring = ast.get_docstring(node) is not None
    docstring = ast.get_docstring(node) if has_docstring else ''
    return ClassSummary(node.name, functions, has_docstring, docstring)

def identify_class_problems(class_sum: ClassSummary) -> list[str]:
    """Creates a list of problems with the class, if any."""
    problems = []
    class_name = class_sum.class_name
    if not class_sum.has_docstring:
        problems.append(f'Class {class_name} is missing a docstring.')
    if not is_valid_format(class_name, is_class=True):
        problems.append(f'Class {class_name}\' name is not in a valid format. Please use Pascal case when possible, or, if an exception is needed, add to .standardignore')
    # TODO
    # if not 
    # if NAME_MANGLE in node.name and node.name not in self.special_methods and node.name not in self.itemsToIgnore:
    #         self.errors.append(self.toString(node, f"Function '{node.name}' uses '{NAME_MANGLE}' inappropriately."))
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
    if not is_valid_format(func_name):
        problems.append(f'Function {func_name}\' name is not in a valid format. Please use snake case when possible, or, if an exception is needed, add to .standardignore')
    return problems

@lru_cache
def load_items_to_ignore(ignoreFile:str) -> list[str]:
    """Loads the items to ignore from an ignore file, cached."""
    if not os.path.exists(ignoreFile):
        return []
    ignoreItems = []
    ignoreSymbol = '!'
    with open(ignoreFile, 'r', encoding='utf-8') as file:
        ignoreItems = [line.strip().strip(ignoreSymbol) for line in file if line.strip() and line.startswith(ignoreSymbol)]
    return ignoreItems

def is_valid_format(name: str, is_class:bool = False) -> bool:
    """Check if a name is in snake_case or other valid format."""
    if name in load_items_to_ignore('.standardignore'):
        return True
    if name.isupper():
        return True
    if name.startswith('_'):
        return True
    if is_class:
        return isPascalCase(name)
    return isSnakeCase(name)

def isPascalCase(name: str) -> bool:
    """Checks if a name is in pascal case."""
    return re.match(r'^[A-Z][A-Za-z0-9]+(?:[A-Z][a-z0-9]*)*$', name) is not None

def isSnakeCase(name: str) -> bool:
    """Checks if a name is in snake case."""        
    if "_" in name:
        parts = name.split("_")
        if any(not part.islower() for part in parts if part):
            return False
        if "__" in name:
            return False
        return True
    return name.islower() and name.isalnum()

def check_file(filename: str) -> list[str]:
    """Checks the classes (and their functions) and the functions in a file."""
    # Set up
    with open(filename, 'r', encoding='utf-8') as file:
        tree = ast.parse(file.read())
    fileProblems:list[str] = []
    
    # Check all classes
    for node in tree.body:
        if not isinstance(node, ast.ClassDef):
            continue
        class_sum = create_class_summary(node)
        class_problems = identify_class_problems(class_sum)
        if not class_problems:
            continue
        fileProblems.append('\n\t'.join([f'Class {class_sum.class_name} on line {node.lineno}:'] + class_problems))

    # Check all functions
    for node in tree.body:
        if not isinstance(node, ast.FunctionDef):
            continue
        func_sum = create_function_summary(node)
        func_problems = identify_func_problems(func_sum)
        if not func_problems:
            continue
        fileProblems.append('\n\t'.join([f'Function {func_sum.function_name} on line {node.lineno}:'] + class_problems))

    # Check all variables
    for node in ast.walk(tree):
        if not isinstance(node, ast.Assign):
            continue
        for target in node.targets:
            if not isinstance(target, ast.Name):
                continue
            if is_valid_format(target.id):
                continue
            fileProblems.append(f'Variable {target.id} on line {node.lineno} is not valid. Please change to snake case, or, if an exception is needed, add to .standardignore')
    return fileProblems
    

# Specify the Python file to check
errors = check_file("replacement.py")
for err in errors:
    print(err)