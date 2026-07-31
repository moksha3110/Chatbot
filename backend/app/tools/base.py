"""
The generic Tool interface.

Every tool — no matter what it does — is described the same way, so the tool
manager can treat them uniformly. A Tool bundles:

  - name:        the identifier the model uses to call it
  - description: WHAT it does and WHEN to use it (the model reads this to decide!)
  - parameters:  a JSON-schema describing the arguments the model must provide
  - run:         the actual Python function that does the work

Keeping this shape generic is the whole point of Milestone 8: adding a new tool
later (weather, search, ...) means creating one Tool object — nothing else in
the calling machinery changes.
"""

from dataclasses import dataclass, field
from typing import Callable


@dataclass
class Tool:
    name: str
    description: str
    # run takes a dict of arguments (from the model) and returns a string result.
    run: Callable[[dict], str]
    # JSON-schema for the arguments. Default: no arguments.
    parameters: dict = field(
        default_factory=lambda: {"type": "object", "properties": {}, "required": []}
    )
