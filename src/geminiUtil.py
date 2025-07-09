from google import genai
from google.genai import types
import wave
import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()
api_key = os.environ["GEMINI_API_KEY"]
client = genai.Client(api_key=api_key)


async def create_unit_tests(context_file: str, path_file: str) -> str:
    """
    Generates unit tests for a given Python file using the Gemini API.

    This function reads the content of a Python file, combines it with user-provided
    context, and sends it to the Gemini model to generate a suite of unit tests
    using the pytest framework.

    Args:
        context_file: context file, contains all the context for creating unit tests
        path_file: The absolute or relative path to the Python file that needs
                   unit tests.

    Returns:
        A string containing the generated Python code for the unit tests.
        If an error occurs (e.g., file not found, API error), a descriptive
        error message string is returned instead.
    """
    # --- 1. Read the source code file ---
    try:
        with open(path_file, 'r', encoding='utf-8') as f:
            file_content = f.read()
    except FileNotFoundError:
        return f"Error: The file at '{path_file}' was not found."
    except Exception as e:
        return f"Error reading file '{path_file}': {e}"

    try:
        with open(context_file, 'r', encoding='utf-8') as f:
            context = f.read()
    except FileNotFoundError:
        return f"Error: The file at '{context_file}' was not found."
    except Exception as e:
        return f"Error reading file '{context_file}': {e}"


    # --- 3. Construct a detailed prompt for the model ---
    prompt = f"""
    You are an expert quantitative developer specializing in writing high-quality, robust unit tests in Python using the pytest framework.

    Your task is to generate a complete suite of unit tests for the following Python code.

    **User-provided context for test generation:**
    {context}

    **Python code to test:**
    ```python
    # File: {path_file}
    {file_content}
    ```

    **Instructions for generating tests:**
    1.  Create comprehensive unit tests that cover all functions, methods, and classes in the provided code.
    2.  Include tests for typical use cases (happy path), edge cases (e.g., zero, empty inputs, large numbers), and potential error conditions.
    3.  Use the `pytest` framework for structuring the tests.
    4.  Employ `pytest` fixtures (`@pytest.fixture`) for any necessary setup or test data to avoid code repetition.
    5.  Add clear, concise comments explaining the purpose of each test function or fixture.
    6.  The entire output should be a single, complete Python code block containing only the test code.
    7.  Do not include the original source code in your response.
    8.  Do not use too much mock, and run the test, make sure it passes before include it in the test set
    9.  Ensure the output is raw code, not wrapped in Markdown backticks (```python ... ```).
    """

    # --- 4. Call the API and handle the response ---
    try:
        response = client.models.generate_content(
            model="gemini-2.5-flash",
            contents=prompt,
            config=types.GenerateContentConfig(
                temperature=0,
            ),
        )

        # The generated code is typically in response.text
        if response.text:
            # Clean up the response to remove potential markdown formatting
            generated_code = response.text.strip()
            if generated_code.startswith("```python"):
                generated_code = generated_code[9:]
            if generated_code.endswith("```"):
                generated_code = generated_code[:-3]
            return generated_code.strip()
        else:
            # This can happen if the prompt is flagged by safety filters
            return "Error: Failed to generate tests. The API response was empty."

    except Exception as e:
        return f"An error occurred while communicating with the Gemini API: {e}"


async def add_comments(context_file: str, path_file: str) -> str:
    """
    Adds comments to a given Python file using the Gemini API.

    This function reads the content of a Python file, combines it with user-provided
    context, and sends it to the Gemini model to add comprehensive comments,
    including docstrings and inline comments.

    Args:
        context_file: A file containing context for
                      how the comments should be added.
        path_file: The absolute or relative path to the Python file that needs
                   comments.

    Returns:
        A string containing the Python code with added comments.
        If an error occurs (e.g., file not found, API error), a descriptive
        error message string is returned instead.
    """
    try:
        # Read the content from the context and python files
        with open(context_file, 'r') as f:
            context = f.read()

        with open(path_file, 'r') as f:
            code_content = f.read()



        # Construct the prompt for the model
        prompt = f"""
        **Context:**
        {context}

        **Python Code to Comment:**
        ```python
        {code_content}
        ```

        **Task:**
        Based on the instructions, add comprehensive and clear comments to the Python code provided above.
        This includes:
        1. A module-level docstring explaining the purpose of the file.
        2. Function and class docstrings following a standard format (e.g., Google's style guide).
        3. Inline comments for complex or non-obvious lines of code.

        Return only the fully commented Python code, without any additional explanations or markdown formatting.
        """

        # Generate the content using the model
        response = client.models.generate_content(
            model="gemini-2.5-flash",
            contents=prompt,
            config=types.GenerateContentConfig(
                temperature=0,
            ),
        )
        # Clean the response to get only the code block
        commented_code = response.text
        if "```python" in commented_code:
            commented_code = commented_code.split("```python\n")[1].split("```")[0]

        return commented_code.strip()

    except FileNotFoundError as e:
        return f"Error: The file was not found - {e}"
    except Exception as e:
        return f"An unexpected error occurred: {e}"