"""
modules/preprocessing.py
========================
Input and Preprocessing: the first module of the system.

Handout reference: Phase 1, Sections 4 and 5; Phase 3, Section 8.
Instructor document: Section 3.1.

Steps (Phase 3, Section 8.1):
  1. read the raw fields           (done by the CLI or the UI)
  2. validate the fields           -> validate and collect error messages
  3. normalize the values          -> "main gate" becomes "Main_Gate"
  4. build one standard request    -> the dictionary from new_request()

OUR rule for normalization (agreed with you): we only fix CASE and SPACES
(and hyphens). A real misspelling such as "cafetria" is NOT guessed, it is
rejected, and the error message lists the valid choices.
"""

from modules.logic_kb import parse_fact, normalize_fact, format_fact
from core.constants import (
    ROLES, REQUEST_TYPES, CATEGORIES, LOCATIONS, VALID_SLOTS,
    SCORE_MIN, SCORE_MAX, BASE_FIELDS, REQUIRED_FIELDS, OPTIONAL_FIELDS,
    new_request,
)

# Fields whose value must be one of a fixed list of names
CHOICE_FIELDS = {
    "category": CATEGORIES,
    "current_location": LOCATIONS,
    "destination": LOCATIONS,
}

# Fields whose value must be a whole number inside a range: (smallest, biggest)
NUMBER_FIELDS = {
    "preferred_slot": (min(VALID_SLOTS), max(VALID_SLOTS)),
    "severity": (SCORE_MIN, SCORE_MAX),
    "time_sensitivity": (SCORE_MIN, SCORE_MAX),
    "crowd_level": (SCORE_MIN, SCORE_MAX),
}

request_counter = 100       # request ids start at REQ101


def generate_request_id():
    """Give every request its own id: REQ101, REQ102, ..."""
    global request_counter
    request_counter = request_counter + 1
    return "REQ" + str(request_counter)


def normalize_choice(value, valid_choices):
    """Match what the user typed against the valid names, ignoring case, spaces
    and hyphens ("ai lab" -> "AI_Lab"). Returns the official name, or None if
    nothing matches."""
    text = str(value).strip().lower()
    text = text.replace(" ", "_")
    text = text.replace("-", "_")
    for choice in valid_choices:
        if choice.lower() == text:
            return choice
    return None


def read_number(value, smallest, biggest):
    """Turn text into a whole number inside [smallest, biggest].
    Returns None if it is not a whole number or is out of range."""
    try:
        number = int(str(value).strip())
    except ValueError:
        return None
    if number < smallest or number > biggest:
        return None
    return number


def preprocess(raw_request):
    """Validate and normalize a raw request (a dictionary of typed-in values).
    Returns two things: (request, errors)
      request - the standard request object (see core/constants.py)
      errors  - a list of problems; an EMPTY list means the request is valid"""
    request = new_request()
    request["request_id"] = generate_request_id()
    errors = []

    # ---- base fields: name, role, request_type (needed by every request) ----
    name = str(raw_request.get("name") or "").strip()
    if name == "":
        errors.append("name is required")
    request["name"] = name

    role = normalize_choice(raw_request.get("role") or "", ROLES)
    if role is None:
        errors.append("role must be one of: " + ", ".join(ROLES))
    else:
        request["role"] = role

    request_type = normalize_choice(raw_request.get("request_type") or "", REQUEST_TYPES)
    if request_type is None:
        errors.append("request_type must be one of: " + ", ".join(REQUEST_TYPES))
        return request, errors      # without a valid type we do not know which fields to check
    request["request_type"] = request_type

    # ---- fields that depend on the request type (Phase 1, Section 2.2) ----
    required = REQUIRED_FIELDS[request_type]
    allowed = required + OPTIONAL_FIELDS[request_type]

    for field in allowed:
        if field in BASE_FIELDS:
            continue
        value = raw_request.get(field)
        if value is None:
            value = ""
        text = str(value).strip()

        if text == "":
            if field in required:
                errors.append(field + " is required")
            continue

        if field in CHOICE_FIELDS:
            official_name = normalize_choice(text, CHOICE_FIELDS[field])
            if official_name is None:
                errors.append(field + " '" + text + "' is not valid. Choose from: "
                              + ", ".join(CHOICE_FIELDS[field]))
            else:
                request[field] = official_name
        elif field in NUMBER_FIELDS:
            smallest, biggest = NUMBER_FIELDS[field]
            number = read_number(text, smallest, biggest)
            if number is None:
                errors.append(field + " must be a whole number from "
                              + str(smallest) + " to " + str(biggest))
            else:
                request[field] = number
        elif field == "query":
            fact = parse_fact(text)
            if fact is None:
                errors.append("query must look like Predicate(Name, Name), "
                              "for example UsesLab(DrKhan, Lab1)")
            else:
                request["query"] = format_fact(normalize_fact(fact))
        else:
            request[field] = text   # free-text field

    return request, errors