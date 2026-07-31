"""
A single, simple tool: get_current_time.

Why this tool first? Because the model genuinely CANNOT know the current time
on its own (its knowledge is frozen at training time). So it's the clearest
possible demonstration of function calling: the model must ask us for the answer.
It also needs no API key, so we can focus purely on the mechanism.
"""

from datetime import datetime

from app.tools.base import Tool


def _get_current_time(args: dict) -> str:
    """Return the server's current local date and time as a readable string."""
    # This tool takes no arguments, so we ignore `args`.
    return datetime.now().strftime("%A, %d %B %Y at %I:%M %p")


# The Tool object the manager registers. The description is written FOR THE MODEL:
# it tells Gemini exactly when reaching for this tool is appropriate.
time_tool = Tool(
    name="get_current_time",
    description=(
        "Get the current local date and time. "
        "Use this whenever the user asks what the current time or date is."
    ),
    run=_get_current_time,
    parameters={"type": "object", "properties": {}, "required": []},
)
