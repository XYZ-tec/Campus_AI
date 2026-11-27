# Smart Campus AI Decision Support and Automation System

AL2002 Artificial Intelligence Lab — Fall 2026

## Modules

- Structured CLI input and preprocessing
- Request router with five request pipelines
- ANN priority prediction: Perceptron binary baseline and MLP four-class model
- Forward-chaining Logic / Knowledge Base
- CSP room and slot allocation using domains, constraints and backtracking
- Campus navigation: BFS, DFS, DLS, IDS, Bidirectional BFS, UCS, Greedy Best-First, A* and RBFS
- Final response aggregation

The ANN training examples are synthetic demonstration data because no labelled campus dataset was supplied in the handout. ANN predicts priority only. It does not grant permission; Logic / KB must approve a request before CSP is executed.

## Requirements

Python 3.10 or later. The application modules use the Python standard library. `pytest` is needed only to run the tests.

## Run the application

Open a terminal in the `Campus_AI` project folder:

```bash
python -m pip install -r requirements.txt
python cli.py
```

## Run the web page

```bash
python web.py
```

Then open http://localhost:8000 in a browser. Press Ctrl + C in the terminal to stop it.

## Run tests

```bash
python -m pytest -v
```

## Compare all search algorithms

```bash
python search_demo.py
```

## Test one request using JSON

```bash
python api.py < request.json
```

## Request pipelines

| Request type | Pipeline |
|---|---|
| Navigation_Only | Search |
| Eligibility_Check | Logic_KB |
| Booking_or_Scheduling | Logic_KB → CSP → optional Search |
| Urgent_Service_Request | ANN → Logic_KB → CSP → optional Search |
| Full_Service_Request | ANN → Logic_KB → CSP → Search |

## Campus map

The predefined map contains 13 locations and 19 two-way weighted edges. BFS is selected for unweighted navigation, A* for weighted navigation when the heuristic is available, and UCS as the weighted fallback.

## Notes about demonstration data

`data/knowledge_base.py` contains the sample facts and rules used by the Logic / KB module. `modules/csp.py` contains editable sample reservations so that slot conflicts and backtracking can be demonstrated. Update these records to match the instructor's preferred campus schedule if additional reservation data is supplied.

## Example requests

Sample structured inputs are available in `examples/`. For example:

```bash
python api.py < examples/sample_full_request.json
```

## Before final submission

1. Run `python -m pytest -v` and keep a screenshot of the passing tests.
2. Run `python cli.py` and capture one screenshot for each request type.
3. Capture a full-service example showing ANN priority, Logic / KB approval, CSP assignment and A* route.
4. Update the report cover page with all group members' correct student IDs.
5. Zip the project using the exact filename format specified by your instructor.
6. Upload the ZIP and PDF report to Google Classroom.
