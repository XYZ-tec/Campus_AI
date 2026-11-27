"""
api.py
======
Optional JSON interface for quick manual testing. The required project
interface remains the structured command-line form in cli.py.
"""

import json
import sys

from pipeline import process_request
from modules.display import display_final_response


def main():
    """Read one JSON request from standard input and print its final response."""
    try:
        raw_request = json.load(sys.stdin)
        display_final_response(process_request(raw_request))
    except (json.JSONDecodeError, TypeError) as error:
        print("Request could not be processed.")
        print("Reason: Invalid JSON input - " + str(error))


if __name__ == "__main__":
    main()
