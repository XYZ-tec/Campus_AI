"""
modules/logic_kb.py
===================
Logic / Knowledge Base module: the rule-based gatekeeper before CSP.

Handout reference: Phase 3, Sections 10 and 11.5 (logic output, allowed flag).
Instructor document: Section 3.4 (FOL diagram).

Method: FORWARD CHAINING. Start with the known facts, apply every rule whose
conditions are all true, add the new facts it produces, and repeat until
nothing new appears. A query is "entailed" if it ends up among the facts.
We also remember which rule produced each new fact, so we can explain the answer.

Two ways to use the module:
  check_query(text)      Eligibility_Check requests: "Is UsesLab(DrKhan, Lab1) true?"
  check_request(request) Booking / Urgent / Full requests: may this person ask
                         for this category? (allowed = True or False)
"""

from core.constants import new_logic_output
from data.knowledge_base import FACTS, RULES, OPEN_CATEGORIES


                                                                             
                                               
                                                                             
def is_variable(term):
    """In a rule, a term starting with a lowercase letter is a variable (like x)."""
    return term[0].islower()


def squash(text):
    """Lowercase and remove spaces, underscores and hyphens, so that
    'dr khan', 'DrKhan' and 'DR-KHAN' all look the same."""
    text = str(text).lower()
    text = text.replace(" ", "")
    text = text.replace("_", "")
    text = text.replace("-", "")
    return text


def make_symbol_table():
    """Collect every name used in the facts and rules (not the variables)."""
    table = {}
    everything = list(FACTS)
    for rule in RULES:
        everything = everything + rule["if"] + [rule["then"]]
    for fact in everything:
        for symbol in fact:
            if not is_variable(symbol):
                table[squash(symbol)] = symbol
    return table


SYMBOL_TABLE = make_symbol_table()


def official_symbol(text):
    """Fix case and spaces of a name that exists in the KB ("dr khan" -> "DrKhan").
    A name the KB does not know is returned unchanged."""
    key = squash(text)
    if key in SYMBOL_TABLE:
        return SYMBOL_TABLE[key]
    return str(text).strip()


def format_fact(fact):
    """('Teaches', 'DrKhan', 'AI') -> 'Teaches(DrKhan, AI)'"""
    return fact[0] + "(" + ", ".join(fact[1:]) + ")"


def format_rule(rule):
    """Print a rule the way the diagram does, e.g. 'Teaches(x, AI) => Instructor(x, AI)'."""
    parts = []
    for premise in rule["if"]:
        parts.append(format_fact(premise))
    return " & ".join(parts) + " => " + format_fact(rule["then"])


def parse_fact(text):
    """Turn typed text like 'UsesLab(DrKhan, Lab1)' into the tuple
    ('UsesLab', 'DrKhan', 'Lab1'). Returns None if the text is not in that form."""
    text = str(text).strip()
    open_position = text.find("(")
    if open_position <= 0 or not text.endswith(")"):
        return None
    if text.count("(") != 1 or text.count(")") != 1:
        return None

    predicate = text[:open_position].strip()
    inside = text[open_position + 1:-1]
    arguments = []
    for piece in inside.split(","):
        piece = piece.strip()
        if piece == "":
            return None
        arguments.append(piece)
    return tuple([predicate] + arguments)


def normalize_fact(fact):
    """Apply official_symbol to every part of a fact."""
    cleaned = []
    for symbol in fact:
        cleaned.append(official_symbol(symbol))
    return tuple(cleaned)


                                                                             
                      
                                                                             
def match_premise(premise, fact, bindings):
    """Try to make one rule condition fit one known fact.
    bindings says what each variable is already set to, e.g. {"x": "Ali"}.
    Returns the (possibly extended) bindings, or None if they do not fit."""
    if len(premise) != len(fact) or premise[0] != fact[0]:
        return None

    new_bindings = dict(bindings)                                               
    for position in range(1, len(premise)):
        wanted = premise[position]
        actual = fact[position]
        if is_variable(wanted):
            if wanted in new_bindings:
                if new_bindings[wanted] != actual:
                    return None
            else:
                new_bindings[wanted] = actual
        elif wanted != actual:
            return None
    return new_bindings


def find_matches(premises, known_facts):
    """Find every way to satisfy ALL conditions of a rule using the known facts.
    Returns a list of (bindings, facts_used) pairs."""
    matches = [({}, [])]
    for premise in premises:
        new_matches = []
        for bindings, used_facts in matches:
            for fact in known_facts:
                new_bindings = match_premise(premise, fact, bindings)
                if new_bindings is not None:
                    new_matches.append((new_bindings, used_facts + [fact]))
        matches = new_matches
    return matches


