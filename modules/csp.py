"""
modules/csp.py
==============
Constraint Satisfaction Problem scheduler.

Instructor document: Section 3.5 (CSP diagram) and the master diagram
("MRV / DH / LCV, Forward Checking / constraints").

A CSP has variables, domains (possible values) and constraints (rules).
One solver is used for two problems:
  1. A normal request:  variables = room and slot
  2. A viva request:    variables = groups G1-G6 from the CSP diagram, values = slots

The solver is backtracking search with:
  MRV  - choose the variable with the fewest values left
  DH   - if there is a tie, choose the variable with the most constraints
  LCV  - try first the value that removes the fewest values from neighbours
  Forward checking - after each choice, remove clashing values from
                     neighbours; if a neighbour has no values left, go back

The Logic / KB module must approve a request before this module is called.
"""

from core.constants import new_csp_output, VALID_SLOTS

ROOM_DOMAINS = {
    "AI_Lab_Support": ["AI_Lab"],
    "Viva": ["Seminar_Room", "Exam_Hall"],
    "Access": ["AI_Lab", "Library"],
    "Maintenance": ["Science_Block", "Admin_Block"],
    "Emergency_Help": ["Medical_Center", "Admin_Block"],
}

# Bookings that exist when the program starts (demonstration data).
SAMPLE_RESERVATIONS = [
    {"room": "AI_Lab", "slot": 1, "booked_by": "AI_Class"},
    {"room": "AI_Lab", "slot": 2, "booked_by": "Robotics_Class"},
    {"room": "Seminar_Room", "slot": 1, "booked_by": "Guest_Talk"},
    {"room": "Exam_Hall", "slot": 2, "booked_by": "Midterm_Exam"},
    {"room": "Science_Block", "slot": 1, "booked_by": "Physics_Lab"},
]

# New bookings are added here while the program runs (no double booking).
reservations = list(SAMPLE_RESERVATIONS)


def not_equal(slot_a, slot_b):
    """Constraint: the two groups must not get the same slot."""
    return slot_a != slot_b


def before(slot_a, slot_b):
    """Constraint: the first group's slot must come before the second group's slot."""
    return slot_a < slot_b


# The CSP diagram: (group_a, group_b, rule)
GROUPS = ["G1", "G2", "G3", "G4", "G5", "G6"]
GROUP_CONSTRAINTS = [
    ("G1", "G2", not_equal),
    ("G1", "G4", not_equal),
    ("G2", "G4", not_equal),
    ("G1", "G3", not_equal),    # examiner clash
    ("G2", "G5", not_equal),    # supervisor clash
    ("G3", "G5", not_equal),
    ("G3", "G6", not_equal),
    ("G5", "G6", not_equal),
    ("G4", "G3", before),       # precedence: G4 before G3
]


def reset_reservations():
    """Remove the bookings made during this run (used by the tests)."""
    reservations.clear()
    reservations.extend(SAMPLE_RESERVATIONS)


def room_is_free(room, slot):
    """Constraint: a room can hold only one booking in a slot."""
    for booking in reservations:
        if booking["room"] == room and booking["slot"] == slot:
            return False
    return True


def is_busy(booked_by, slot):
    """True if this person or group already has a booking in this slot."""
    for booking in reservations:
        if booking["booked_by"] == booked_by and booking["slot"] == slot:
            return True
    return False


# ---------------------------------------------------------------------------
# General CSP solver
# ---------------------------------------------------------------------------
def neighbours(variable, constraints):
    """Return the variables that share a constraint with this variable."""
    result = []
    for first, second, rule in constraints:
        if first == variable and second not in result:
            result.append(second)
        if second == variable and first not in result:
            result.append(first)
    return result


def values_agree(var_a, value_a, var_b, value_b, constraints):
    """Check every constraint between var_a and var_b for these two values."""
    for first, second, rule in constraints:
        if first == var_a and second == var_b and not rule(value_a, value_b):
            return False
        if first == var_b and second == var_a and not rule(value_b, value_a):
            return False
    return True


