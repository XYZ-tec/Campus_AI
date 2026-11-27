"""
modules/csp.py
==============
Constraint Satisfaction Problem scheduler.

The scheduler assigns a compatible room and a slot (1-4). It uses domains,
constraints and backtracking. Existing reservations are demonstration data;
they make conflicts visible and can be edited for a different campus setup.
The Logic / KB module must approve a request before this module is called.
"""

from core.constants import new_csp_output, VALID_SLOTS

ROOM_DOMAINS = {
    "AI_Lab_Support": ["AI_Lab", "Science_Block"],
    "Viva": ["Seminar_Room", "Exam_Hall"],
    "Access": ["AI_Lab", "Library"],
    "Maintenance": ["Science_Block", "Admin_Block"],
    "Emergency_Help": ["Medical_Center", "Admin_Block"],
}

                                                                           
                                                                            
EXISTING_RESERVATIONS = [
    {"room": "AI_Lab", "slot": 1, "group_id": "G1"},
    {"room": "AI_Lab", "slot": 2, "group_id": "G2"},
    {"room": "Seminar_Room", "slot": 1, "group_id": "G3"},
    {"room": "Exam_Hall", "slot": 2, "group_id": "G4"},
    {"room": "Science_Block", "slot": 1, "group_id": "G5"},
]


def ordered_slots(preferred_slot, priority):
    """Order slot values so the preferred slot is tried first, then alternatives."""
    if preferred_slot in VALID_SLOTS:
        slots = list(VALID_SLOTS)
        start = slots.index(preferred_slot)
        ordered = slots[start:] + slots[:start]
    else:
        ordered = list(VALID_SLOTS)
    if priority == "urgent":
        ordered = sorted(ordered, key=lambda slot: (slot != preferred_slot, slot))
    return ordered


def is_consistent(room, slot, group_id):
    """Check room availability and prevent the same group booking two resources in one slot."""
    for reservation in EXISTING_RESERVATIONS:
        if reservation["room"] == room and reservation["slot"] == slot:
            return False
        if group_id and reservation["group_id"] == group_id and reservation["slot"] == slot:
            return False
    return True


def backtrack(variables, domains, assignment, group_id):
    """Assign one variable at a time and backtrack when a constraint is violated."""
    if len(assignment) == len(variables):
        return dict(assignment)
    variable = variables[len(assignment)]
    for value in domains[variable]:
        candidate = dict(assignment)
        candidate[variable] = value
        if variable == "slot" and not is_consistent(candidate["room"], value, group_id):
            continue
        result = backtrack(variables, domains, candidate, group_id)
        if result is not None:
            return result
    return None


def schedule_request(request, priority="normal"):
    """Find a conflict-free room and slot for an already-authorized request."""
    output = new_csp_output()
    category = request.get("category", "")
    if category not in ROOM_DOMAINS:
        output["decision"] = "rejected"
        output["notes"] = "No room domain is defined for this service category."
        return output

    preferred = request.get("preferred_slot")
    rooms = list(ROOM_DOMAINS[category])
    slots = ordered_slots(preferred, priority)
    domains = {"room": rooms, "slot": slots}
    assignment = backtrack(["room", "slot"], domains, {}, request.get("group_id", ""))

    if assignment is None:
        output["decision"] = "rejected"
        output["notes"] = "All compatible rooms and slots are occupied or conflict with another booking."
        return output

    output["decision"] = "accepted"
    output["assigned_room"] = assignment["room"]
    output["assigned_slot"] = assignment["slot"]
    output["destination"] = assignment["room"]
    if preferred and assignment["slot"] != preferred:
        output["notes"] = ("Preferred slot " + str(preferred)
                           + " was unavailable. Slot " + str(assignment["slot"])
                           + " is the next feasible conflict-free assignment.")
    else:
        output["notes"] = "A compatible room and conflict-free slot were assigned."
    return output
