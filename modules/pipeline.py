"""
pipeline.py
===========
The ONE function that runs a whole request:  process_request(raw_request).
The CLI and (later) the UI both call this function, so they behave identically.

Handout reference: Phase 3, Sections 1, 2 and 5 (module-to-module flow).

Flow:  Preprocessing -> Router -> selected modules (in order) -> Final Response
"""

from modules.preprocessing import preprocess
from modules.router import route_request
from modules.logic_kb import check_query, check_request
from modules.search import find_route
from modules.final_response import build_rejection, build_final_response

# Modules that exist so far. We add CSP and ANN as we build them.
READY_MODULES = ["Search", "Logic_KB"]


def process_request(raw_request):
    """Run one request through the full system and return the final response."""
    request, errors = preprocess(raw_request)
    if len(errors) > 0:
        return build_rejection(request["request_id"],
                               "Invalid request: " + "; ".join(errors))

    router_output = route_request(request)
    if router_output is None:
        return build_rejection(request["request_id"], "Request type is not supported.")

    module_outputs = {}
    for module_name in router_output["selected_pipeline"]:
        if module_name not in READY_MODULES:
            return build_rejection(request["request_id"],
                                   module_name + " module is not built yet.")
        if module_name == "Logic_KB":
            if request["request_type"] == "Eligibility_Check":
                module_outputs["Logic_KB"] = check_query(request["query"])
            else:
                module_outputs["Logic_KB"] = check_request(request)
                if module_outputs["Logic_KB"]["allowed"] == False:
                    break           # not allowed: stop here, never reach CSP
        if module_name == "Search":
            module_outputs["Search"] = find_route(request["current_location"],
                                                  request["destination"])

    return build_final_response(request, module_outputs)