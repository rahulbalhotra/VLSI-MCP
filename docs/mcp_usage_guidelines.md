# Guidelines for Claude: Using the VLSI Formal Verification MCP Server

This workspace is connected to a custom Model Context Protocol (MCP) server containing **34 digital design and formal verification tools**. As Claude, you should proactively use these tools to inspect the design, write assertions, debug logs, check specifications, query git, and execute solver stubs.

Use the mapping below to determine when to trigger specific MCP tools.

---

## 🗺️ Tool Category Trigger Map

### 1. RTL Exploration & Block Interface
* **Trigger when**: The user asks about ports, signals, submodules, FSMs, or clock/reset networks.
* **Key Tools**:
  - `list_modules`: Find all designs in the repo.
  - `find_module`: Look up interface definitions (ports, params).
  - `find_signal`: Trace signal declarations, bit widths, and drivers.
  - `show_fsm`: Extract state names and transition conditions.
  - `show_hierarchy`: Map submodule instantiations.
  - `find_clock_domains` & `find_reset_tree`: Identify clocking trees and reset polarities.

### 2. Assertion Authoring & Quality Checks
* **Trigger when**: The user wants to write assertions (SVA), verify rules, or check property logic.
* **Key Tools**:
  - `generate_assertion`: Convert natural language to SVA properties.
  - `lint_assertion`: Inspect SVA logic for syntax errors, mismatched brackets, or vacuity risks.
  - `explain_assertion`: Get a plain English description of a temporal assertion.
  - `optimize_assertion`: Simplify complex assertions to speed up formal solvers.

### 3. Formal Solver Executions & Bottlenecks
* **Trigger when**: The user wants to run proofs, check constraints, simplify logic, or debug timeouts.
* **Key Tools**:
  - `run_formal`: Invoke JasperGold, VC Formal, or Questa.
  - `generate_constraints`: Infer clock and reset setups for formal runs.
  - `blackbox_module`: Substitute complex sub-blocks with stubs and assumptions to resolve timeouts.
  - `analyze_counterexample`: Parse solver failure logs to find the root cause.
  - `compare_runs`: Analyze runtime and proof changes between two test runs.

### 4. Waveform & Log Debugging
* **Trigger when**: The user provides a waveform file (VCD/FSDB), wants to track a signal value, or trace a bug.
* **Key Tools**:
  - `parse_vcd` / `parse_fsdb`: Load and register a waveform.
  - `signal_history`: Trace the value of a signal across cycle intervals (e.g. `clk`, `state`).
  - `explain_waveform`: Reconstruct transaction flow and handshakes from raw transitions.
  - `compare_waveforms`: Run cycle-by-cycle comparisons between two waveform logs.

### 5. Protocol Specification RAG
* **Trigger when**: The user asks about bus protocol rules (AXI, APB, PCIe, USB, DDR, RISC-V).
* **Key Tools**:
  - `search_spec`: Query specification chapters semantically.
  - `explain_protocol`: Lookup specific protocol behaviors.
  - `requirement_to_property`: Search specs and map standard interface requirements to SVAs.

### 6. Coverage & Test Plans
* **Trigger when**: The user wants to improve proof coverage or find unreachable code.
* **Key Tools**:
  - `analyze_coverage` / `uncovered_properties`: List unproven/vacuous properties.
  - `recommend_tests`: Generate suggestions to improve formal search coverage.

### 7. Bug Database & Regressions
* **Trigger when**: The user asks about historical bugs, similar failure patterns, or overnight results.
* **Key Tools**:
  - `search_bug` / `similar_failures`: Query the semantic bug database.
  - `regression_summary`: Compare overnight runs.

### 8. Git Version Tracking
* **Trigger when**: The user asks who wrote a line, which commit modified a signal, or what changed recently.
* **Key Tools**:
  - `search_commits`: Find commits affecting a design file.
  - `blame_signal`: Trace changes to lines declaring a signal.
  - `recent_changes`: List latest log activity.

### 9. Utility Documentation
* **Trigger when**: The user asks for design summaries, reports, or block diagrams.
* **Key Tools**:
  - `summarize_design` / `explain_module`: Generate block-level explanations.
  - `generate_documentation`: Write complete structured Markdown documentation.
  - `dependency_graph`: Generate connection relationships.