def select_variable(variables, domains, assignment, constraints):
    """MRV: fewest values left. DH (tie-break): most unassigned neighbours."""
    best = None
    for variable in variables:
        if variable in assignment:
            continue
        values_left = len(domains[variable])
        degree = 0
        for other in neighbours(variable, constraints):
            if other not in assignment:
                degree = degree + 1
        if best is None or (values_left, -degree) < best[0]:
            best = ((values_left, -degree), variable)
    return best[1]


def order_values(variable, domains, assignment, constraints):
    """LCV: try first the value that rules out the fewest neighbour values.
    Values that rule out the same number keep their original order."""
    def ruled_out(value):
        count = 0
        for other in neighbours(variable, constraints):
            if other in assignment:
                continue
            for other_value in domains[other]:
                if not values_agree(variable, value, other, other_value, constraints):
                    count = count + 1
        return count
    return sorted(domains[variable], key=ruled_out)


def forward_check(variable, value, domains, assignment, constraints):
    """Remove neighbour values that clash with variable=value.
    Returns the new domains, or None if a neighbour has no value left."""
    new_domains = dict(domains)
    new_domains[variable] = [value]
    for other in neighbours(variable, constraints):
        if other in assignment:
            continue
        kept = []
        for other_value in domains[other]:
            if values_agree(variable, value, other, other_value, constraints):
                kept.append(other_value)
        if len(kept) == 0:
            return None
        new_domains[other] = kept
    return new_domains


def backtrack(variables, domains, assignment, constraints):
    """Assign one variable at a time; undo and try the next value on a dead end."""
    if len(assignment) == len(variables):
        return dict(assignment)
    variable = select_variable(variables, domains, assignment, constraints)
    for value in order_values(variable, domains, assignment, constraints):
        new_domains = forward_check(variable, value, domains, assignment, constraints)
        if new_domains is None:
            continue
        assignment[variable] = value
        result = backtrack(variables, new_domains, assignment, constraints)
        if result is not None:
            return result
        del assignment[variable]
    return None


def solve(variables, domains, constraints):
    """Start the backtracking search with an empty assignment."""
    return backtrack(variables, domains, {}, constraints)


# ---------------------------------------------------------------------------
# The two scheduling problems
# ---------------------------------------------------------------------------
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


def schedule_service(rooms, slots, booked_by):
    """Normal request: variables are room and slot.
    Constraint: the chosen room must be free in the chosen slot."""
    free_slots = [slot for slot in slots if not is_busy(booked_by, slot)]
    domains = {"room": list(rooms), "slot": free_slots}
    constraints = [("room", "slot", room_is_free)]
    return solve(["room", "slot"], domains, constraints)


def group_slot(group):
    """Return the slot of a viva this group already booked, or None."""
    for booking in reservations:
        if booking["booked_by"] == group and booking["room"] in ROOM_DOMAINS["Viva"]:
            return booking["slot"]
    return None


def schedule_viva(group, slots):
    """Viva request: solve the CSP diagram for all groups G1-G6.
    Slots are tried in preference order; a slot is accepted only if a viva room
    is free AND every group can still be scheduled without breaking a constraint."""
    for slot in slots:
        free_rooms = [room for room in ROOM_DOMAINS["Viva"] if room_is_free(room, slot)]
        if len(free_rooms) == 0 or is_busy(group, slot):
            continue
        domains = {}
        for other in GROUPS:
            booked = group_slot(other)
            domains[other] = [booked] if booked is not None else list(VALID_SLOTS)
        domains[group] = [slot]
        if solve(GROUPS, domains, GROUP_CONSTRAINTS) is not None:
            return {"room": free_rooms[0], "slot": slot}
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
    slots = ordered_slots(preferred, priority)
    group = request.get("group_id", "")
    booked_by = group or request.get("name", "")

    if category == "Viva" and group in GROUPS:
        assignment = schedule_viva(group, slots)
    else:
        assignment = schedule_service(ROOM_DOMAINS[category], slots, booked_by)

    if assignment is None:
        output["decision"] = "rejected"
        output["notes"] = "All compatible rooms and slots are occupied or conflict with another booking."
        return output

    reservations.append({"room": assignment["room"], "slot": assignment["slot"],
                         "booked_by": booked_by})
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
