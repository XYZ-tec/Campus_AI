"""Tests for the ANN priority predictor and CSP scheduler."""

from modules.ann import build_feature_vector, predict_priority
from modules.csp import schedule_request


def sample_request():
    """Return the sample full-service request from the project handout."""
    return {
        "name": "Ali", "role": "student", "category": "AI_Lab_Support",
        "current_location": "Hostel", "preferred_slot": 2,
        "severity": 8, "time_sensitivity": 9, "crowd_level": 5,
    }


def test_ann_uses_seven_features_in_fixed_order():
    """Check that ANN preprocessing follows the standard seven-feature vector."""
    vector = build_feature_vector(sample_request())
    assert len(vector) == 7
    assert vector[0] == 0
    assert vector[1] == 0
    assert vector[2:5] == [8, 9, 5]
    assert vector[5] == 6
    assert vector[6] == 1


def test_ann_returns_both_priority_predictions():
    """Check Perceptron and MLP return the expected output fields."""
    result = predict_priority(sample_request())
    assert result["binary_priority"] in ["urgent", "not_urgent"]
    assert result["final_priority"] in ["low", "normal", "high", "urgent"]
    assert 0 <= result["confidence"] <= 1


def test_csp_moves_to_next_available_slot():
    """Check the preferred AI Lab slot conflict is resolved by backtracking."""
    result = schedule_request(sample_request(), "high")
    assert result["decision"] == "accepted"
    assert result["assigned_room"] == "AI_Lab"
    assert result["assigned_slot"] == 3


def test_csp_rejects_unknown_category():
    """Check that an unsupported service category is rejected safely."""
    request = sample_request()
    request["category"] = "Unknown"
    result = schedule_request(request)
    assert result["decision"] == "rejected"


def test_csp_never_double_books():
    """Check that a room and slot given to one request is not given to another."""
    first = schedule_request(sample_request())
    second = schedule_request(sample_request())
    assert first["decision"] == "accepted"
    assert second["decision"] == "accepted"
    first_booking = (first["assigned_room"], first["assigned_slot"])
    second_booking = (second["assigned_room"], second["assigned_slot"])
    assert first_booking != second_booking
