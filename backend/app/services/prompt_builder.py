"""
Prompt builder.

A request to an LLM is not one string — it's ASSEMBLED from parts:
  1. a system instruction  (who the bot is + how it should behave)
  2. the conversation history  (past turns)
  3. the new user message
  (later: tool results, and retrieved documents for RAG)

This module is the SINGLE place that assembles those parts. Keeping it in one
file means we can always answer "what exactly are we sending the model?" and,
when we add tool results (M8) or RAG context (M10), there's one obvious place
to slot them in — instead of prompt fragments scattered across the codebase.
"""

from dataclasses import dataclass


# ---------------------------------------------------------------------------
# The system instruction: the bot's identity and rules. Gemini treats this as
# a special, high-priority instruction that shapes every reply. This is where
# you tune personality, tone, and guardrails.
# ---------------------------------------------------------------------------
SYSTEM_INSTRUCTION = """You are AURUM AI, a warm and sharp assistant built on \
Google Gemini for a developer's internship project.

Guidelines:
- Be helpful, clear, and concise. Prefer short paragraphs and tidy lists.
- If you are unsure or don't know something, say so plainly instead of guessing.
- Use light Markdown for structure when it genuinely helps readability.
- You may use the ✦ symbol as an occasional signature flourish, sparingly.
- You can use tools when helpful. You have a tool for the current date and time, \
and a tool for the current weather in a city — use them instead of guessing.
- You do not yet have web browsing or news tools. If asked for those, say that \
capability is coming soon rather than inventing an answer."""


# The context-window cap: only the most recent messages are replayed to the
# model, so a long chat never overflows its token limit. (Moved here from the
# conversation engine because trimming history is part of building the prompt.)
MAX_HISTORY_MESSAGES = 20


@dataclass
class BuiltPrompt:
    """Everything gemini_service needs for one call, assembled and ready."""
    system_instruction: str
    contents: list[dict]


def build(history: list[dict], user_message: str) -> BuiltPrompt:
    """
    Assemble the full prompt from the session's history and the new message.

    `history` is a list of {"role", "text"} dicts (from the memory store).
    Returns a BuiltPrompt with the system instruction and the `contents` list
    in Gemini's turn format.
    """
    # history + the new user turn, trimmed to the context-window cap.
    messages = history + [{"role": "user", "text": user_message}]
    messages = messages[-MAX_HISTORY_MESSAGES:]

    # Convert our simple {role, text} shape into Gemini's {role, parts} format.
    contents = [
        {"role": m["role"], "parts": [{"text": m["text"]}]}
        for m in messages
    ]

    return BuiltPrompt(system_instruction=SYSTEM_INSTRUCTION, contents=contents)
