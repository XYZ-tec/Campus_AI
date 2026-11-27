def display_final_response(response):
    """Display the final request result in a readable terminal format."""
    print("\nRequest Result")
    print("Status: " + str(response.get("decision", "unknown")).replace("_", " ").title())
    print("Request ID: " + str(response.get("request_id", "N/A")))

    priority = response.get("priority") or {}
    if priority:
        print("\nPriority")
        print("Predicted priority: " + str(priority.get("final_priority", "N/A")).title())
        print("Urgency baseline: " + str(priority.get("binary_priority", "N/A")).replace("_", " ").title())
        print("Confidence: " + str(priority.get("confidence", "N/A")))

    eligibility = response.get("eligibility") or {}
    if eligibility:
        print("\nEligibility")
        allowed = eligibility.get("allowed", eligibility.get("entailed"))
        print("Result: " + ("Approved" if allowed else "Not approved"))
        if eligibility.get("explanation"):
            print("Explanation: " + str(eligibility["explanation"]))

    assignment = response.get("assignment") or {}
    if assignment:
        print("\nAssignment")
        print("Room: " + str(assignment.get("room", "N/A")))
        print("Slot: " + str(assignment.get("slot", "N/A")))
        if assignment.get("notes"):
            print("Note: " + str(assignment["notes"]))

    route = response.get("route") or {}
    if route:
        print("\nRoute")
        print("Algorithm: " + str(route.get("algorithm", "N/A")))
        print("Path: " + " -> ".join(route.get("path", [])))
        print("Total cost: " + str(route.get("cost", "N/A")))
        print("Steps: " + str(route.get("steps", "N/A")))

    if response.get("message"):
        print("\nMessage: " + str(response["message"]))


def display_search_comparison(results):
    """Display search algorithm results as readable summaries instead of JSON."""
    print("\nSearch Algorithm Comparison")
    for result in results:
        print("\n" + str(result.get("algorithm_used", "Search")))
        path = result.get("path", [])
        print("Route: " + (" -> ".join(path) if path else "No route found"))
        print("Cost: " + str(result.get("cost", "N/A")))
        print("Steps: " + str(result.get("steps", "N/A")))
        print("Nodes explored: " + str(result.get("nodes_expanded", "N/A")))
