"""
data/campus_graph.py
====================
The campus map used by the Search module.

Source: the instructor's project document (AL2002 capstone, Section 3.6,
weighted campus graph). The document says the campus map is predefined
(Section 9), so we use it exactly: 13 locations, 19 two-way edges.

EDGES:   (place_a, place_b, walking_cost)
COORDS:  (x, y) of each place, as printed on the instructor's diagram.
         They are used only to build the A* heuristic.

Gap we had to fill: the document gives coordinates but does not say which
heuristic to use. Plain straight-line distance OVERESTIMATES on this map
(for example Main_Gate to Bus_Stop is 3 units apart but costs only 1),
and A* is only guaranteed to find the cheapest route if the heuristic never
overestimates. So we shrink the straight-line distance by a safe factor that
is calculated from the map itself (see calculate_heuristic_scale).
"""

import math

                                                                  
EDGES = [
    ("Admin_Block", "Student_Services", 1),
    ("Admin_Block", "Main_Gate", 4),
    ("Admin_Block", "Exam_Hall", 2),
    ("Main_Gate", "Parking", 2),
    ("Main_Gate", "Bus_Stop", 1),
    ("Main_Gate", "Hostel", 5),
    ("Parking", "Bus_Stop", 2),
    ("Parking", "Science_Block", 3),
    ("Student_Services", "Library", 2),
    ("Exam_Hall", "Seminar_Room", 1),
    ("Exam_Hall", "Science_Block", 3),
    ("Seminar_Room", "Science_Block", 2),
    ("Library", "AI_Lab", 3),
    ("Library", "Cafeteria", 2),
    ("AI_Lab", "Science_Block", 1),
    ("Cafeteria", "Science_Block", 3),
    ("Cafeteria", "Hostel", 2),
    ("Medical_Center", "Bus_Stop", 2),
    ("Medical_Center", "Hostel", 3),
]

COORDS = {
    "Admin_Block": (3, 5),
    "Student_Services": (6, 5),
    "Exam_Hall": (8, 5),
    "Main_Gate": (0, 4),
    "Parking": (2, 4),
    "Seminar_Room": (10, 4),
    "Library": (6, 2),
    "AI_Lab": (9, 2),
    "Medical_Center": (1, 1),
    "Bus_Stop": (0, 1),
    "Cafeteria": (4, 1),
    "Science_Block": (7, 1),
    "Hostel": (2, 0),
}


def build_graph(weighted=True):
    """Return the map as a dictionary: graph["Hostel"] = {"Cafeteria": 2, ...}.
    If weighted is False, every edge costs 1 (used by BFS)."""
    graph = {}
    for node in COORDS:
        graph[node] = {}
    for place_a, place_b, cost in EDGES:
        if weighted == False:
            cost = 1
        graph[place_a][place_b] = cost
        graph[place_b][place_a] = cost
    return graph


def straight_line_distance(node, goal):
    """Plain straight-line (Euclidean) distance between two places."""
    x1, y1 = COORDS[node]
    x2, y2 = COORDS[goal]
    return math.sqrt((x1 - x2) ** 2 + (y1 - y2) ** 2)


def calculate_heuristic_scale():
    """Find the biggest factor we can multiply straight-line distance by and
    still never overestimate. For each edge, cost / distance is the largest
    safe factor for that edge, so we take the smallest one over all edges."""
    scale = 1.0
    for place_a, place_b, cost in EDGES:
        ratio = cost / straight_line_distance(place_a, place_b)
        if ratio < scale:
            scale = ratio
    return scale


HEURISTIC_SCALE = calculate_heuristic_scale()


def heuristic(node, goal):
    """Estimated cost from node to goal, used by A*, Greedy and RBFS."""
    return HEURISTIC_SCALE * straight_line_distance(node, goal)


def check_heuristic():
    """A* is only optimal if the heuristic is consistent:
    h(a, goal) <= cost(a, b) + h(b, goal) for every edge and every goal.
    Returns True if that holds everywhere."""
    graph = build_graph(weighted=True)
    for goal in COORDS:
        for node_a in graph:
            for node_b in graph[node_a]:
                cost = graph[node_a][node_b]
                if heuristic(node_a, goal) > cost + heuristic(node_b, goal) + 0.000000001:
                    return False
    return True