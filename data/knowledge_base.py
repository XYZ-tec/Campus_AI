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

                                               
FACTS = [
    ("Teaches", "DrKhan", "AI"),
    ("Enrolled", "Ali", "AI"),
    ("Student", "Sara"),
    ("Student", "Ali"),
    ("Completed", "Ali", "ProgrammingFundamentals"),
]

RULES = [
                                                                      
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

                                                                             
                                                                               
OPEN_CATEGORIES = ["Maintenance", "Emergency_Help"]