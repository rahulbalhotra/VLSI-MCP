import os
import sys
from typing import List, Dict, Any, Optional

# Add project root to python path to avoid import issues
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if project_root not in sys.path:
    sys.path.insert(0, project_root)

from mcp.server.fastmcp import FastMCP

# Initialize FastMCP Server
mcp = FastMCP("VLSI Formal Verification Server")

# Import tool handlers
import tools.rtl.tools as rtl_tools
import tools.assertions.tools as assert_tools
import tools.formal.tools as formal_tools
import tools.waveform.tools as wave_tools
import tools.specs.tools as spec_tools
import tools.coverage.tools as cov_tools
import tools.bugs.tools as bug_tools
import tools.git.tools as git_tools
import tools.utilities.tools as util_tools


# ==========================================
# 1. RTL Tools
# ==========================================

@mcp.tool()
def find_module(module_name: str) -> Dict[str, Any]:
    """
    Find module definition and return its hierarchy, ports, parameters, and instances.
    """
    return rtl_tools.find_module(module_name)

@mcp.tool()
def find_signal(signal_name: str, module_name: str) -> Dict[str, Any]:
    """
    Search for a signal in a module and return its declaration, width, driver, fanout, and module details.
    """
    return rtl_tools.find_signal(signal_name, module_name)

@mcp.tool()
def show_hierarchy(top_module: str) -> Dict[str, Any]:
    """
    Returns complete module hierarchy tree starting from the top module.
    """
    return rtl_tools.show_hierarchy(top_module)

@mcp.tool()
def show_fsm(module_name: str) -> Dict[str, Any]:
    """
    Extract finite state machine (states, transitions, reset state, outputs) for the specified module.
    """
    return rtl_tools.show_fsm(module_name)

@mcp.tool()
def list_modules() -> List[Dict[str, str]]:
    """
    Return a list of all Verilog/SystemVerilog modules found in the workspace.
    """
    return rtl_tools.list_modules()

@mcp.tool()
def find_clock_domains(module_name: str) -> Dict[str, Any]:
    """
    Identify clock signals, generated clocks, and asynchronous domains within the module.
    """
    return rtl_tools.find_clock_domains(module_name)

@mcp.tool()
def find_reset_tree(module_name: str) -> Dict[str, Any]:
    """
    Identify reset signals and return the reset topology/polarity details.
    """
    return rtl_tools.find_reset_tree(module_name)


# ==========================================
# 2. Assertion Tools
# ==========================================

@mcp.tool()
def generate_assertion(requirement: str) -> str:
    """
    Converts a natural language requirement into a SystemVerilog Assertion (SVA).
    """
    return assert_tools.generate_assertion(requirement)

@mcp.tool()
def explain_assertion(property_expr: str) -> str:
    """
    Provides a plain English explanation of a SystemVerilog Assertion (SVA).
    """
    return assert_tools.explain_assertion(property_expr)

@mcp.tool()
def lint_assertion(name: str, property_expr: str) -> Dict[str, Any]:
    """
    Analyzes an SVA expression for syntax errors, vacuity risks, or overlapping implications.
    """
    return assert_tools.lint_assertion(name, property_expr)

@mcp.tool()
def optimize_assertion(property_expr: str) -> str:
    """
    Suggests optimizations to simplify an SVA property and reduce formal solver complexity.
    """
    return assert_tools.optimize_assertion(property_expr)


# ==========================================
# 3. Formal Tools
# ==========================================

@mcp.tool()
def run_formal(
    engine: str,
    rtl_files: List[str],
    assertion_files: List[str],
    constraints_files: List[str],
    top_module: Optional[str] = None,
    work_dir: Optional[str] = None
) -> Dict[str, Any]:
    """
    Executes a formal verification run using the specified engine (e.g. 'JasperGold', 'VCFormal', 'Questa').
    """
    return formal_tools.run_formal(engine, rtl_files, assertion_files, constraints_files, top_module, work_dir)

@mcp.tool()
def generate_constraints(module_name: str) -> str:
    """
    Automatically infers clocks, resets, and assumptions to generate a formal constraints template.
    """
    return formal_tools.generate_constraints(module_name)

@mcp.tool()
def analyze_counterexample(counterexample_trace: str) -> str:
    """
    Analyzes a formal counterexample trace log and provides a plain English root cause summary.
    """
    return formal_tools.analyze_counterexample(counterexample_trace)

@mcp.tool()
def compare_runs(run_a: Dict[str, Any], run_b: Dict[str, Any]) -> Dict[str, Any]:
    """
    Compares two formal verification execution reports.
    """
    return formal_tools.compare_runs(run_a, run_b)


# ==========================================
# 4. Waveform Tools
# ==========================================

@mcp.tool()
def parse_vcd(file_path: str) -> Dict[str, Any]:
    """
    Loads and parses a VCD waveform file, returning metadata and signal lists.
    """
    return wave_tools.parse_vcd(file_path)

