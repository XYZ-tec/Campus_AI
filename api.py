"""
api.py
======
Optional JSON interface for quick manual testing. The required project
interface remains the structured command-line form in cli.py.
"""

import json
import sys

from pipeline import process_request


def main():
    """Read one JSON request from standard input and print its final response."""
    try:
        raw_request = json.load(sys.stdin)
        print(json.dumps(process_request(raw_request), indent=2))
    except (json.JSONDecodeError, TypeError) as error:
        print(json.dumps({"decision": "rejected", "message": "Invalid JSON input: " + str(error)}, indent=2))


if __name__ == "__main__":
    main()
