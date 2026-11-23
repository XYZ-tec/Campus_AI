"""
data/knowledge_base.py
======================
The facts and rules of the Logic / Knowledge Base module.

Source: the instructor's FOL diagram (project document, Section 3.4).
Facts and rules are plain Python data, so adding a new person is just
adding one line to FACTS.

How to read the notation:
  a fact is a tuple:   ("Teaches", "DrKhan", "AI")      means Teaches(DrKhan, AI)
  in a rule, a name that starts with a lowercase letter is a VARIABLE
  (like x). Names that start with a capital letter are constants.
"""

# ---- Facts from the instructor's diagram ----
FACTS = [
    ("Teaches", "DrKhan", "AI"),
    ("Enrolled", "Ali", "AI"),
    ("Student", "Sara"),
    ("Student", "Ali"),
    ("Completed", "Ali", "ProgrammingFundamentals"),
]

RULES = [
    # ---- R1 to R4: exactly as drawn in the instructor's diagram ----
    {"name": "R1",
     "if": [("Student", "x"), ("Completed", "x", "ProgrammingFundamentals")],
     "then": ("Eligible", "x", "AI")},
    {"name": "R2",
     "if": [("Teaches", "x", "AI")],
     "then": ("Instructor", "x", "AI")},
    {"name": "R3",
     "if": [("Enrolled", "x", "AI")],
     "then": ("UsesLab", "x", "Lab1")},
    {"name": "R4",
     "if": [("Instructor", "x", "AI")],
     "then": ("UsesLab", "x", "Lab1")},

    # ---- R5 to R8: OUR additions. The diagram only covers lab use and
    # ---- eligibility, but booking requests need a rule that says who may
    # ---- request which service. CanRequest(person, category) is that rule.
    {"name": "R5",
     "if": [("Eligible", "x", "AI")],
     "then": ("CanRequest", "x", "Viva")},
    {"name": "R6",
     "if": [("Instructor", "x", "AI")],
     "then": ("CanRequest", "x", "Viva")},
    {"name": "R7",
     "if": [("UsesLab", "x", "Lab1")],
     "then": ("CanRequest", "x", "AI_Lab_Support")},
    {"name": "R8",
     "if": [("UsesLab", "x", "Lab1")],
     "then": ("CanRequest", "x", "Access")},
]

# OUR decision: these categories are open to every user (an emergency request
# must never be blocked by a rule), so the gate does not check the KB for them.
OPEN_CATEGORIES = ["Maintenance", "Emergency_Help"]