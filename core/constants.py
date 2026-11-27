"""
core/constants.py
=================
Single source of truth for names, ranges, encodings and templates.
Every module (preprocessing, router, search, logic_kb, csp, ann) imports
from here so that naming never drifts between modules.

Handout reference: Phase 3, Section 12 (Standard Python Data Structures),
plus Phase 1 Sections 2, 4.2 and 7 (fields, validation, router rules).
"""

import copy

# ---------------------------------------------------------------------------
# Allowed values (used by preprocessing validation, Phase 1 Sec 4.2)
# ---------------------------------------------------------------------------
REQUEST_TYPES = [
    "Navigation_Only",
    "Eligibility_Check",
    "Booking_or_Scheduling",
    "Urgent_Service_Request",
    "Full_Service_Request",
]

ROLES = ["student", "instructor", "staff"]

# Categories offered in the CLI form (Phase 1 Sec 1.2). The same list is the
# ANN "RequestType" feature (Phase 2 Sec 1.3), so there is only one definition.
# Emergency_Help comes from the handout's ANN encoding; we expose it in the CLI.
CATEGORIES = ["AI_Lab_Support", "Viva", "Access", "Maintenance", "Emergency_Help"]

# Campus locations: the 13 places on the instructor's predefined campus map
# (data/campus_graph.py holds how they connect).
LOCATIONS = [
    "Admin_Block",
    "Student_Services",
    "Exam_Hall",
    "Main_Gate",
    "Parking",
    "Seminar_Room",
    "Library",
    "AI_Lab",
    "Medical_Center",
    "Bus_Stop",
    "Cafeteria",
    "Science_Block",
    "Hostel",
]

VALID_SLOTS = (1, 2, 3, 4)          # Phase 1 Sec 4.2
SCORE_MIN, SCORE_MAX = 1, 10        # severity / time_sensitivity / crowd_level

# ---------------------------------------------------------------------------
# Required fields per request type (Phase 1 Sec 2.2)
# ---------------------------------------------------------------------------
BASE_FIELDS = ["name", "role", "request_type"]

REQUIRED_FIELDS = {
    "Navigation_Only": BASE_FIELDS + ["current_location", "destination"],
    "Eligibility_Check": BASE_FIELDS + ["query"],
    "Booking_or_Scheduling": BASE_FIELDS + ["category", "preferred_slot"],
    "Urgent_Service_Request": BASE_FIELDS + [
        "category", "current_location",
        "severity", "time_sensitivity", "crowd_level",
    ],
    "Full_Service_Request": BASE_FIELDS + [
        "category", "current_location", "preferred_slot",
        "severity", "time_sensitivity", "crowd_level",
    ],
}

# ---------------------------------------------------------------------------
# Router table (Phase 1 Sec 7.2). The router will own the needs_* flags.
# ---------------------------------------------------------------------------
PIPELINES = {
    "Navigation_Only": ["Search"],
    "Eligibility_Check": ["Logic_KB"],
    "Booking_or_Scheduling": ["Logic_KB", "CSP"],      # + optional Search
    "Urgent_Service_Request": ["ANN", "Logic_KB", "CSP"],  # + optional Search
    "Full_Service_Request": ["ANN", "Logic_KB", "CSP", "Search"],
}
# OUR decision: for these types, Search is added only if current_location
# was provided (the handout just says "optional / if needed").
OPTIONAL_SEARCH_TYPES = {"Booking_or_Scheduling", "Urgent_Service_Request"}

# Optional fields accepted by the structured CLI form (Handout Sections 2.2).
OPTIONAL_FIELDS = {
    "Navigation_Only": [],
    "Eligibility_Check": [],
    "Booking_or_Scheduling": ["group_id", "current_location"],
    "Urgent_Service_Request": ["preferred_slot", "group_id", "description_note"],
    "Full_Service_Request": ["group_id", "description_note"],
}

# ---------------------------------------------------------------------------
# ANN encodings (Phase 2 Sec 1.2 - 1.3)
# ---------------------------------------------------------------------------
FEATURE_ORDER = [
    "Role",
    "RequestType",
    "Severity",
    "TimeSensitivity",
    "CrowdLevel",
    "Distance",
    "Eligibility",
]

ROLE_ENCODING = {"student": 0, "instructor": 1, "staff": 2}

# Built from CATEGORIES so the CLI and the ANN can never disagree.
# Gives AI_Lab_Support=0, Viva=1, Access=2, Maintenance=3, Emergency_Help=4,
# the same numbers as the handout's example.
CATEGORY_ENCODING = {}
for number in range(len(CATEGORIES)):
    CATEGORY_ENCODING[CATEGORIES[number]] = number

PRIORITY_BINARY_LABELS = {0: "not_urgent", 1: "urgent"}
PRIORITY_CLASS_LABELS = {0: "low", 1: "normal", 2: "high", 3: "urgent"}

# ---------------------------------------------------------------------------
# Templates (Phase 3 Sec 12.1 - 12.7). Use the new_*() helpers, not the dicts
# directly, so two requests never share the same mutable object.
# ---------------------------------------------------------------------------
REQUEST_TEMPLATE = {
    "request_id": "",
    "name": "",
    "role": "",
    "request_type": "",
    "category": "",
    "current_location": "",
    "destination": "",
    "preferred_slot": None,
    "severity": 0,
    "time_sensitivity": 0,
    "crowd_level": 0,
    "group_id": "",
    "query": "",
    "eligibility_claim": False,
    "description_note": "",
}

ROUTER_OUTPUT_TEMPLATE = {
    "request_id": "",
    "selected_pipeline": [],
    "needs_ann": False,
    "needs_logic": False,
    "needs_csp": False,
    "needs_search": False,
}

PRIORITY_OUTPUT_TEMPLATE = {
    "binary_priority": "",
    "final_priority": "",
    "confidence": 0.0,
}

LOGIC_OUTPUT_TEMPLATE = {
    "allowed": False,
    "entailed": False,
    "explanation": "",
}

CSP_OUTPUT_TEMPLATE = {
    "decision": "",
    "assigned_room": "",
    "assigned_slot": None,
    "destination": "",
    "notes": "",
}

SEARCH_OUTPUT_TEMPLATE = {
    "algorithm_used": "",
    "path": [],
    "cost": 0,
    "steps": 0,
}

FINAL_RESPONSE_TEMPLATE = {
    "request_id": "",
    "decision": "",
    "priority": {},
    "eligibility": {},
    "assignment": {},
    "route": {},
    "message": "",
}


def _fresh(template):
    return copy.deepcopy(template)


def new_request():
    return _fresh(REQUEST_TEMPLATE)


def new_router_output():
    return _fresh(ROUTER_OUTPUT_TEMPLATE)


def new_priority_output():
    return _fresh(PRIORITY_OUTPUT_TEMPLATE)


def new_logic_output():
    return _fresh(LOGIC_OUTPUT_TEMPLATE)


def new_csp_output():
    return _fresh(CSP_OUTPUT_TEMPLATE)


def new_search_output():
    return _fresh(SEARCH_OUTPUT_TEMPLATE)


def new_final_response():
    return _fresh(FINAL_RESPONSE_TEMPLATE)