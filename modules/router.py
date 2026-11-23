"""
modules/router.py
=================
Request Router: the control-flow brain of the platform.

Handout reference: Phase 1, Sections 7 and 8; Phase 3, Section 7.
Instructor document: Section 3.2.

The router does NOT solve the request. It only reads request_type and decides
which modules run, and in what order. It also owns the needs_* flags.
"""

from core.constants import PIPELINES, OPTIONAL_SEARCH_TYPES, new_router_output


def route_request(request):
    """Choose the pipeline for a valid request.
    Returns the router output dictionary, or None if the request type is
    not supported (the handout's 'ELSE: reject request')."""
    request_type = request["request_type"]
    if request_type not in PIPELINES:
        return None

    pipeline = list(PIPELINES[request_type])    # a copy, so the table is never changed

    # Booking and Urgent requests only get route guidance if the user told us
    # where they are (our decision: the handout just says "optional").
    if request_type in OPTIONAL_SEARCH_TYPES and request["current_location"] != "":
        pipeline.append("Search")

    output = new_router_output()
    output["request_id"] = request["request_id"]
    output["selected_pipeline"] = pipeline
    output["needs_ann"] = "ANN" in pipeline
    output["needs_logic"] = "Logic_KB" in pipeline
    output["needs_csp"] = "CSP" in pipeline
    output["needs_search"] = "Search" in pipeline
    return output