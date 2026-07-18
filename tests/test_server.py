import os
import pytest
from parsers.verilog_parser import VerilogParser
from parsers.vcd_parser import VCDParser
from parsers.assertion_parser import AssertionParser
from app.config import rtl_service, waveform_service, rag_service, regression_service, WORKSPACE_ROOT

# Paths
TEST_DATA_DIR = os.path.join(WORKSPACE_ROOT, "tests", "data")
FIFO_V = os.path.join(TEST_DATA_DIR, "fifo.v")
FIFO_VCD = os.path.join(TEST_DATA_DIR, "fifo_tb.vcd")

def test_verilog_parser():
    """Test parsing of sample Verilog file."""
    assert os.path.exists(FIFO_V), f"{FIFO_V} does not exist"
    modules = VerilogParser.parse_file(FIFO_V)
    assert len(modules) == 1
    mod = modules[0]
    assert mod.name == "fifo"
    assert any(p.name == "clk" for p in mod.ports)
    assert any(p.name == "rst_n" for p in mod.ports)
    assert any(p.name == "w_en" for p in mod.ports)
    assert any(p.name == "r_en" for p in mod.ports)
    assert any(param.name == "DEPTH" for param in mod.parameters)

def test_fsm_extraction():
    """Test FSM state and transition extraction."""
    fsm = VerilogParser.extract_fsm(FIFO_V, "fifo")
    assert "STATE_IDLE" in fsm["states"]
    assert "STATE_BUSY" in fsm["states"]
    assert "STATE_FULL" in fsm["states"]
    assert fsm["reset_state"] == "STATE_IDLE"
    assert len(fsm["transitions"]) > 0

def test_vcd_parser():
    """Test parsing of VCD waveform file."""
    assert os.path.exists(FIFO_VCD)
    trace = VCDParser.parse_file(FIFO_VCD)
    assert "clk" in trace.signals
    assert "rst_n" in trace.signals
    assert "w_en" in trace.signals
    assert any("state" in s for s in trace.signals)
    assert trace.timescale == "1ns"
    assert trace.max_time == 120
    # Check transitions
    assert len(trace.transitions["clk"]) > 0
    assert len(trace.transitions["rst_n"]) > 0

def test_assertion_linter():
    """Test SystemVerilog Assertion linter."""
    # Test valid property
    res1 = AssertionParser.lint_assertion("p_valid", "assert property (@(posedge clk) req |-> ##[1:5] gnt);")
    assert not res1.has_error
    assert len(res1.errors) == 0

    # Test mismatched parentheses
    res2 = AssertionParser.lint_assertion("p_broken", "assert property (@(posedge clk) (req |-> ##[1:5] gnt;")
    assert res2.has_error
    assert "Mismatched" in res2.errors[0] or "Unclosed" in res2.errors[0]

    # Test vacuity risk
    res3 = AssertionParser.lint_assertion("p_vacuous", "assert property (@(posedge clk) req |-> 1);")
    assert res3.vacuity_risk

def test_rag_service():
    """Test spec indexing and semantic search."""
    results = rag_service.search_spec("Write Handshake", "AXI")
    assert len(results) > 0
    assert results[0]["protocol"] == "AXI"
    assert "AWVALID" in results[0]["content"] or "BVALID" in results[0]["content"]

def test_regression_service():
    """Test regression runs and comparison logs."""
    summary = regression_service.get_regression_summary("run_2026_07_17", "run_2026_07_18")
    assert summary["runs_compared"] == ["run_2026_07_17", "run_2026_07_18"]
    # Resolved failure is p_axi_handshake (it was failing in 17, but not in 18)
    assert "p_axi_handshake" in summary["resolved_failures"]
    assert summary["trends"]["status_change"] == "failed -> failed"

def test_arbiter_parsing():
    """Test parsing of the new arbiter module."""
    arb_v = os.path.join(WORKSPACE_ROOT, "design", "arbiter.sv")
    assert os.path.exists(arb_v)
    modules = VerilogParser.parse_file(arb_v)
    assert len(modules) == 1
    mod = modules[0]
    assert mod.name == "arbiter"
    assert any(p.name == "req" for p in mod.ports)
    assert any(p.name == "gnt" for p in mod.ports)
    # Check that we parsed parameter MODE
    assert any(param.name == "MODE" for param in mod.parameters)

