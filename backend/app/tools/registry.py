"""
The Tool Manager (registry).

It holds all available tools and offers two things to the rest of the app:
  1. declarations(): the tools described in Gemini's format, so the model knows
     what's on the menu.
  2. execute(name, args): actually run a tool the model asked for, by name.

This is the single choke-point between "the model wants to use a tool" and
"our Python code runs it". Adding a tool = add it to the list at the bottom.
"""

from google.genai import types

from app.tools.base import Tool
from app.tools.time_tool import time_tool


class ToolManager:
    def __init__(self, tools: list[Tool]):
        # Index tools by name for fast lookup when the model calls one.
        self._tools: dict[str, Tool] = {t.name: t for t in tools}

    def declarations(self):
        """
        Return the tools in Gemini's format (a list of types.Tool), or None if
        there are no tools. This is what we hand to the model so it can decide
        whether to call something.
        """
        if not self._tools:
            return None
        function_declarations = [
            types.FunctionDeclaration(
                name=t.name,
                description=t.description,
                parameters=t.parameters,
            )
            for t in self._tools.values()
        ]
        return [types.Tool(function_declarations=function_declarations)]

    def execute(self, name: str, args: dict) -> str:
        """
        Run the tool the model requested and return its result as a string.

        We never let a tool crash the request: unknown tools and tool errors
        become plain strings, which we hand back to the model so it can react.
        """
        tool = self._tools.get(name)
        if tool is None:
            return f"Error: no tool named '{name}'."
        try:
            return tool.run(args or {})
        except Exception as e:
            return f"Error while running tool '{name}': {e}"


# The app-wide tool manager. Register tools here — this is the ONLY line that
# changes when we add a new tool (e.g. weather in Milestone 9).
tool_manager = ToolManager([time_tool])
