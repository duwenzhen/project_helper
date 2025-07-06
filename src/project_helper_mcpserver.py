"""
Model Context Protocol (MCP) gemini api Server implementation.

This module sets up an MCP-compliant server and registers gemini api tools
that follow Anthropic's Model Context Protocol specification. These tools can be
accessed by Claude and other MCP-compatible AI models.
"""
from mcp.server.fastmcp import FastMCP
from typing import Dict
import argparse
from mylogging import logger
from treeList import generate_tree_with_functions
from fileUtil import combine_files
from gitUtil import clone_repo_native
DEFAULT_PORT = 3001
DEFAULT_CONNECTION_TYPE = "stdio"  # Alternative: "stdio"
def create_mcp_server(port=DEFAULT_PORT):
    """
    Create and configure the Model Context Protocol server.

    Args:
        port: Port number to run the server on

    Returns:
        Configured MCP server instance
    """
    mcp = FastMCP("GeminiApiService", port=port)

    # Register MCP-compliant tools
    register_tools(mcp)

    return mcp


def register_tools(mcp):
    """
    Register all tools with the MCP server following the Model Context Protocol specification.

    Each tool is decorated with @mcp.tool() to make it available via the MCP interface.

    Args:
        mcp: The MCP server instance
    """

    @mcp.tool()
    async def browse_folder(path : str):
        """
        Browse or scan the folder and the sub folders of the path provided, and list the files inside
        Args:
            path: the path to the folder you want to browse

        Returns:
            return in a dictionary, tree_string, the arborescence of the folders as a string and path_dictionary, a dictionary mapping unique file IDs to their absolute paths.
        """
        tree_string, path_dictionary = await generate_tree_with_functions(path)
        return  {
            "tree_string": tree_string,
            "path_dictionary": path_dictionary
        }

    @mcp.tool()
    async def checkout_git_repo(url : str) -> str:
        """
        Checkout the git repo that is provided, checkout it into a temporary folder
        Args:
            url: the url where the git repo is located

        Returns:
            return the temporary folder's location as a string
        """
        return await clone_repo_native(url)

    @mcp.tool()
    async def combine_path_dictionary(tree_string  :str, path_dictionary) :
        """
        for each file in the path_dictionary, take the contains and combine all the content into one big file
        Args:

            path_dictionary: a dictionary of key = int and value = str, int is the unique number and str is the path to the file
            tree_string : the arborescence of the folders as a string

        Returns:
            return dictionary of output_file_path, a path to the big file with combined content, and path_dictionary
        """
        return await combine_files(tree_string, path_dictionary)




    @mcp.tool()
    def server_status():
        """
        Check if the Model Context Protocol server is running.

        This MCP tool provides a simple way to verify the server is operational.

        Returns:
            A status message indicating the server is online
        """
        return {"status": "online", "message": "MCP gemini api Server is running"}

    logger.debug("Model Context Protocol tools registered")


def main():
    """
    Main entry point for the Model Context Protocol gemini api Server.
    """
    # Initialize argument parser
    parser = argparse.ArgumentParser(description="Model Context Protocol gemini api Server")
    parser.add_argument("--connection_type", type=str, default=DEFAULT_CONNECTION_TYPE,
                        choices=["http", "stdio"], help="Connection type (http or stdio)")
    parser.add_argument("--port", type=int, default=DEFAULT_PORT,
                        help=f"Port to run the server on (default: {DEFAULT_PORT})")
    args = parser.parse_args()

    # Initialize MCP server
    mcp = create_mcp_server(port=args.port)

    # Determine server type
    server_type = "sse" if args.connection_type == "http" else "stdio"

    # Start the server
    logger.info(
        f"🚀 Starting Model Context Protocol gemini api Server on port {args.port} with {args.connection_type} connection")
    mcp.run(server_type)


if __name__ == "__main__":
    main()