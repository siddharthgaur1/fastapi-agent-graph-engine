
from __future__ import annotations

from typing import Any, Literal

from pydantic import BaseModel, Field


class LoopConfig(BaseModel):
    """Configuration for looping a node until a condition is met."""

    condition_key: str
    operator: Literal["<", "<=", ">", ">=", "==", "!="]
    target_value: int | float | str | bool
    max_iterations: int = 10
    next_on_break: str | None = None  # optional next node when loop ends


class NodeConfig(BaseModel):
    """Definition of a node in the graph."""

    id: str
    tool: str  # name of tool to call
    next: str | None = None  # default next node
    branch_on: str | None = None  # key in state to branch on
    branches: dict[str, str] | None = None  # value -> next node id
    loop: LoopConfig | None = None  # optional loop behaviour


class GraphCreateRequest(BaseModel):
    nodes: list[NodeConfig]
    start_node_id: str
    metadata: dict[str, Any] | None = None


class GraphCreateResponse(BaseModel):
    graph_id: str


class Graph(BaseModel):
    id: str
    nodes: dict[str, NodeConfig]
    start_node_id: str
    metadata: dict[str, Any] = Field(default_factory=dict)


class GraphRunRequest(BaseModel):
    graph_id: str
    initial_state: dict[str, Any] = Field(default_factory=dict)


class StepLog(BaseModel):
    step_index: int
    node_id: str
    tool: str
    loop_iteration: int | None = None
    state_snapshot: dict[str, Any]
    message: str | None = None
    timestamp: str


class GraphRunResponse(BaseModel):
    run_id: str
    final_state: dict[str, Any]
    log: list[StepLog]


class Run(BaseModel):
    id: str
    graph_id: str
    state: dict[str, Any]
    finished: bool = False
    log: list[StepLog] = Field(default_factory=list)


class RunStateResponse(BaseModel):
    run_id: str
    state: dict[str, Any]
    finished: bool
    log: list[StepLog]
