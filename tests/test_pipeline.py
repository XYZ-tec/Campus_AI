"""
tests/test_pipeline.py
Tests for preprocessing, router, final response and the pipeline.
Run from the campus_ai folder with:   python -m pytest tests
"""

from modules.preprocessing import preprocess, normalize_choice
from modules.router import route_request
from modules.final_response import build_final_response
from pipeline import process_request


def navigation_request(source="Hostel", destination="AI_Lab"):
    return {"name": "Ali", "role": "student", "request_type": "Navigation_Only",
            "current_location": source, "destination": destination}


def full_request():
    return {"name": "Ali", "role": "student", "request_type": "Full_Service_Request",
            "category": "AI_Lab_Support", "current_location": "Hostel",
            "preferred_slot": "2", "severity": "8", "time_sensitivity": "9",
            "crowd_level": "5", "description_note": "Need urgent help"}


# ---------------- preprocessing ----------------
def test_normalization_fixes_case_and_spaces():
    assert normalize_choice("ai lab", ["AI_Lab", "Library"]) == "AI_Lab"
    assert normalize_choice("  MAIN-gate ", ["Main_Gate"]) == "Main_Gate"
    assert normalize_choice("urgent_service_request", ["Urgent_Service_Request"]) == "Urgent_Service_Request"


def test_misspelling_is_rejected_not_guessed():
    request, errors = preprocess(navigation_request(source="cafetria"))
    assert len(errors) == 1
    assert "current_location" in errors[0]


def test_valid_request_has_no_errors_and_is_normalized():
    request, errors = preprocess(navigation_request("hostel", "ai lab"))
    assert errors == []
    assert request["current_location"] == "Hostel"
    assert request["destination"] == "AI_Lab"
    assert request["request_id"].startswith("REQ")


def test_numbers_are_checked():
    for bad_value in ["0", "11", "abc", "7.5"]:
        raw = full_request()
        raw["severity"] = bad_value
        request, errors = preprocess(raw)
        assert len(errors) == 1
    raw = full_request()
    raw["preferred_slot"] = "5"
    request, errors = preprocess(raw)
    assert len(errors) == 1


def test_missing_required_fields_are_all_reported():
    request, errors = preprocess({"name": "", "role": "student", "request_type": "Navigation_Only"})
    assert len(errors) == 3         # name, current_location, destination


def test_unsupported_request_type_rejected():
    request, errors = preprocess({"name": "Ali", "role": "student", "request_type": "Pizza"})
    assert len(errors) == 1


def test_optional_field_left_empty_is_fine():
    raw = {"name": "Ali", "role": "student", "request_type": "Booking_or_Scheduling",
           "category": "Viva", "preferred_slot": "2", "current_location": ""}
    request, errors = preprocess(raw)
    assert errors == []


# ---------------- router ----------------
def route_for(raw):
    request, errors = preprocess(raw)
    return route_request(request)


def test_router_pipelines():
    assert route_for(navigation_request())["selected_pipeline"] == ["Search"]
    assert route_for(full_request())["selected_pipeline"] == ["ANN", "Logic_KB", "CSP", "Search"]

    eligibility = {"name": "DrKhan", "role": "instructor",
                   "request_type": "Eligibility_Check", "query": "UsesLab(DrKhan, Lab1)"}
    assert route_for(eligibility)["selected_pipeline"] == ["Logic_KB"]


def test_router_optional_search():
    booking = {"name": "Ali", "role": "student", "request_type": "Booking_or_Scheduling",
               "category": "Viva", "preferred_slot": "2"}
    assert route_for(booking)["selected_pipeline"] == ["Logic_KB", "CSP"]
    booking["current_location"] = "Hostel"
    output = route_for(booking)
    assert output["selected_pipeline"] == ["Logic_KB", "CSP", "Search"]
    assert output["needs_search"] == True
    assert output["needs_ann"] == False


# ---------------- final response (with fake module outputs) ----------------
def test_final_response_full_service():
    request, errors = preprocess(full_request())
    outputs = {
        "ANN": {"binary_priority": "urgent", "final_priority": "high", "confidence": 0.87},
        "Logic_KB": {"allowed": True, "entailed": False, "explanation": ["ok"]},
        "CSP": {"decision": "accepted", "assigned_room": "AI_Lab", "assigned_slot": 3,
                "destination": "AI_Lab", "notes": ""},
        "Search": {"algorithm_used": "A*", "path": ["Hostel", "Cafeteria", "Science_Block", "AI_Lab"],
                   "cost": 6, "steps": 3},
    }
    response = build_final_response(request, outputs)
    assert response["decision"] == "accepted"
    assert response["assignment"] == {"room": "AI_Lab", "slot": 3}
    assert response["route"]["cost"] == 6
    assert "AI_Lab in slot 3" in response["message"]


def test_final_response_logic_rejection():
    request, errors = preprocess(full_request())
    outputs = {"Logic_KB": {"allowed": False, "entailed": False, "explanation": ["Prerequisite missing"]}}
    response = build_final_response(request, outputs)
    assert response["decision"] == "rejected"
    assert response["eligibility"]["allowed"] == False


# ---------------- whole pipeline ----------------
def test_navigation_end_to_end():
    response = process_request(navigation_request("hostel", "ai lab"))
    assert response["decision"] == "completed"
    assert response["route"]["path"] == ["Hostel", "Cafeteria", "Science_Block", "AI_Lab"]
    assert response["route"]["cost"] == 6
    assert response["route"]["steps"] == 3
    assert response["message"] == "Best route generated successfully."


def test_invalid_request_is_rejected_by_pipeline():
    response = process_request(navigation_request(source="Mars"))
    assert response["decision"] == "rejected"
    assert "Invalid request" in response["message"]


def test_modules_not_built_yet_are_reported():
    response = process_request(full_request())
    assert response["decision"] == "rejected"
    assert "not built yet" in response["message"]