
from typing import Any, Callable, Dict, List
from dataclasses import dataclass


@dataclass
class ToolRegistry:
    tools: Dict[str, Callable[[Dict[str, Any]], Dict[str, Any]]]

    def __init__(self) -> None:
        self.tools = {}

    def register(self, name: str, func: Callable[[Dict[str, Any]], Dict[str, Any]]) -> None:
        self.tools[name] = func

    def get(self, name: str) -> Callable[[Dict[str, Any]], Dict[str, Any]]:
        if name not in self.tools:
            raise KeyError(f"Tool '{name}' not registered")
        return self.tools[name]


tool_registry = ToolRegistry()


# -----------------------------
#  Summarization workflow tools
#  (Option B in the assignment)
# -----------------------------


def split_text_into_chunks(state: Dict[str, Any]) -> Dict[str, Any]:
    """
    Input:
        state["input_text"]: str
        state["chunk_size"]: int (optional, default=300 characters)
    Output:
        state["chunks"]: List[str]
    """
    text: str = state.get("input_text", "")
    chunk_size: int = int(state.get("chunk_size", 300))

    chunks: List[str] = []
    current = 0
    while current < len(text):
        chunks.append(text[current : current + chunk_size])
        current += chunk_size

    state["chunks"] = chunks
    state["num_chunks"] = len(chunks)
    return state


def summarize_chunks(state: Dict[str, Any]) -> Dict[str, Any]:
    """
    Very naive summarizer: takes first N words of each chunk.
    Input:
        state["chunks"]: List[str]
        state["chunk_summary_words"]: int (optional, default=30)
    Output:
        state["chunk_summaries"]: List[str]
    """
    chunks = state.get("chunks", [])
    max_words = int(state.get("chunk_summary_words", 30))

    summaries: List[str] = []
    for chunk in chunks:
        words = chunk.split()
        short = " ".join(words[:max_words])
        summaries.append(short)

    state["chunk_summaries"] = summaries
    return state


def merge_summaries(state: Dict[str, Any]) -> Dict[str, Any]:
    """
    Input:
        state["chunk_summaries"]: List[str]
    Output:
        state["summary"]: str
    """
    summaries = state.get("chunk_summaries", [])
    merged = " ".join(summaries)
    state["summary"] = merged
    state["summary_length"] = len(merged.split())
    return state


def refine_summary(state: Dict[str, Any]) -> Dict[str, Any]:
    """
    Refines the summary by gradually shrinking it.
    - On each call, it will reduce the number of words by a factor until
      it's closer to the desired limit, then just trim to the limit.

    Input:
        state["summary"]: str
        state["max_summary_words"]: int (desired final length, default 80)
        state["refine_factor"]: float (0 < f <= 1, default 0.7)
    Output:
        state["summary"]: str (updated)
        state["summary_length"]: int
    """
    summary: str = state.get("summary", "")
    words = summary.split()
    max_words = int(state.get("max_summary_words", 80))
    refine_factor = float(state.get("refine_factor", 0.7))

    current_len = len(words)
    if current_len <= max_words:
        # Already short enough; no change
        new_words = words
    else:
        # Gradually reduce length toward the limit
        # First shrink by factor; never below max_words
        new_len = max(max_words, int(current_len * refine_factor))
        new_words = words[:new_len]

    new_summary = " ".join(new_words)
    state["summary"] = new_summary
    state["summary_length"] = len(new_words)
    return state


def lowercase_text(state: Dict[str, Any]) -> Dict[str, Any]:
    """Simple generic tool: lowercase the input_text into lowercase_text."""
    text = state.get("input_text", "")
    state["lowercase_text"] = text.lower()
    return state


def register_default_tools() -> None:
    """Call this at startup to register built-in tools."""
    tool_registry.register("split_text", split_text_into_chunks)
    tool_registry.register("summarize_chunks", summarize_chunks)
    tool_registry.register("merge_summaries", merge_summaries)
    tool_registry.register("refine_summary", refine_summary)
    tool_registry.register("lowercase_text", lowercase_text)
