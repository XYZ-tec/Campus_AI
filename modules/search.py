"""
modules/search.py
=================
Route finding on the campus graph.

Handout reference: Phase 2, Sections 4 to 10.
  - Operational mode (Sec 4, 6, 7): find_route() picks ONE algorithm by the
    official policy and returns one route.
  - Comparison / demo mode (Sec 4, 8): compare_all() runs all nine algorithms.

Every algorithm has the same shape:
    algorithm(graph, start, goal)  ->  result dictionary
The result dictionary is the handout's search output (Sec 10):
    algorithm_used, path, cost, steps
plus one academic field the handout allows: nodes_expanded.
If no route is found, path is an empty list.

The graph is a dictionary: graph["Hostel"] = {"Ground": 3, "Dhabba": 6, ...}
"""

import heapq

from core.constants import new_search_output
from data.campus_graph import build_graph, heuristic

DEPTH_LIMIT = 5         # used by DLS in comparison mode
BIG_NUMBER = 999999     # stands in for "infinity" in RBFS


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------
def path_cost(graph, path):
    """Add up the edge costs along a path."""
    total = 0
    for i in range(len(path) - 1):
        total = total + graph[path[i]][path[i + 1]]
    return total


def make_result(name, graph, path, expanded):
    """Build the standard search output. path=None means 'no route found'."""
    result = new_search_output()
    result["algorithm_used"] = name
    result["nodes_expanded"] = expanded
    if path is not None:
        result["path"] = path
        result["cost"] = path_cost(graph, path)
        result["steps"] = len(path) - 1
    return result


# ---------------------------------------------------------------------------
# Uninformed algorithms (no costs, no heuristic)
# ---------------------------------------------------------------------------
def bfs(graph, start, goal):
    """Breadth-First Search: shortest path by NUMBER OF STEPS."""
    frontier = [[start]]        # a queue of paths
    visited = [start]
    expanded = 0
    while len(frontier) > 0:
        path = frontier.pop(0)          # take from the front (queue)
        node = path[-1]
        expanded = expanded + 1
        if node == goal:
            return make_result("BFS", graph, path, expanded)
        for neighbour in sorted(graph[node]):
            if neighbour not in visited:
                visited.append(neighbour)
                frontier.append(path + [neighbour])
    return make_result("BFS", graph, None, expanded)


def dfs(graph, start, goal):
    """Depth-First Search: goes deep first, does NOT guarantee shortest path."""
    frontier = [[start]]        # a stack of paths
    visited = []
    expanded = 0
    while len(frontier) > 0:
        path = frontier.pop()           # take from the back (stack)
        node = path[-1]
        if node in visited:
            continue
        visited.append(node)
        expanded = expanded + 1
        if node == goal:
            return make_result("DFS", graph, path, expanded)
        for neighbour in sorted(graph[node], reverse=True):
            if neighbour not in visited:
                frontier.append(path + [neighbour])
    return make_result("DFS", graph, None, expanded)


def dls(graph, start, goal, limit):
    """Depth-Limited Search: DFS that never goes deeper than 'limit' steps."""
    frontier = [[start]]
    expanded = 0
    while len(frontier) > 0:
        path = frontier.pop()
        node = path[-1]
        expanded = expanded + 1
        if node == goal:
            return make_result("DLS", graph, path, expanded)
        if len(path) - 1 < limit:
            for neighbour in sorted(graph[node], reverse=True):
                if neighbour not in path:       # avoid loops on this path
                    frontier.append(path + [neighbour])
    return make_result("DLS", graph, None, expanded)


def ids(graph, start, goal):
    """Iterative Deepening Search: run DLS with limit 0, 1, 2, ... until found."""
    total_expanded = 0
    for limit in range(len(graph)):
        result = dls(graph, start, goal, limit)
        total_expanded = total_expanded + result["nodes_expanded"]
        if len(result["path"]) > 0:
            result["algorithm_used"] = "IDS"
            result["nodes_expanded"] = total_expanded
            return result
    return make_result("IDS", graph, None, total_expanded)


