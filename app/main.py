
from fastapi import FastAPI, HTTPException
from uuid import uuid4

from .models import (
    GraphCreateRequest,
    GraphCreateResponse,
    GraphRunRequest,
    GraphRunResponse,
    RunStateResponse,
    Graph,
    Run,
)
from .store import GRAPHS, RUNS
from .engine import execute_graph
from .tools import register_default_tools


app = FastAPI(
    title="Minimal Agent Workflow Engine",
    version="0.1.0",
)


@app.on_event("startup")
def startup_event() -> None:
    # Register built-in tools (summarization workflow + utility tools)
    register_default_tools()


@app.post("/graph/create", response_model=GraphCreateResponse)
async def create_graph(payload: GraphCreateRequest) -> GraphCreateResponse:
    # Build node dict
    nodes_dict = {node.id: node for node in payload.nodes}
    if payload.start_node_id not in nodes_dict:
        raise HTTPException(
            status_code=400,
            detail=f"start_node_id '{payload.start_node_id}' not found in nodes",
        )

    graph_id = str(uuid4())
    graph = Graph(
        id=graph_id,
        nodes=nodes_dict,
        start_node_id=payload.start_node_id,
        metadata=payload.metadata or {},
    )
    GRAPHS[graph_id] = graph
    return GraphCreateResponse(graph_id=graph_id)


@app.post("/graph/run", response_model=GraphRunResponse)
async def run_graph(payload: GraphRunRequest) -> GraphRunResponse:
    graph = GRAPHS.get(payload.graph_id)
    if graph is None:
        raise HTTPException(status_code=404, detail="Graph not found")

    # Create run
    run_id = str(uuid4())
    run = Run(id=run_id, graph_id=graph.id, state=payload.initial_state, finished=False)
    RUNS[run_id] = run

    # Synchronously execute for now
    final_state, logs = execute_graph(graph, payload.initial_state)
    run.state = final_state
    run.log = logs
    run.finished = True
    RUNS[run_id] = run

    return GraphRunResponse(run_id=run_id, final_state=final_state, log=logs)


@app.get("/graph/state/{run_id}", response_model=RunStateResponse)
async def get_run_state(run_id: str) -> RunStateResponse:
    run = RUNS.get(run_id)
    if run is None:
        raise HTTPException(status_code=404, detail="Run not found")

    return RunStateResponse(
        run_id=run.id,
        state=run.state,
        finished=run.finished,
        log=run.log,
    )