@mcp.tool()
def parse_fsdb(file_path: str) -> Dict[str, Any]:
    """
    Loads and parses an FSDB waveform file, returning metadata and signal lists.
    """
    return wave_tools.parse_fsdb(file_path)

@mcp.tool()
def explain_waveform(file_path: str, signals: List[str]) -> str:
    """
    Analyzes a segment of waveform data and generates a natural-language explanation of transitions.
    """
    return wave_tools.explain_waveform(file_path, signals)

@mcp.tool()
def signal_history(file_path: str, signal_name: str, start_time: int = 0, end_time: Optional[int] = None) -> List[Dict[str, Any]]:
    """
    Returns the historical values of a signal across simulation cycles/ticks.
    """
    return wave_tools.signal_history(file_path, signal_name, start_time, end_time)

@mcp.tool()
def compare_waveforms(file_a: str, file_b: str, signals: List[str]) -> Dict[str, Any]:
    """
    Compares signal values between two waveform files and reports mismatches.
    """
    return wave_tools.compare_waveforms(file_a, file_b, signals)


# ==========================================
# 5. Specification Tools
# ==========================================

@mcp.tool()
def search_spec(query: str, protocol: Optional[str] = None) -> List[Dict[str, Any]]:
    """
    Searches indexed protocol specifications (AXI, APB, PCIe, USB, DDR, RISC-V) using semantic search.
    """
    return spec_tools.search_spec(query, protocol)

@mcp.tool()
def explain_protocol(protocol: str, concept: str) -> str:
    """
    Explains a protocol concept using indexed specification context.
    """
    return spec_tools.explain_protocol(protocol, concept)

@mcp.tool()
def requirement_to_property(requirement: str) -> str:
    """
    Translates a verification requirement into SystemVerilog Assertions using specification context.
    """
    return spec_tools.requirement_to_property(requirement)


# ==========================================
# 6. Coverage Tools
# ==========================================

@mcp.tool()
def analyze_coverage(module_name: str) -> Dict[str, Any]:
    """
    Analyzes functional, assertion, and proof coverage for a module under formal verification.
    """
    return cov_tools.analyze_coverage(module_name)

@mcp.tool()
def uncovered_properties(module_name: str) -> List[Dict[str, Any]]:
    """
    Lists assertions that have not been fully proven or activated during verification.
    """
    return cov_tools.uncovered_properties(module_name)

@mcp.tool()
def recommend_tests(module_name: str) -> str:
    """
    Suggests stimulus, helper constraints, or test plan updates to improve coverage.
    """
    return cov_tools.recommend_tests(module_name)


# ==========================================
# 7. Bug Database Tools
# ==========================================

@mcp.tool()
def search_bug(query: str) -> List[Dict[str, Any]]:
    """
    Performs a semantic bug search over historical failure databases.
    """
    return bug_tools.search_bug(query)

@mcp.tool()
def similar_failures(failure_description: str) -> List[Dict[str, Any]]:
    """
    Finds matching historical failures based on failure symptoms or log descriptions.
    """
    return bug_tools.similar_failures(failure_description)

@mcp.tool()
def regression_summary(run_id_a: str, run_id_b: str) -> Dict[str, Any]:
    """
    Compares two overnight regression runs and summarizes status changes and runtime trends.
    """
    return bug_tools.regression_summary(run_id_a, run_id_b)


# ==========================================
# 8. Git Tools
# ==========================================

@mcp.tool()
def search_commits(file_path: str, max_count: int = 5) -> List[Dict[str, Any]]:
    """
    Finds commits affecting the specified design or verification file.
    """
    return git_tools.search_commits(file_path, max_count)

@mcp.tool()
def blame_signal(file_path: str, signal_name: str) -> List[Dict[str, Any]]:
    """
    Identifies the commit history and changes for lines containing the specified signal.
    """
    return git_tools.blame_signal(file_path, signal_name)

@mcp.tool()
def recent_changes(max_count: int = 5) -> List[Dict[str, Any]]:
    """
    Returns latest modifications/commits in the git repository.
    """
    return git_tools.recent_changes(max_count)


# ==========================================
# 9. Utility Tools
# ==========================================

@mcp.tool()
def summarize_design(top_module: str) -> str:
    """
    Generates a high-level architectural summary of the design under the specified top module.
    """
    return util_tools.summarize_design(top_module)

@mcp.tool()
def explain_module(module_name: str) -> str:
    """
    Generates a detailed explanation of a module's ports, parameters, signals, and sub-instances.
    """
    return util_tools.explain_module(module_name)

@mcp.tool()
def generate_documentation(module_name: str) -> str:
    """
    Generates structured Markdown documentation for a Verilog/SystemVerilog module.
    """
    return util_tools.generate_documentation(module_name)

@mcp.tool()
def dependency_graph(top_module: str) -> Dict[str, Any]:
    """
    Generates a dependency node-edge graph mapping sub-module instantiation dependencies.
    """
    return util_tools.dependency_graph(top_module)


# Main Entry Point
if __name__ == "__main__":
    mcp.run()
