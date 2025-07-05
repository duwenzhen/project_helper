import tempfile
import shutil
import pygit2 # The library that does all the work

def clone_repo_native(repo_url: str) -> str | None:
    """
    Clones a Git repository using pygit2, without needing git installed.

    Args:
        repo_url: The URL of the Git repository to clone.

    Returns:
        The local file path to the cloned repository on success,
        or None on failure.
    """
    # Create a new temporary directory for the clone.
    temp_dir = tempfile.mkdtemp()
    print(f"✅ Created temporary directory: {temp_dir}")

    try:
        print(f"⏳ Cloning repository from {repo_url}...")

        # Use pygit2 to clone the repository.
        # This is the native Python equivalent of 'git clone'.
        pygit2.clone_repository(repo_url, temp_dir)

        print("✅ Repository cloned successfully.")
        return temp_dir

    except pygit2.GitError as e:
        print(f"❌ Error: Failed to clone repository with pygit2.")
        print(f"   Error: {e}")
        shutil.rmtree(temp_dir) # Clean up the failed attempt
        return None
    except ImportError:
        print("❌ Error: pygit2 library not found. Please run 'pip install pygit2'.")
        shutil.rmtree(temp_dir)
        return None
    except Exception as e:
        print(f"An unexpected error occurred: {e}")
        shutil.rmtree(temp_dir)
        return None


if __name__ == '__main__':
    # --- Example Usage ---
    # A public repository URL to test with.
    example_repo_url = "https://github.com/psf/black.git"

    local_path = clone_repo_native(example_repo_url)

    if local_path:
        print("\n---")
        print(f"🚀 Success! The repository is available at the following local path:")
        print(f"   {local_path}")
    else:
        print("\n---")
        print("🔥 Operation failed. Please check the error messages above.")