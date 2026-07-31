"""
Gemini service — the ONLY place that knows how to talk to Google Gemini.

Unchanged in behaviour from Milestone 3; it now reads its configuration from
the central `settings` object instead of calling os.getenv() itself.
"""

from google import genai
from google.genai import types

from app.core.config import settings


class GeminiError(Exception):
    """Raised when we cannot get a valid reply from Gemini.

    The API layer catches this and turns it into a clean HTTP 502, so a
    failure talking to Gemini never crashes the whole server.
    """


# Fail loudly and early if the key is missing.
if not settings.GEMINI_API_KEY:
    raise GeminiError(
        "GEMINI_API_KEY is not set. Copy backend/.env.example to backend/.env "
        "and add your key from https://aistudio.google.com/apikey"
    )

# Create the Gemini client once, at import time, and reuse it for every request.
# A request timeout means a slow or stuck Gemini call fails cleanly (raising an
# error we turn into a 502) instead of hanging the request forever.
client = genai.Client(
    api_key=settings.GEMINI_API_KEY,
    http_options=types.HttpOptions(timeout=30_000),  # milliseconds
)


# Safety cap: how many times the model may call a tool within one request.
# Prevents an infinite "call tool -> call tool -> ..." loop.
MAX_TOOL_STEPS = 5


def _first_function_call(response):
    """Return the model's function_call from a response, or None if it replied
    with plain text instead of asking for a tool."""
    try:
        parts = response.candidates[0].content.parts
    except (AttributeError, IndexError, TypeError):
        return None
    for part in parts or []:
        if getattr(part, "function_call", None):
            return part.function_call
    return None


def generate_reply(
    contents,
    system_instruction: str | None = None,
    tools=None,
    execute_tool=None,
) -> str:
    """
    Send `contents` to Gemini and return the model's text reply, running any
    tools the model asks for along the way (function calling).

    `contents`            : a string, or a list of turns in Gemini's format.
    `system_instruction`  : optional persona/rules (sent separately via config).
    `tools`               : optional tool declarations (from the tool manager).
    `execute_tool(name,args)` : callback that actually runs a tool by name.

    The function-calling loop:
      1. Ask the model (giving it the tool menu).
      2. If it replied with TEXT -> that's the final answer, return it.
      3. If it asked for a TOOL -> run the tool, append the call + result to the
         conversation, and loop back to step 1 so the model can use the result.

    Raises GeminiError on API/network failure or an empty response.
    """
    config = types.GenerateContentConfig(
        system_instruction=system_instruction,
        tools=tools,
        # Disable the SDK's built-in auto-execution: we run tools ourselves so
        # the mechanism is explicit and under our control.
        automatic_function_calling=(
            types.AutomaticFunctionCallingConfig(disable=True) if tools else None
        ),
    )

    # We may append tool turns, so work on our own list.
    working = list(contents) if isinstance(contents, list) else [contents]

    for _ in range(MAX_TOOL_STEPS):
        try:
            response = client.models.generate_content(
                model=settings.GEMINI_MODEL,
                contents=working,
                config=config,
            )
        except Exception as e:
            raise GeminiError(f"Gemini request failed: {e}") from e

        function_call = _first_function_call(response)

        # No tool requested -> the model gave us the final text answer.
        if function_call is None:
            if not response.text:
                raise GeminiError("Gemini returned an empty response.")
            return response.text

        # The model asked to call a tool.
        if execute_tool is None:
            raise GeminiError(
                f"Model requested tool '{function_call.name}' but no executor "
                "was provided."
            )
        args = dict(function_call.args) if function_call.args else {}
        result = execute_tool(function_call.name, args)

        # Append (a) the model's tool-call turn and (b) our tool-result turn,
        # then loop so the model can turn the result into a natural answer.
        working.append(response.candidates[0].content)
        working.append(
            types.Content(
                role="user",
                parts=[
                    types.Part.from_function_response(
                        name=function_call.name,
                        response={"result": result},
                    )
                ],
            )
        )

    raise GeminiError("Tool loop did not finish (too many tool calls).")
