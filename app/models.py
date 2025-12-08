
from __future__ import annotations

from typing import Any, Dict, List, Optional, Literal, Union
from pydantic import BaseModel, Field


class LoopConfig(BaseModel):
    """Configuration for looping a node until a condition is met."""

    condition_key: str
    operator: Literal["<", "<=", ">", ">=", "==", "!="]
    target_value: Union[int, float, str, bool]
    max_iterations: int = 10
    next_on_break: Optional[str] = None  # optional next node when loop ends


class NodeConfig(BaseModel):
    """Definition of a node in the graph."""

    id: str
    tool: str  # name of tool to call
    next: Optional[str] = None  # default next node
    branch_on: Optional[str] = None  # key in state to branch on
    branches: Optional[Dict[str, str]] = None  # value -> next node id
    loop: Optional[LoopConfig] = None  # optional loop behaviour


class GraphCreateRequest(BaseModel):
    nodes: List[NodeConfig]
    start_node_id: str
    metadata: Optional[Dict[str, Any]] = None


class GraphCreateResponse(BaseModel):
    graph_id: str


class Graph(BaseModel):
    id: str
    nodes: Dict[str, NodeConfig]
    start_node_id: str
    metadata: Dict[str, Any] = Field(default_factory=dict)


class GraphRunRequest(BaseModel):
    graph_id: str
    initial_state: Dict[str, Any] = Field(default_factory=dict)


class StepLog(BaseModel):
    step_index: int
    node_id: str
    tool: str
    loop_iteration: Optional[int] = None
    state_snapshot: Dict[str, Any]
    message: Optional[str] = None
    timestamp: str


class GraphRunResponse(BaseModel):
    run_id: str
    final_state: Dict[str, Any]
    log: List[StepLog]


class Run(BaseModel):
    id: str
    graph_id: str
    state: Dict[str, Any]
    finished: bool = False
    log: List[StepLog] = Field(default_factory=list)


class RunStateResponse(BaseModel):
    run_id: str
    state: Dict[str, Any]
    finished: bool
    log: List[StepLog]
