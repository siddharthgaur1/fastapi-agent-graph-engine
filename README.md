# Minimal Agent Workflow Engine

A small FastAPI service that runs **agent-style workflows as directed graphs
of Python tools** — sequential steps, conditional branching, and looping —
with full execution logging, so every workflow run is inspectable after the
fact, not just its final output.

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)
[![Python 3.10+](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/downloads/)

## Problem → Approach → Result

**Problem.** Most "agent workflow" toys are either a single linear chain
(no branching, no loops) or a full-blown orchestration framework that's
overkill for a small automation service. There's a gap for something that
supports state mutation, conditional branching, and bounded looping, with
zero external dependencies beyond FastAPI/Pydantic.

**Approach.** Model a workflow as a graph of named nodes; each node calls a
registered `tool` function that takes the run's mutable `state` dict and
returns an updated one. Branching reads a key out of `state` and picks the
next node from a `branches` map; looping re-runs a node until a condition on
`state` is met or `max_iterations` is hit. Every node execution — including
each loop iteration — is logged with a timestamped state snapshot.

**Result.** A ~460-line, dependency-light engine (`app/engine.py`) with three
endpoints (create a graph, run it, fetch a run's state+log), demonstrated
below with a real request against a running instance — a text-summarization
pipeline that loops a "shrink the summary" tool until it's under a target
word count.

## Architecture

```
POST /graph/create  { nodes, start_node_id, metadata }
      │
      ▼
in-memory GRAPHS store (app/store.py)
      │
POST /graph/run  { graph_id, initial_state }
      │
      ▼
execute_graph() (app/engine.py)
      │
      ├── sequential:  node.next
      ├── branching:   node.branch_on -> state[key] -> node.branches[value]
      └── looping:     node.loop.condition_key/operator/target_value,
                        re-runs the SAME node until satisfied or
                        max_iterations, then node.loop.next_on_break
      │
      ▼
tool_registry (app/tools.py)  ──  each tool: (state: dict) -> dict
      │
      ▼
StepLog per node execution (+ per loop iteration), full run history
returned by /graph/run and GET /graph/state/{run_id}
```

## Setup

```bash
pip install -r requirements.txt
uvicorn app.main:app --reload
```

Interactive API docs at `http://localhost:8000/docs`.

## Try it: a real run, not a mockup

The five built-in tools (`app/tools.py`) implement a naive text-summarization
pipeline: split into chunks, summarize each chunk, merge, then **loop** a
refine step that shrinks the summary until it's under a target word count.
This graph and request were run against a live local instance:

```bash
curl -X POST localhost:8000/graph/create -H "Content-Type: application/json" -d '{
  "nodes": [
    {"id": "split",     "tool": "split_text",       "next": "summarize"},
    {"id": "summarize", "tool": "summarize_chunks",  "next": "merge"},
    {"id": "merge",     "tool": "merge_summaries",   "next": "refine"},
    {"id": "refine",    "tool": "refine_summary",    "next": null,
     "loop": {"condition_key": "summary_length", "operator": "<=",
              "target_value": 40, "max_iterations": 5}}
  ],
  "start_node_id": "split",
  "metadata": {"name": "summarization-pipeline"}
}'
# {"graph_id": "d4793c83-6fa3-4e0a-b149-0e02a780a224"}

curl -X POST localhost:8000/graph/run -H "Content-Type: application/json" -d '{
  "graph_id": "d4793c83-6fa3-4e0a-b149-0e02a780a224",
  "initial_state": {"input_text": "<200 words>", "chunk_size": 300, "max_summary_words": 40}
}'
```

Actual response: `final_state.summary_length` converges to exactly `40`
(the target), reached via **4 loop iterations** of the `refine` node before
the condition was satisfied — visible as 7 total log entries (split,
summarize, merge, refine×4), each with its own state snapshot and timestamp:

```
0  split      split_text        loop_iteration=None
1  summarize  summarize_chunks  loop_iteration=None
2  merge      merge_summaries   loop_iteration=None
3  refine     refine_summary    loop_iteration=0
4  refine     refine_summary    loop_iteration=1
5  refine     refine_summary    loop_iteration=2
6  refine     refine_summary    loop_iteration=3
```

## API

| Endpoint | Purpose |
|---|---|
| `POST /graph/create` | Register a graph (nodes + start node + optional metadata). Returns `graph_id`. |
| `POST /graph/run` | Execute a graph synchronously from `start_node_id` with an `initial_state`. Returns `run_id`, `final_state`, and the full step log. |
| `GET /graph/state/{run_id}` | Re-fetch a completed run's final state and log. |

## Adding your own tools

A tool is any `(state: dict) -> dict` function, registered by name:

```python
from app.tools import tool_registry

def my_tool(state: dict) -> dict:
    state["result"] = do_something(state["input"])
    return state

tool_registry.register("my_tool", my_tool)
```

Reference it from a `NodeConfig.tool` field and it's usable in any graph.

## Known limitations

- **In-memory state only** (`app/store.py` is a pair of plain dicts) — graphs
  and run history are lost on restart. Fine for a demo/prototype engine, not
  for anything that needs persistence across deploys.
- **Synchronous execution** — `/graph/run` blocks until the whole graph
  finishes; there's no async/background execution or streaming of
  in-progress state.
- **No auth** — every endpoint is open. Not meant to be exposed publicly
  as-is.
- **Loop safety net is `max_iterations` only** — no cycle detection across
  branches, so a badly configured `branches` map could still infinite-loop
  outside of the dedicated `loop` mechanism.

## License

MIT — see [LICENSE](LICENSE).
