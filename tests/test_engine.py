"""Self-checks for the graph execution engine (sequential, branching, looping)."""
from app.engine import execute_graph
from app.models import Graph, LoopConfig, NodeConfig
from app.tools import tool_registry


def _reset_registry():
    tool_registry.tools.clear()


def test_sequential_execution_runs_all_nodes_in_order():
    _reset_registry()
    tool_registry.register("inc", lambda state: {**state, "n": state.get("n", 0) + 1})

    graph = Graph(
        id="g1",
        start_node_id="a",
        nodes={
            "a": NodeConfig(id="a", tool="inc", next="b"),
            "b": NodeConfig(id="b", tool="inc", next=None),
        },
    )
    final_state, logs = execute_graph(graph, {"n": 0})
    assert final_state["n"] == 2
    assert [log.node_id for log in logs] == ["a", "b"]


def test_branch_on_state_value_selects_matching_edge():
    _reset_registry()
    tool_registry.register("noop", lambda state: state)
    tool_registry.register("route", lambda state: {**state, "path": "left"})

    graph = Graph(
        id="g2",
        start_node_id="router",
        nodes={
            "router": NodeConfig(id="router", tool="route", branch_on="path", branches={"left": "left_node"}),
            "left_node": NodeConfig(id="left_node", tool="noop", next=None),
            "right_node": NodeConfig(id="right_node", tool="noop", next=None),
        },
    )
    _, logs = execute_graph(graph, {})
    assert [log.node_id for log in logs] == ["router", "left_node"]


def test_loop_stops_when_condition_met():
    _reset_registry()
    tool_registry.register("inc", lambda state: {**state, "count": state.get("count", 0) + 1})

    graph = Graph(
        id="g3",
        start_node_id="loop_node",
        nodes={
            "loop_node": NodeConfig(
                id="loop_node",
                tool="inc",
                next=None,
                loop=LoopConfig(condition_key="count", operator=">=", target_value=3, max_iterations=10),
            ),
        },
    )
    final_state, logs = execute_graph(graph, {"count": 0})
    assert final_state["count"] == 3
    assert len(logs) == 3


def test_loop_stops_at_max_iterations_even_if_condition_never_met():
    _reset_registry()
    tool_registry.register("noop", lambda state: state)

    graph = Graph(
        id="g4",
        start_node_id="loop_node",
        nodes={
            "loop_node": NodeConfig(
                id="loop_node",
                tool="noop",
                next=None,
                loop=LoopConfig(condition_key="never", operator="==", target_value="unreachable", max_iterations=3),
            ),
        },
    )
    _, logs = execute_graph(graph, {})
    assert len(logs) == 3
    assert "max_iterations" in logs[-1].message


def test_unregistered_tool_raises_key_error():
    _reset_registry()
    graph = Graph(id="g5", start_node_id="a", nodes={"a": NodeConfig(id="a", tool="missing", next=None)})
    try:
        execute_graph(graph, {})
        raise AssertionError("expected KeyError for unregistered tool")
    except KeyError:
        pass


if __name__ == "__main__":
    test_sequential_execution_runs_all_nodes_in_order()
    test_branch_on_state_value_selects_matching_edge()
    test_loop_stops_when_condition_met()
    test_loop_stops_at_max_iterations_even_if_condition_never_met()
    test_unregistered_tool_raises_key_error()
    print("all engine self-checks passed")
