"""
Logging configuration.

Logging (not print()) is how real services record what happened — for debugging,
monitoring, and audits. We set a consistent format and a level controlled by
config, so you can turn detail up (DEBUG) or down (WARNING) without code changes.
"""

import logging


def setup_logging(level: str = "INFO") -> None:
    logging.basicConfig(
        level=level.upper(),
        format="%(asctime)s %(levelname)-8s %(name)s: %(message)s",
    )
