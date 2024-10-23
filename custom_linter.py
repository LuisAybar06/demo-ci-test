import os
import ast
import re
import sys
import nbformat
from nbconvert import PythonExporter
from radon.complexity import cc_visit


def convert_noteboock_to_scrpit(noteboock_path):
    with open(noteboock_path, "r", encoding="utf-8") as f:
        notebook_content = nbformat.read(f, as_version=4)

    exporter = PythonExporter()
    script, _ = exporter.from_notebook_node(notebook_content)

    return script



def check_long_functions(file_content, file_path, max_line=5):
    print(f"checking file: {file_path}")
    errors = 0
    tree = ast.parse(file_content)

    functions = [node for node in ast.walk(tree) if isinstance(node, ast.FunctionDef)]

    for func in functions:
        lines = len(func.body)
        if lines > max_line:
            print(f"{file_path}: Function '{func.name}' has {lines} lines, whit exceedes the threshold of {max_line}")
            errors += 1
    return errors





def lint_file(file_path, max_line_lenght):
    error = 0
    if file_path.endswith('.ipynb'):
        file_content = convert_noteboock_to_scrpit(file_path)
    else:
        with open(file_path, "r", encoding="utf-8") as file:
            file_content = file.read()

    error += check_long_functions(file_content, file_path, max_line_lenght)

    return error


def lint_directory(directory, max_line_lenght):
    total_errors = 0
    for root, _, files in os.walk(directory):
        for file in files:
            if file.endswith(".ipynb"):
                file_path = os.path.join(root, file)
                total_errors += lint_file(file_path, max_line_lenght)
    return total_errors


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Custom Linter")
    parser.add_argument("directories", nargs='+', help="Directories to lint")
    parser.add_argument("--max-line-lenght", type=int, default=88)

    args = parser.parse_args()

    total_errors = 0

    for directory in args.directories:
        total_errors += lint_directory(directory, args.max_line_lenght)

    if total_errors > 0:
        sys.exit(1)
    else:
        sys.exit(0)
