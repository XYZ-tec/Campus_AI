"""
tests/test_search.py
Run from the campus_ai folder with:   python -m pytest tests
"""

from data.campus_graph import COORDS, check_heuristic
from modules.search import find_route, compare_all


def test_heuristic_is_safe_for_astar():
    assert check_heuristic() == True


def test_policy_weighted_uses_astar():
    result = find_route("Hostel", "AI_Lab")
    assert result["algorithm_used"] == "A*"
    assert result["path"] == ["Hostel", "Cafeteria", "Science_Block", "AI_Lab"]
    assert result["cost"] == 6
    assert result["steps"] == 3


def test_policy_unweighted_uses_bfs():
    result = find_route("Hostel", "AI_Lab", graph_type="unweighted")
    assert result["algorithm_used"] == "BFS"
    assert result["steps"] == 3
    assert result["cost"] == 3                                                         


def test_policy_without_heuristic_uses_ucs():
    result = find_route("Hostel", "AI_Lab", heuristic_available=False)
    assert result["algorithm_used"] == "UCS"
    assert result["cost"] == 6


def test_invalid_node_gives_empty_path():
    result = find_route("Hostel", "Mars")
    assert result["path"] == []


def test_same_start_and_goal():
    result = find_route("Library", "Library")
    assert result["path"] == ["Library"]
    assert result["steps"] == 0


def test_ucs_astar_rbfs_agree_on_every_pair():
    for start in COORDS:
        for goal in COORDS:
            costs = {}
            for result in compare_all(start, goal):
                costs[result["algorithm_used"]] = result["cost"]
            assert costs["A*"] == costs["UCS"]
            assert costs["RBFS"] == costs["UCS"]


def test_map_has_13_places_and_19_edges():
    from data.campus_graph import EDGES
    assert len(COORDS) == 13
    assert len(EDGES) == 19


def test_every_algorithm_never_beats_ucs():
    for start in COORDS:
        for goal in COORDS:
            results = compare_all(start, goal)
            best = 0
            for result in results:
                if result["algorithm_used"] == "UCS":
                    best = result["cost"]
            for result in results:
                if len(result["path"]) > 0:
                    assert result["cost"] >= best