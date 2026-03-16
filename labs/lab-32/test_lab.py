"""
Tests for Lab 32: Dead Code Eliminator
"""

import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))
sys.path.insert(0, os.path.dirname(__file__))

import dead_code


# ---------------------------------------------------------------------------
# Test graphs
# ---------------------------------------------------------------------------

SIMPLE_GRAPH = {
    "entry": "main",
    "functions": {
        "main": ["init", "game_loop"],
        "init": ["load_assets"],
        "game_loop": ["update", "render"],
        "update": [],
        "render": ["draw_sprite"],
        "draw_sprite": [],
        "load_assets": [],
        "debug_dump": ["debug_print"],
        "debug_print": [],
    }
}

ALL_REACHABLE = {
    "entry": "start",
    "functions": {
        "start": ["a"],
        "a": ["b"],
        "b": ["c"],
        "c": [],
    }
}

ALL_DEAD = {
    "entry": "main",
    "functions": {
        "main": [],
        "orphan_a": [],
        "orphan_b": ["orphan_c"],
        "orphan_c": [],
    }
}

CYCLIC_GRAPH = {
    "entry": "main",
    "functions": {
        "main": ["a"],
        "a": ["b"],
        "b": ["a"],  # cycle: a -> b -> a
        "isolated": [],
    }
}

SINGLE_NODE = {
    "entry": "main",
    "functions": {
        "main": [],
    }
}


# ---------------------------------------------------------------------------
# find_reachable
# ---------------------------------------------------------------------------

class TestFindReachable:
    def test_returns_set(self):
        entry, graph = dead_code.load_call_graph_from_dict(SIMPLE_GRAPH)
        result = dead_code.find_reachable(entry, graph)
        assert result is not None, "find_reachable() returned None"
        assert isinstance(result, set)

    def test_includes_entry(self):
        entry, graph = dead_code.load_call_graph_from_dict(SIMPLE_GRAPH)
        result = dead_code.find_reachable(entry, graph)
        assert "main" in result

    def test_includes_direct_callees(self):
        entry, graph = dead_code.load_call_graph_from_dict(SIMPLE_GRAPH)
        result = dead_code.find_reachable(entry, graph)
        assert "init" in result
        assert "game_loop" in result

    def test_includes_transitive_callees(self):
        entry, graph = dead_code.load_call_graph_from_dict(SIMPLE_GRAPH)
        result = dead_code.find_reachable(entry, graph)
        assert "load_assets" in result
        assert "draw_sprite" in result

    def test_excludes_unreachable(self):
        entry, graph = dead_code.load_call_graph_from_dict(SIMPLE_GRAPH)
        result = dead_code.find_reachable(entry, graph)
        assert "debug_dump" not in result
        assert "debug_print" not in result

    def test_all_reachable(self):
        entry, graph = dead_code.load_call_graph_from_dict(ALL_REACHABLE)
        result = dead_code.find_reachable(entry, graph)
        assert len(result) == 4

    def test_handles_cycles(self):
        entry, graph = dead_code.load_call_graph_from_dict(CYCLIC_GRAPH)
        result = dead_code.find_reachable(entry, graph)
        assert "main" in result
        assert "a" in result
        assert "b" in result
        assert "isolated" not in result

    def test_single_node(self):
        entry, graph = dead_code.load_call_graph_from_dict(SINGLE_NODE)
        result = dead_code.find_reachable(entry, graph)
        assert result == {"main"}


# ---------------------------------------------------------------------------
# find_dead_code
# ---------------------------------------------------------------------------

class TestFindDeadCode:
    def test_returns_set(self):
        entry, graph = dead_code.load_call_graph_from_dict(SIMPLE_GRAPH)
        result = dead_code.find_dead_code(entry, graph)
        assert result is not None, "find_dead_code() returned None"
        assert isinstance(result, set)

    def test_finds_dead_functions(self):
        entry, graph = dead_code.load_call_graph_from_dict(SIMPLE_GRAPH)
        result = dead_code.find_dead_code(entry, graph)
        assert result == {"debug_dump", "debug_print"}

    def test_no_dead_code(self):
        entry, graph = dead_code.load_call_graph_from_dict(ALL_REACHABLE)
        result = dead_code.find_dead_code(entry, graph)
        assert len(result) == 0

    def test_multiple_dead(self):
        entry, graph = dead_code.load_call_graph_from_dict(ALL_DEAD)
        result = dead_code.find_dead_code(entry, graph)
        assert result == {"orphan_a", "orphan_b", "orphan_c"}

    def test_cycle_with_isolated(self):
        entry, graph = dead_code.load_call_graph_from_dict(CYCLIC_GRAPH)
        result = dead_code.find_dead_code(entry, graph)
        assert result == {"isolated"}