def fill_in(pattern, bindings):
    """Replace the variables in a rule's conclusion with their values."""
    filled = []
    for term in pattern:
        if term in bindings:
            filled.append(bindings[term])
        else:
            filled.append(term)
    return tuple(filled)


def forward_chain(facts, rules):
    """Apply the rules again and again until no new fact can be derived.
    Returns (known_facts, how): how[new_fact] = (rule, facts that were used)."""
    known_facts = list(facts)
    how = {}
    found_something_new = True
    while found_something_new:
        found_something_new = False
        for rule in rules:
            for bindings, used_facts in find_matches(rule["if"], known_facts):
                new_fact = fill_in(rule["then"], bindings)
                if new_fact not in known_facts:
                    known_facts.append(new_fact)
                    how[new_fact] = (rule, used_facts)
                    found_something_new = True
    return known_facts, how


def explain(goal, how):
    """Walk back from the goal to the original facts and describe every step,
    listed from the starting facts to the conclusion."""
    steps = []
    to_explain = [goal]
    already_done = []
    while len(to_explain) > 0:
        fact = to_explain.pop()
        if fact in already_done:
            continue
        already_done.append(fact)
        if fact in how:
            rule, used_facts = how[fact]
            steps.append(rule["name"] + ": " + format_rule(rule)
                         + " gives " + format_fact(fact))
            for used in used_facts:
                to_explain.append(used)
        else:
            steps.append("Known fact: " + format_fact(fact))
    steps.reverse()
    return steps


def prove(goal):
    """Decide whether the goal fact follows from the knowledge base.
    Returns the standard logic output (core/constants.py)."""
    known_facts, how = forward_chain(FACTS, RULES)
    output = new_logic_output()
    if goal in known_facts:
        output["allowed"] = True
        output["entailed"] = True
        output["explanation"] = explain(goal, how)
    else:
        output["explanation"] = [format_fact(goal)
                                 + " cannot be derived from the knowledge base."]
    return output


                                                                             
                                           
                                                                             
def registered_roles(name):
    """Return the roles that the Knowledge Base proves for this person."""
    person = official_symbol(name)
    known_facts, _ = forward_chain(FACTS, RULES)
    roles = []
    for fact in known_facts:
        if fact[0] == "Student" and len(fact) == 2 and fact[1] == person:
            roles.append("student")
        elif fact[0] == "Instructor" and len(fact) >= 2 and fact[1] == person:
            roles.append("instructor")
        elif fact[0] == "Staff" and len(fact) == 2 and fact[1] == person:
            roles.append("staff")
    return roles


def verify_role(name, role):
    """Check that the role supplied by the user matches a role proved by the KB."""
    output = new_logic_output()
    person = official_symbol(name)
    roles = registered_roles(person)
    entered_role = str(role).strip().lower()
    if entered_role in roles:
        output["allowed"] = True
        output["entailed"] = True
        output["explanation"] = [
            "Role verified: " + format_fact((roles_predicate(entered_role), person))
        ]
    else:
        output["allowed"] = False
        output["entailed"] = False
        if roles:
            registered = ", ".join(roles)
            output["explanation"] = [
                "Role mismatch. " + person + " is registered as " + registered
                + ", not " + entered_role + "."
            ]
        else:
            output["explanation"] = [
                person + " is not registered with a role in the knowledge base."
            ]
    return output


def roles_predicate(role):
    """Map a normalized role name to its Knowledge Base predicate."""
    return {"student": "Student", "instructor": "Instructor", "staff": "Staff"}[role]


def check_query(query_text):
    """Eligibility_Check: is the typed query entailed by the knowledge base?"""
    fact = parse_fact(query_text)
    if fact is None:
        output = new_logic_output()
        output["explanation"] = ["The query must look like Predicate(Name, Name)."]
        return output
    return prove(normalize_fact(fact))


def check_request(request):
    """Booking / Urgent / Full requests: is this person allowed to ask for this
    category? This is the 'Eligible / Allowed?' decision in the project flow."""
    category = request["category"]
    if request.get("role"):
        identity = verify_role(request["name"], request["role"])
        if not identity["allowed"]:
            return identity
    if category in OPEN_CATEGORIES:
        output = new_logic_output()
        output["allowed"] = True
        output["entailed"] = True
        output["explanation"] = ["Category " + category
                                 + " is open to every user, so no rule check is needed."]
        return output
    goal = ("CanRequest", official_symbol(request["name"]), category)
    return prove(goal)