def join_paths(forward_path, backward_path):
    """forward_path goes start -> meeting node, backward_path goes goal -> meeting node.
    Reverse the second one and glue them together."""
    second_half = list(backward_path)
    second_half.reverse()
    return forward_path + second_half[1:]       # [1:] skips the meeting node (already in forward_path)


def bidirectional_bfs(graph, start, goal):
    """Two BFS searches, one from start and one from goal, until they meet."""
    if start == goal:
        return make_result("Bidirectional BFS", graph, [start], 1)

    forward_paths = {start: [start]}    # node -> path from start to that node
    backward_paths = {goal: [goal]}     # node -> path from goal to that node
    forward_queue = [start]
    backward_queue = [goal]
    expanded = 0

    while len(forward_queue) > 0 and len(backward_queue) > 0:
        # expand one node from the start side
        node = forward_queue.pop(0)
        expanded = expanded + 1
        for neighbour in sorted(graph[node]):
            if neighbour not in forward_paths:
                forward_paths[neighbour] = forward_paths[node] + [neighbour]
                forward_queue.append(neighbour)
                if neighbour in backward_paths:
                    full_path = join_paths(forward_paths[neighbour], backward_paths[neighbour])
                    return make_result("Bidirectional BFS", graph, full_path, expanded)

        # expand one node from the goal side
        node = backward_queue.pop(0)
        expanded = expanded + 1
        for neighbour in sorted(graph[node]):
            if neighbour not in backward_paths:
                backward_paths[neighbour] = backward_paths[node] + [neighbour]
                backward_queue.append(neighbour)
                if neighbour in forward_paths:
                    full_path = join_paths(forward_paths[neighbour], backward_paths[neighbour])
                    return make_result("Bidirectional BFS", graph, full_path, expanded)

    return make_result("Bidirectional BFS", graph, None, expanded)


# ---------------------------------------------------------------------------
# Weighted / informed algorithms
# ---------------------------------------------------------------------------
def ucs(graph, start, goal):
    """Uniform Cost Search: always expand the cheapest path so far.
    Needs no heuristic, always finds the cheapest route."""
    frontier = [(0, [start])]           # (cost so far, path), kept as a heap
    explored = []
    expanded = 0
    while len(frontier) > 0:
        cost, path = heapq.heappop(frontier)    # pops the smallest cost
        node = path[-1]
        if node in explored:
            continue
        explored.append(node)
        expanded = expanded + 1
        if node == goal:
            return make_result("UCS", graph, path, expanded)
        for neighbour in graph[node]:
            if neighbour not in explored:
                new_cost = cost + graph[node][neighbour]
                heapq.heappush(frontier, (new_cost, path + [neighbour]))
    return make_result("UCS", graph, None, expanded)


def greedy(graph, start, goal):
    """Greedy Best-First: only looks at the heuristic h(n). Fast, but NOT always cheapest."""
    frontier = [(heuristic(start, goal), [start])]
    explored = []
    expanded = 0
    while len(frontier) > 0:
        h, path = heapq.heappop(frontier)
        node = path[-1]
        if node in explored:
            continue
        explored.append(node)
        expanded = expanded + 1
        if node == goal:
            return make_result("Greedy Best-First", graph, path, expanded)
        for neighbour in graph[node]:
            if neighbour not in explored:
                heapq.heappush(frontier, (heuristic(neighbour, goal), path + [neighbour]))
    return make_result("Greedy Best-First", graph, None, expanded)


