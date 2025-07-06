# pip install google-generativeai mcp
import asyncio
import os
# Add json import for formatting output
import json
import time
from datetime import datetime
from google import genai
from google.genai import types
from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client
from dotenv import load_dotenv
import markdown

# Load environment variables from .env file
load_dotenv()

# It's safer to use .get() to avoid errors if the key is missing
api_key = os.environ.get("GEMINI_API_KEY")
if not api_key:
    raise ValueError("GEMINI_API_KEY not found in environment variables or .env file")

client = genai.Client(api_key=api_key)

# Re-add StdioServerParameters, setting args for stdio
server_params = StdioServerParameters(
    command="python",
    args=["src/project_helper_mcpserver.py",
          "--connection_type", "stdio"],
    cwd=".",
    env={"GMAIL_API_KEY": api_key},
)


async def run(prompt_content):
    """
    Runs a multi-turn conversation with the Gemini model, allowing it to call
    a sequence of tools to fulfill the user's request.
    """
    async with stdio_client(server_params) as (read, write):
        async with ClientSession(read, write) as session:
            await session.initialize()

            mcp_tools = await session.list_tools()
            tools = [
                types.Tool(
                    function_declarations=[
                        {
                            "name": tool.name,
                            "description": tool.description,
                            "parameters": {
                                k: v
                                for k, v in tool.inputSchema.items()
                                if k not in ["additionalProperties", "$schema"]
                            },
                        }
                    ]
                )
                for tool in mcp_tools.tools
            ]

            # 1. Start the conversation with the user's prompt.
            # The model API expects a list of contents.
            conversation_history = [types.Content(role="user", parts=[types.Part(text=prompt_content)])]
            print(f"▶️ Starting conversation with prompt: \"{prompt_content}\"")

            # 2. Loop until the model gives a final text answer instead of a tool call.
            while True:
                # Send the entire conversation history to the model
                response = client.models.generate_content(
                    # Using a model that is strong with multi-turn tool use
                    model="gemini-2.5-flash",
                    contents=conversation_history,
                    config=types.GenerateContentConfig(
                        temperature=0,
                        tools=tools,
                    ),
                )

                latest_part = response.candidates[0].content.parts[0]

                # 3. Check if the model's response is a function call.
                if not latest_part.function_call:
                    # If not, we're done. The model has provided its final answer.
                    print("\n✅ Model has finished. Final response:")
                    print(response.text)
                    return response.text

                # 4. If we are here, the model wants to call a tool.
                function_call = latest_part.function_call
                tool_name = function_call.name
                tool_args = dict(function_call.args)

                print(f"🤖 Model wants to call tool: {tool_name}({json.dumps(tool_args)})")

                # Add the model's tool request to our history
                conversation_history.append(response.candidates[0].content)

                # 5. Execute the tool call using the MCP session.
                tool_result = await session.call_tool(tool_name, arguments=tool_args)
                print(f"🛠️ Tool '{tool_name}' executed.")

                # 6. Add the tool's result back to the conversation history.
                # This informs the model of the outcome of the tool call.
                conversation_history.append(
                    types.Content(
                        role = "function",
                        parts=[
                            types.Part(
                                function_response=types.FunctionResponse(
                                    name=tool_name,
                                    # The response from the tool must be a dictionary.
                                    response={"result": tool_result},
                                )
                            )
                        ]
                    )
                )
                # The loop will now continue, sending the updated history back to the model
                # for it to decide the next step.
