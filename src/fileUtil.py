import os
from typing import Dict

import tempfile

async def combine_files(tree_string : str, path_dictionary: Dict[int, str]):
    """
    Combines multiple files from a dictionary into a single output file.

    For each file in the map, it writes a header with the key and path,
    followed by the full content of that file.

    Args:
        path_dictionary: A dictionary where keys are unique identifiers (e.g., int)
                  and values are the absolute paths to the files to combine.
        output_file_path: The path for the final combined text file.
    """
    temp_dir = tempfile.mkdtemp()
    output_file_path = os.path.join(temp_dir, "combined_project_code.txt")

    print(f"🚀 Starting to combine files into '{output_file_path}'...")

    try:
        with open(output_file_path, 'w', encoding='utf-8') as outfile:
            outfile.write("---Arborescence of the project---\n")
            outfile.write(tree_string + "\n")

            # Sort by key to ensure a consistent order
            sorted_files = sorted(path_dictionary.items())

            for file_id, file_path in sorted_files:
                # --- Create a clear header for each file ---
                header = f"\n{'=' * 40}\n--- FILE: [{file_id}] | PATH: {file_path} ---\n{'=' * 40}\n\n"
                outfile.write(header)

                try:
                    # --- Read the content of the source file and write it ---
                    with open(file_path, 'r', encoding='utf-8') as infile:
                        content = infile.read()
                        outfile.write(content)
                    print(f"  ✅ Added file [{file_id}]: {os.path.basename(file_path)}")

                except FileNotFoundError:
                    error_message = f"*** ERROR: File not found at path: {file_path} ***\n"
                    outfile.write(error_message)
                    print(f"  ❌ Error: File not found for ID {file_id} at {file_path}")
                except Exception as e:
                    error_message = f"*** ERROR: Could not read file. Reason: {e} ***\n"
                    outfile.write(error_message)
                    print(f"  ❌ Error: Could not read file for ID {file_id}. Reason: {e}")

        print(f"\n🎉 Successfully created the combined file: {output_file_path}")

    except IOError as e:
        print(f"🔥 Critical Error: Could not write to output file '{output_file_path}'. Reason: {e}")
    return {"output_file_path" : output_file_path, "path_dictionary" : path_dictionary}


if __name__ == '__main__':
    # --- Example Usage ---

    # 1. Create a dummy project structure for demonstration
    if not os.path.exists('temp_project'):
        os.makedirs('temp_project/utils')

    with open('temp_project/main.py', 'w') as f:
        f.write('def main():\n    print("Hello from main!")\n')

    with open('temp_project/utils/helpers.py', 'w') as f:
        f.write('def helper_function():\n    return "This is a helper."\n')

    with open('temp_project/README.md', 'w') as f:
        f.write('# My Project\n\nThis is a test project.')

    # 2. This is the kind of dictionary your other script would generate.
    # We are creating it manually here for the example.
    example_file_map = {
        1: os.path.abspath('temp_project/main.py'),
        2: os.path.abspath('temp_project/utils/helpers.py'),
        3: os.path.abspath('temp_project/non_existent_file.py')  # Example of a missing file
    }

    # 3. Define the name of the output file.
    combined_output_file = "combined_project_code.txt"

    # 4. Run the function.
    combine_files(example_file_map, combined_output_file)

    print(f"\nCheck the file '{combined_output_file}' to see the result.")