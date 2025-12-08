
from copy import deepcopy
from datetime import datetime
from typing import Any, Dict, List, Tuple, Optional

from .models import Graph, NodeConfig, StepLog, LoopConfig
from .tools import tool_registry


def _compare(a: Any, op: str, b: Any) -> bool:
    if op == "<":
        return a < b
    if op == "<=":
        return a <= b
    if op == ">":
        return a > b
    if op == ">=":
        return a >= b
    if op == "==":
        return a == b
    if op == "!=":
        return a != b
    raise ValueError(f"Unsupported operator {op}")


def _evaluate_loop_condition(state: Dict[str, Any], loop: LoopConfig) -> bool:
    """Return True if loop condition is satisfied (i.e., we should stop looping)."""
    value = state.get(loop.condition_key)
    return _compare(value, loop.operator, loop.target_value)


def _run_single_node(
    node: NodeConfig,
    state: Dict[str, Any],
    step_index: int,
    loop_iteration: Optional[int] = None,
) -> Tuple[Dict[str, Any], StepLog]:
    """Execute a single node: call its tool and produce a log entry."""
    tool = tool_registry.get(node.tool)
    updated_state = tool(state)

    log = StepLog(
        step_index=step_index,
        node_id=node.id,
        tool=node.tool,
        loop_iteration=loop_iteration,
        state_snapshot=deepcopy(updated_state),
        message=None,
        timestamp=datetime.utcnow().isoformat() + "Z",
    )
    return updated_state, log


def execute_graph(graph: Graph, initial_state: Dict[str, Any]) -> Tuple[Dict[str, Any], List[StepLog]]:
    """
    Run the graph from start_node_id until there is no next node.

    Supports:
      * sequential execution via node.next
      * branching via node.branch_on + node.branches
      * looping via node.loop: run node until condition is met or max_iterations
    """
    state = deepcopy(initial_state)
    logs: List[StepLog] = []

    current_node_id: Optional[str] = graph.start_node_id
    step_index = 0

    while current_node_id is not None:
        node: NodeConfig = graph.nodes[current_node_id]

        # If node has loop configuration
        if node.loop is not None:
            loop_cfg = node.loop
            iteration = 0
            while True:
                state, log = _run_single_node(
                    node=node,
                    state=state,
                    step_index=step_index,
                    loop_iteration=iteration,
                )
                logs.append(log)
                step_index += 1
                iteration += 1

                # stop looping if condition satisfied or we hit max_iterations
                if _evaluate_loop_condition(state, loop_cfg):
                    # proceed to next_on_break if present, else normal next
                    next_node = loop_cfg.next_on_break or node.next
                    current_node_id = next_node
                    break

                if iteration >= loop_cfg.max_iterations:
                    # safety stop; still go to next node
                    log.message = (
                        f"Loop max_iterations ({loop_cfg.max_iterations}) reached; "
                        f"moving to next node."
                    )
                    next_node = loop_cfg.next_on_break or node.next
                    current_node_id = next_node
                    break

            # loop handled; continue to next node in outer while
            continue

        # No loop: run node once
        state, log = _run_single_node(
            node=node,
            state=state,
            step_index=step_index,
            loop_iteration=None,
        )
        logs.append(log)
        step_index += 1

        # Decide next node: branching if configured
        next_node_id: Optional[str] = None
        if node.branch_on and node.branches:
            key = node.branch_on
            value = state.get(key)
            if value in node.branches:
                next_node_id = node.branches[value]
            else:
                # Fallback to default next
                next_node_id = node.next
        else:
            next_node_id = node.next

        current_node_id = next_node_id

    return state, logs
