"""
tests/test_logic_kb.py
Tests for the Logic / Knowledge Base module.
Run from the campus_ai folder with:   python -m pytest tests
"""

from modules.logic_kb import ( check_query, check_request, parse_fact, normalize_fact, format_fact)
from modules.preprocessing import preprocess
from pipeline import process_request


def ask(text):
    return check_query(text)


def gate(name, category):
    return check_request({"name": name, "category": category})


                                                        
def test_parse_fact():
    assert parse_fact("UsesLab(DrKhan, Lab1)") == ("UsesLab", "DrKhan", "Lab1")
    assert parse_fact("Student(Ali)") == ("Student", "Ali")


def test_bad_queries_are_not_parsed():
    for bad in ["UsesLab", "UsesLab()", "UsesLab(Ali,)", "(Ali)", "A(B(C))", "UsesLab(Ali"]:
        assert parse_fact(bad) is None


def test_names_are_cleaned_by_case_and_spaces():
    fact = normalize_fact(parse_fact("useslab(dr khan, LAB1)"))
    assert format_fact(fact) == "UsesLab(DrKhan, Lab1)"


                                                            
def test_instructor_chain_R2_then_R4():
    result = ask("UsesLab(DrKhan, Lab1)")
    assert result["entailed"] == True
    assert result["explanation"][0] == "Known fact: Teaches(DrKhan, AI)"
    assert result["explanation"][1].startswith("R2:")
    assert result["explanation"][2].startswith("R4:")


def test_student_uses_lab_by_R3():
    result = ask("UsesLab(Ali, Lab1)")
    assert result["entailed"] == True
    assert result["explanation"][-1].startswith("R3:")


def test_ali_eligible_by_R1():
    result = ask("Eligible(Ali, AI)")
    assert result["entailed"] == True
    assert result["explanation"][-1].startswith("R1:")
    assert len(result["explanation"]) == 3                                  


def test_sara_is_not_eligible():
    result = ask("Eligible(Sara, AI)")
    assert result["entailed"] == False
    assert "cannot be derived" in result["explanation"][0]


def test_unknown_things_are_not_entailed():
    assert ask("UsesLab(Sara, Lab1)")["entailed"] == False
    assert ask("UsesLab(Bilal, Lab1)")["entailed"] == False
    assert ask("Flies(Ali, AI)")["entailed"] == False


def test_known_facts_are_entailed_directly():
    result = ask("Student(Ali)")
    assert result["entailed"] == True
    assert result["explanation"] == ["Known fact: Student(Ali)"]


                                                                  
def test_ali_may_request_everything():
    for category in ["AI_Lab_Support", "Viva", "Access", "Maintenance", "Emergency_Help"]:
        assert gate("Ali", category)["allowed"] == True


def test_drkhan_may_request_lab_viva_and_access():
    for category in ["AI_Lab_Support", "Viva", "Access"]:
        assert gate("DrKhan", category)["allowed"] == True


def test_sara_is_blocked_except_open_categories():
    for category in ["AI_Lab_Support", "Viva", "Access"]:
        assert gate("Sara", category)["allowed"] == False
    assert gate("Sara", "Maintenance")["allowed"] == True
    assert gate("Sara", "Emergency_Help")["allowed"] == True


def test_gate_cleans_the_name():
    assert gate("ali", "AI_Lab_Support")["allowed"] == True
    assert gate("dr khan", "Viva")["allowed"] == True


def test_unknown_person_is_blocked():
    assert gate("Bilal", "AI_Lab_Support")["allowed"] == False


                                                                  
def test_bad_query_is_rejected_in_preprocessing():
    raw = {"name": "DrKhan", "role": "instructor", "request_type": "Eligibility_Check",
           "query": "UsesLab DrKhan Lab1"}
    request, errors = preprocess(raw)
    assert len(errors) == 1


def test_query_is_cleaned_in_preprocessing():
    raw = {"name": "DrKhan", "role": "instructor", "request_type": "Eligibility_Check",
           "query": "useslab(drkhan,lab1)"}
    request, errors = preprocess(raw)
    assert errors == []
    assert request["query"] == "UsesLab(DrKhan, Lab1)"


def test_eligibility_check_end_to_end():
    raw = {"name": "DrKhan", "role": "instructor", "request_type": "Eligibility_Check",
           "query": "UsesLab(DrKhan, Lab1)"}
    response = process_request(raw)
    assert response["decision"] == "answered"
    assert response["eligibility"]["entailed"] == True
    assert "R2" in response["eligibility"]["explanation"]
    assert response["message"] == "Eligibility query answered successfully."


def test_booking_by_ineligible_user_is_rejected_before_csp():
    raw = {"name": "Sara", "role": "student", "request_type": "Booking_or_Scheduling",
           "category": "AI_Lab_Support", "preferred_slot": "2"}
    response = process_request(raw)
    assert response["decision"] == "rejected"
    assert response["eligibility"]["allowed"] == False
    assert "not eligible" in response["message"]

def test_role_verification_rejects_ali_as_instructor():
    from modules.logic_kb import verify_role
    result = verify_role("Ali", "instructor")
    assert result["allowed"] is False
    assert "registered as student" in result["explanation"][0]


def test_role_verification_accepts_ali_as_student():
    from modules.logic_kb import verify_role
    result = verify_role("Ali", "student")
    assert result["allowed"] is True


def test_eligibility_pipeline_rejects_role_mismatch():
    raw = {"name": "ali", "role": "instructor", "request_type": "Eligibility_Check",
           "query": "CanRequest(Ali, Viva)"}
    response = process_request(raw)
    assert response["decision"] == "rejected"
    assert response["eligibility"]["allowed"] is False
    assert "Role mismatch" in response["eligibility"]["explanation"]


def test_eligibility_pipeline_accepts_matching_role():
    raw = {"name": "ali", "role": "student", "request_type": "Eligibility_Check",
           "query": "CanRequest(Ali, Viva)"}
    response = process_request(raw)
    assert response["decision"] == "answered"
    assert response["eligibility"]["entailed"] is True


def test_eligibility_query_cannot_check_another_users_identity():
    """Reject an eligibility query whose subject differs from the requester."""
    raw = {"name": "Ali", "role": "student",
           "request_type": "Eligibility_Check",
           "query": "CanRequest(DrKhan, Viva)"}
    response = process_request(raw)
    assert response["decision"] == "rejected"
    assert response["eligibility"]["allowed"] is False
    assert "Identity mismatch" in response["eligibility"]["explanation"]