def a_star(graph, start, goal):
    """A*: expands the path with the smallest f = g + h
    (g = real cost so far, h = straight-line estimate to the goal)."""
    frontier = [(heuristic(start, goal), 0, [start])]   # (f, g, path)
    explored = []
    expanded = 0
    while len(frontier) > 0:
        f, g, path = heapq.heappop(frontier)
        node = path[-1]
        if node in explored:
            continue
        explored.append(node)
        expanded = expanded + 1
        if node == goal:
            return make_result("A*", graph, path, expanded)
        for neighbour in graph[node]:
            if neighbour not in explored:
                new_g = g + graph[node][neighbour]
                new_f = new_g + heuristic(neighbour, goal)
                heapq.heappush(frontier, (new_f, new_g, path + [neighbour]))
    return make_result("A*", graph, None, expanded)


def rbfs_search(graph, goal, path, g, node_f, f_limit):
    """Recursive part of RBFS.
    Returns three things: (path found or None, updated f value, nodes expanded)."""
    node = path[-1]
    if node == goal:
        return path, node_f, 1
    expanded = 1

    # build the children as small lists: [f, g, name]
    children = []
    for neighbour in graph[node]:
        if neighbour not in path:
            child_g = g + graph[node][neighbour]
            child_f = child_g + heuristic(neighbour, goal)
            if child_f < node_f:
                child_f = node_f        # a child never gets a smaller f than its parent
            children.append([child_f, child_g, neighbour])

    if len(children) == 0:
        return None, BIG_NUMBER, expanded

    while True:
        children.sort()                 # best (smallest f) child first
        best = children[0]
        if best[0] > f_limit:
            return None, best[0], expanded

        if len(children) > 1:
            alternative = children[1][0]
        else:
            alternative = BIG_NUMBER
        new_limit = f_limit
        if alternative < new_limit:
            new_limit = alternative

        found, new_f, used = rbfs_search(graph, goal, path + [best[2]], best[1], best[0], new_limit)
        expanded = expanded + used
        best[0] = new_f                 # remember the backed-up f value
        if found is not None:
            return found, new_f, expanded


def rbfs(graph, start, goal):
    """Recursive Best-First Search: A*-like, but uses very little memory."""
    start_f = heuristic(start, goal)
    found, final_f, expanded = rbfs_search(graph, goal, [start], 0, start_f, BIG_NUMBER)
    return make_result("RBFS", graph, found, expanded)


# ---------------------------------------------------------------------------
# Operational mode (Phase 2, Sections 6.2, 7.1, 7.2): the official policy
# ---------------------------------------------------------------------------
def find_route(source, destination, graph_type="weighted", heuristic_available=True):
    """Pick ONE algorithm by the official project rule:
         unweighted graph                    -> BFS
         weighted graph with heuristic       -> A*
         weighted graph without heuristic    -> UCS
    """
    if graph_type == "unweighted":
        graph = build_graph(weighted=False)
    else:
        graph = build_graph(weighted=True)

    if source not in graph or destination not in graph:
        return make_result("None", graph, None, 0)     # invalid node -> no route

    if graph_type == "unweighted":
        return bfs(graph, source, destination)
    if heuristic_available:
        return a_star(graph, source, destination)
    return ucs(graph, source, destination)


# ---------------------------------------------------------------------------
# Comparison / demo mode (Phase 2, Sections 4 and 8.2)
# ---------------------------------------------------------------------------
def compare_all(source, destination):
    """Run all nine algorithms on the weighted graph and return a list of results.
    Costs are in walking minutes, so they can be compared fairly. BFS, DFS, DLS,
    IDS and Bidirectional BFS ignore the weights when choosing, which is exactly
    why they can return a more expensive route than UCS and A*."""
    graph = build_graph(weighted=True)
    results = []
    results.append(bfs(graph, source, destination))
    results.append(dfs(graph, source, destination))
    results.append(dls(graph, source, destination, DEPTH_LIMIT))
    results.append(ids(graph, source, destination))
    results.append(bidirectional_bfs(graph, source, destination))
    results.append(ucs(graph, source, destination))
    results.append(greedy(graph, source, destination))
    results.append(a_star(graph, source, destination))
    results.append(rbfs(graph, source, destination))
    return results