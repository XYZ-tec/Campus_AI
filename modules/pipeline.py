"""
modules/pipeline.py
===================
Central integration layer for the Smart Campus AI system.

The router selects modules. ANN predicts priority, Logic / KB validates
permission, CSP allocates resources, Search finds a route, and the final
response combines only the outputs produced by the selected pipeline.
"""

from modules.preprocessing import preprocess
from modules.router import route_request
from modules.ann import predict_priority, TARGET_ROOMS
from modules.logic_kb import check_query, check_request
from modules.csp import schedule_request
from modules.search import find_route
from modules.final_response import build_rejection, build_final_response


def process_request(raw_request):
    """Validate one raw request, execute its routed modules, and return one response."""
    request, errors = preprocess(raw_request)
    if errors:
        return build_rejection(
            request["request_id"], "Invalid request: " + "; ".join(errors)
        )

    router_output = route_request(request)
    if router_output is None:
        return build_rejection(request["request_id"], "Request type is not supported.")

    module_outputs = {}
    assigned_destination = request.get("destination", "")

    for module_name in router_output["selected_pipeline"]:
        if module_name == "ANN":
            module_outputs["ANN"] = predict_priority(request)

        elif module_name == "Logic_KB":
            if request["request_type"] == "Eligibility_Check":
                module_outputs["Logic_KB"] = check_query(request["query"])
                break
            module_outputs["Logic_KB"] = check_request(request)
            if not module_outputs["Logic_KB"]["allowed"]:
                break

        elif module_name == "CSP":
            priority = "normal"
            if "ANN" in module_outputs:
                priority = module_outputs["ANN"]["final_priority"]
            module_outputs["CSP"] = schedule_request(request, priority)
            if module_outputs["CSP"]["decision"] != "accepted":
                break
            assigned_destination = module_outputs["CSP"]["destination"]

        elif module_name == "Search":
            destination = assigned_destination
            if not destination:
                destination = TARGET_ROOMS.get(request.get("category", ""), "")
            module_outputs["Search"] = find_route(
                request["current_location"], destination
            )

    return build_final_response(request, module_outputs)
