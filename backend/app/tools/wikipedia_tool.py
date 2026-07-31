"""
A Wikipedia lookup tool — a simple "search" capability, no API key needed.

Two calls to Wikipedia's public API:
  1. search for the best-matching article title,
  2. fetch that article's summary.

Wikipedia asks API clients to send a descriptive User-Agent, so we do.
"""

import httpx

from app.tools.base import Tool

SEARCH_URL = "https://en.wikipedia.org/w/api.php"
SUMMARY_URL = "https://en.wikipedia.org/api/rest_v1/page/summary/"
# Wikimedia requires a descriptive User-Agent identifying the app + a contact URL,
# otherwise it returns 403. See https://meta.wikimedia.org/wiki/User-Agent_policy
HEADERS = {
    "User-Agent": (
        "AURUM-Chatbot/1.0 (https://github.com/moksha3110/Chatbot) python-httpx"
    )
}


def _wikipedia(args: dict) -> str:
    query = (args.get("query") or "").strip()
    if not query:
        return "Error: no search query provided."
    try:
        # 1. Find the best-matching article title.
        search = httpx.get(
            SEARCH_URL,
            params={
                "action": "query",
                "list": "search",
                "srsearch": query,
                "srlimit": 1,
                "format": "json",
            },
            headers=HEADERS,
            timeout=10,
        )
        search.raise_for_status()
        hits = search.json()["query"]["search"]
        if not hits:
            return f"No Wikipedia article found for '{query}'."
        title = hits[0]["title"]

        # 2. Fetch that article's summary.
        summary = httpx.get(SUMMARY_URL + title.replace(" ", "_"), headers=HEADERS, timeout=10)
        summary.raise_for_status()
        extract = summary.json().get("extract", "")
        return f"{title}: {extract}" if extract else f"Found '{title}' but no summary was available."
    except Exception as e:
        return f"Error searching Wikipedia for '{query}': {e}"


wikipedia_tool = Tool(
    name="search_wikipedia",
    description=(
        "Look up factual/encyclopedic information on Wikipedia. Use for questions "
        "about people, places, history, science, and general knowledge."
    ),
    run=_wikipedia,
    parameters={
        "type": "object",
        "properties": {
            "query": {
                "type": "string",
                "description": "What to look up, e.g. 'Alan Turing' or 'photosynthesis'.",
            }
        },
        "required": ["query"],
    },
)
