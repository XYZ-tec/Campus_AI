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

                                                                             
                                                                    
                                                                             
REQUEST_TYPES = [
    "Navigation_Only",
    "Eligibility_Check",
    "Booking_or_Scheduling",
    "Urgent_Service_Request",
    "Full_Service_Request",
]

ROLES = ["student", "instructor", "staff"]

                                                                            
                                                                               
                                                                                
CATEGORIES = ["AI_Lab_Support", "Viva", "Access", "Maintenance", "Emergency_Help"]

                                                                           
                                                
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

VALID_SLOTS = (1, 2, 3, 4)                           
SCORE_MIN, SCORE_MAX = 1, 10                                                   

                                                                             
                                                    
                                                                             
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

                                                                             
                                                                        
                                                                             
PIPELINES = {
    "Navigation_Only": ["Search"],
    "Eligibility_Check": ["Logic_KB"],
    "Booking_or_Scheduling": ["Logic_KB", "CSP"],                         
    "Urgent_Service_Request": ["ANN", "Logic_KB", "CSP"],                     
    "Full_Service_Request": ["ANN", "Logic_KB", "CSP", "Search"],
}
                                                                         
                                                              
OPTIONAL_SEARCH_TYPES = {"Booking_or_Scheduling", "Urgent_Service_Request"}

                                                                             
OPTIONAL_FIELDS = {
    "Navigation_Only": [],
    "Eligibility_Check": [],
    "Booking_or_Scheduling": ["group_id", "current_location"],
    "Urgent_Service_Request": ["preferred_slot", "group_id", "description_note"],
    "Full_Service_Request": ["group_id", "description_note"],
}

                                                                             
                                       
                                                                             
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

                                                                  
                                                                            
                                            
CATEGORY_ENCODING = {}
for number in range(len(CATEGORIES)):
    CATEGORY_ENCODING[CATEGORIES[number]] = number

PRIORITY_BINARY_LABELS = {0: "not_urgent", 1: "urgent"}
PRIORITY_CLASS_LABELS = {0: "low", 1: "normal", 2: "high", 3: "urgent"}

                                                                             
                                                                             
                                                                
                                                                             
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