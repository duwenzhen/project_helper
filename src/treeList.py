import os
import ast
import sys
from typing import Dict, List, Tuple


def generate_tree_with_functions(start_path: str) -> Tuple[str, Dict[int, str]]:
    """
    Generates a directory tree, numbers Python files, and returns the
    tree as a string and a dictionary mapping numbers to file paths.

    Args:
        start_path: The root directory to start scanning from.

    Returns:
        A tuple containing:
        - The entire directory tree as a single formatted string.
        - A dictionary mapping unique file IDs to their absolute paths.
    """
    if not os.path.isdir(start_path):
        error_msg = f"Error: Provided path '{start_path}' is not a directory."
        return error_msg, {}

    abs_path = os.path.abspath(start_path)

    # Initialize state keepers
    file_counter = [0]  # Use a list for mutable integer across calls
    file_map = {}

    # Generate the tree lines recursively
    tree_lines = [f"🌳 {os.path.basename(abs_path)}/"]
    tree_lines.extend(_walk_dir(abs_path, "", file_counter, file_map))

    # Join lines into a single string and return with the map
    return "\n".join(tree_lines), file_map


def _list_py_contents(file_path: str, base_prefix: str = "") -> List[str]:
    """
    Parses a Python file and returns a list of strings representing its contents.
    """
    lines = []
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            source = f.read()
        tree = ast.parse(source)
    except (SyntaxError, UnicodeDecodeError, FileNotFoundError):
        lines.append(f"{base_prefix}└── [Could not parse file]")
        return lines

    definitions = [node for node in tree.body if isinstance(node, (ast.FunctionDef, ast.ClassDef))]

    for i, node in enumerate(definitions):
        is_last_def = (i == len(definitions) - 1)
        connector = "└── " if is_last_def else "├── "

        if isinstance(node, ast.FunctionDef):
            lines.append(f"{base_prefix}{connector}𝑓 {node.name}()")

        elif isinstance(node, ast.ClassDef):
            lines.append(f"{base_prefix}{connector}𝐂 {node.name}")

            method_prefix = base_prefix + ("    " if is_last_def else "│   ")
            methods = [m for m in node.body if isinstance(m, ast.FunctionDef)]

            for j, method in enumerate(methods):
                is_last_method = (j == len(methods) - 1)
                method_connector = "└── " if is_last_method else "├── "
                lines.append(f"{method_prefix}{method_connector}𝑓 {method.name}()")
    return lines


def _walk_dir(current_path: str, prefix: str, file_counter: List[int], file_map: Dict[int, str]) -> List[str]:
    """
    Recursively walks a directory, returning its structure as a list of strings.
    """
    dir_lines = []
    try:
        entries = sorted([e for e in os.listdir(current_path) if not e.startswith('.')])
    except PermissionError:
        dir_lines.append(f"{prefix}└── [Permission Denied]")
        return dir_lines

    for i, entry in enumerate(entries):
        is_last = (i == len(entries) - 1)
        connector = "└── " if is_last else "├── "

        path = os.path.join(current_path, entry)
        child_prefix = prefix + ("    " if is_last else "│   ")

        if entry.endswith('.py'):
            file_counter[0] += 1
            file_id = file_counter[0]
            file_map[file_id] = path

            dir_lines.append(f"{prefix}{connector}[{file_id}] {entry}")
            dir_lines.extend(_list_py_contents(path, child_prefix))

        elif os.path.isdir(path):
            dir_lines.append(f"{prefix}{connector}{entry}/")
            dir_lines.extend(_walk_dir(path, child_prefix, file_counter, file_map))
        else:
            dir_lines.append(f"{prefix}{connector}{entry}")

    return dir_lines


if __name__ == "__main__":
    target_path = r'C:\Users\Wenzhen\PyCharmProject'
    if len(sys.argv) > 1:
        target_path = sys.argv[1]

    # Unpack the returned tuple
    tree_string, path_dictionary = generate_tree_with_functions(target_path)

    print("--- Project Structure ---")
    print(tree_string)  # Print the returned string

    print("\n" + "=" * 40)
    print("--- Generated File Map ---")
    if path_dictionary:
        for file_id, file_path in path_dictionary.items():
            print(f"  {file_id}: {file_path}")
    else:
        print("  No Python files were found.")
    print("=" * 40)