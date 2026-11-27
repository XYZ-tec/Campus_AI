"""
cli.py
======
Command-line interface: asks the structured request form, one field at a time.

Handout reference: Phase 1, Sections 1 and 2 (the CLI form).
Run it with:   python cli.py
"""

from core.constants import (
    ROLES, REQUEST_TYPES, CATEGORIES, LOCATIONS, BASE_FIELDS,
    REQUIRED_FIELDS, OPTIONAL_FIELDS,
)
from modules.preprocessing import normalize_choice
from pipeline import process_request
from modules.display import display_final_response

                                   
PROMPTS = {
    "category": "Enter Category (" + " / ".join(CATEGORIES) + ")",
    "current_location": "Enter Current Location (" + ", ".join(LOCATIONS) + ")",
    "destination": "Enter Destination (" + ", ".join(LOCATIONS) + ")",
    "preferred_slot": "Enter Preferred Slot (1-4)",
    "severity": "Enter Severity (1-10)",
    "time_sensitivity": "Enter Time Sensitivity (1-10)",
    "crowd_level": "Enter Crowd Level (1-10)",
    "group_id": "Enter Group ID (for example G1)",
    "query": "Enter Query (for example UsesLab(DrKhan, Lab1))",
    "description_note": "Enter Description Note",
    "include_route": "Do you also want route guidance? (yes/no)",
}


def ask(prompt):
    """Show a question and return the typed answer without extra spaces."""
    return input(prompt + ": ").strip()


def convert_menu_choice(choice):
    """The menu is numbered 1-5. Turn a number into the request type name.
    Anything else is returned unchanged so preprocessing can accept or reject it."""
    try:
        number = int(choice)
    except ValueError:
        return choice
    if number >= 1 and number <= len(REQUEST_TYPES):
        return REQUEST_TYPES[number - 1]
    return choice


def collect_request():
    """Ask the form and return the raw request as a dictionary of typed text."""
    raw_request = {}
    raw_request["name"] = ask("Enter Name")
    raw_request["role"] = ask("Enter Role (" + "/".join(ROLES) + ")")

    print("Enter Request Type:")
    for number in range(len(REQUEST_TYPES)):
        print("  " + str(number + 1) + ". " + REQUEST_TYPES[number])
    choice = ask("Enter choice")
    raw_request["request_type"] = convert_menu_choice(choice)

    request_type = normalize_choice(raw_request["request_type"], REQUEST_TYPES)
    if request_type is None:
        return raw_request                                                  

    for field in REQUIRED_FIELDS[request_type]:
        if field not in BASE_FIELDS:
            raw_request[field] = ask(PROMPTS[field])
    for field in OPTIONAL_FIELDS[request_type]:
        raw_request[field] = ask(PROMPTS[field] + " (optional, press Enter to skip)")
    return raw_request


def main():
    """Keep asking for requests until the user says no."""
    print("Smart Campus AI Decision Support and Automation System")
    try:
        while True:
            raw_request = collect_request()
            response = process_request(raw_request)
            display_final_response(response)
            again = ask("\nSubmit another request? (yes/no)").lower()
            if again != "yes" and again != "y":
                break
    except (EOFError, KeyboardInterrupt):
        print("\nInput closed.")
    print("Goodbye!")


if __name__ == "__main__":
    main()