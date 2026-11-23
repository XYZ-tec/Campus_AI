"""
modules/final_response.py
=========================
Final Response Layer: combines the outputs of the modules that actually ran
into ONE user-facing answer.

Handout reference: Phase 1, Section 6 and 8; Phase 3, Sections 3.4 and 6.
Instructor document: Section 3.7.

module_outputs is a dictionary that only contains the modules that ran, e.g.
    {"Search": {...}}  or  {"ANN": {...}, "Logic_KB": {...}, "CSP": {...}, "Search": {...}}
"""

from core.constants import new_final_response


def build_rejection(request_id, message, eligibility=None):
    """Build the standard 'rejected' response (Phase 3, Section 3.4).
    eligibility is only filled when Logic/KB was the module that said no."""
    response = new_final_response()
    response["request_id"] = request_id
    response["decision"] = "rejected"
    if eligibility is not None:
        response["eligibility"] = eligibility
    response["message"] = message
    return response


def build_final_response(request, module_outputs):
    """Combine whatever the modules returned into the final response.
    If any module reports a failure, a rejection is returned instead."""
    request_id = request["request_id"]
    request_type = request["request_type"]
    response = new_final_response()
    response["request_id"] = request_id

    if "ANN" in module_outputs:
        priority = module_outputs["ANN"]
        response["priority"] = {
            "binary_priority": priority["binary_priority"],
            "final_priority": priority["final_priority"],
            "confidence": priority["confidence"],
        }

    if "Logic_KB" in module_outputs:
        logic = module_outputs["Logic_KB"]
        if request_type == "Eligibility_Check":
            response["eligibility"] = {
                "entailed": logic["entailed"],
                "explanation": "; ".join(logic["explanation"]),
            }
        elif logic["allowed"] == False:
            reason = {"allowed": False, "explanation": "; ".join(logic["explanation"])}
            return build_rejection(request_id,
                                   "Your request has been rejected because you are not eligible for this service.",
                                   reason)
        else:
            response["eligibility"] = {"allowed": True}

    if "CSP" in module_outputs:
        csp = module_outputs["CSP"]
        if csp["decision"] != "accepted":
            return build_rejection(request_id, "No valid assignment was found. " + csp["notes"])
        response["assignment"] = {"room": csp["assigned_room"], "slot": csp["assigned_slot"]}

    if "Search" in module_outputs:
        search = module_outputs["Search"]
        if len(search["path"]) == 0:
            return build_rejection(request_id, "No valid route exists for this request.")
        response["route"] = {
            "algorithm": search["algorithm_used"],
            "path": search["path"],
            "cost": search["cost"],
            "steps": search["steps"],
        }

    # ---- decision and message depend on the request type (Phase 3, Section 3) ----
    if request_type == "Navigation_Only":
        response["decision"] = "completed"
        response["message"] = "Best route generated successfully."
    elif request_type == "Eligibility_Check":
        response["decision"] = "answered"
        response["message"] = "Eligibility query answered successfully."
    elif request_type == "Booking_or_Scheduling":
        response["decision"] = "accepted"
        response["message"] = "Booking assigned successfully."
    else:
        response["decision"] = "accepted"
        message = ("Your request has been accepted. You are assigned "
                   + response["assignment"]["room"] + " in slot "
                   + str(response["assignment"]["slot"]) + ".")
        if "Search" in module_outputs:
            message = message + " Please follow the recommended route."
        response["message"] = message

    return response