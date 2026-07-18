# VLSI Formal Verification MCP Server - Technical Documentation

This document describes the inner workings, data structures, parsing algorithms, and connector schemas of the VLSI Formal Verification MCP Server.

---

## 💾 Core Data Models (Pydantic)

We define strongly-typed models under [models/](file:///d:/VLSI-MCP/models/) to guarantee clean serialization of ASTs and verification records.

### 1. RTL Structures ([models/rtl.py](file:///d:/VLSI-MCP/models/rtl.py))
- **`Port`**: Represents module interfaces (name, direction: input/output/inout, bit width expression).
- **`Parameter`**: Stores parameter names, values, and default assignments.
- **`Signal`**: Represents wires, registers, and logic blocks. It tracks drivers (assignment statements, always blocks) and load nets.
- **`Instance`**: Represents submodules instantiated in a parent design, mapping submodule ports to parent nets and overrides.
- **`Module`**: Combines ports, parameters, signals, sub-instances, and structural hierarchy.

### 2. SVA Structures ([models/assertion.py](file:///d:/VLSI-MCP/models/assertion.py))
- **`Assertion`**: Represents an SVA property, containing its expression (e.g. `assert property (@(posedge clk) req |-> ##[1:5] gnt)`), module path, proof status, and functional coverage.
- **`LintResult`**: Tracks SVA syntax errors, unclosed brackets, and Boolean vacuity checks.
- **`AssertionOptimization`**: Contains the original vs. optimized property expression and complexity reduction rationale.

### 3. Waveform Structures ([models/waveform.py](file:///d:/VLSI-MCP/models/waveform.py))
- **`SignalTransition`**: Records value change timestamps (time, value string e.g. `'0'`, `'1'`, `'x'`, `'z'`).
- **`WaveformTrace`**: Maps signal names to chronological lists of `SignalTransition` points.

### 4. Regression Structures ([models/regression.py](file:///d:/VLSI-MCP/models/regression.py))
- **`RegressionRun`**: Aggregates run id, runtime, commit hash, pass/fail counts, and list of failing properties.
- **`RegressionSummary`**: Compares two runs to compute runtime difference and lists of new/resolved failures.

---

## 🔍 Parsing Details

### 1. Verilog Parser (`parsers/verilog_parser.py`)
Because full SystemVerilog syntax is extremely broad, we use a regex-based parser built for high portability across environments. It cleans comments (`//` and `/* ... */`) and extracts structural blocks:
- **Module block**: Finds module scopes using `\bmodule\b\s+(\w+)\s*(.*?)\bendmodule\b` to separate headers and bodies.
- **Ports & Parameters**: Scans declarations using keywords like `input`, `output`, `inout`, `parameter`, and `localparam`.
- **Instances**: Extracts submodule instantiations while filtering out standard Verilog keywords.
- **FSM logic**: Recognizes `case` blocks checking state registers (e.g., `case(state)`), parsing target state assignments (`next_state <= STATE_NAME`) and corresponding conditions (e.g., `if (w_en)`).

### 2. VCD Parser (`parsers/vcd_parser.py`)
Value Change Dump (VCD) files are parsed line-by-line:
1. **Header Phase**: Parses definitions within `$timescale`, `$var`, and `$enddefinitions`.
2. **Timeline Reconstruction**: Builds an index of symbols mapped to signal names.
3. **Transition Tracking**: Scans lines starting with `#` for timestamps, and Scalar/Vector lines (e.g. `1!`, `b0101 `) to log value transitions in a timeline.

### 3. SVA Linter (`parsers/assertion_parser.py`)
Performs static analysis on assertion strings:
- **Parentheses matching**: Validates braces, brackets, and parentheses using a character stack.
- **Vacuity**: Alerts if consequents evaluate to constants (e.g., `|-> 1`), or if triggers are unreachable due to a constant false antecedent (e.g., `assert property (0 |-> ...)`).
- **Overlapping implications**: Checks if multiple implications (e.g., `|->`, `|=>`) are nested on a single path.

---

## 🔌 EDA Connectors & Mocks

Connectors under [connectors/](file:///d:/VLSI-MCP/connectors/) translate python calls into subprocess invocations.

### 1. Cadence JasperGold Connector (`connectors/jasper.py`)
- If `jg` is available, it creates a temporary TCL launch script:
  ```tcl
  clear -all
  analyze -sv [rtl_files]
  analyze -sv [assertion_files]
  elaborate -top [top_module]
  clock clk
  reset rst
  prove -all
  exit
  ```
- Launches `jg -no_gui -fpv [tcl_file] -log jaspergold.log`.
- Parses the resulting log file. If the solver is missing, it falls back to **Mock Execution**, checking assertions by filename (e.g. assertions containing "fail" are marked as failed, others proven).

### 2. Synopsys VC Formal & Siemens Questa Connectors (`connectors/vcformal.py`, `connectors/questa.py`)
Wrappers executing equivalent CLI commands (`vc_formal -file...` or `qformal -c -do "run -all; exit"`). They fall back to mock outcomes during evaluation.

---

## 🗄️ Database Schemas

We maintain local semantic databases using SQLite under `database/`:

### 1. Specification chunks (`database/rag.db`)
Stores chunks of protocol guides (e.g., AXI, APB, PCIe specs) alongside float list embeddings stored as flat binary arrays (`BLOB`).
- **Schema**: `spec_chunks(id, protocol, document_name, section, content, embedding BLOB)`
- **Search**: Computes **Cosine Similarity** between the query embedding and stored chunks using NumPy:
  $$\text{Cosine Similarity} = \frac{A \cdot B}{\|A\| \|B\|}$$

### 2. Bug & Regression Runs Database (`database/regression.db`)
- **`regression_runs`**: Logs historical test suites to identify status trends and failures.
  - Schema: `(run_id, timestamp, commit_hash, total_properties, passed_properties, failed_properties, vacuous_properties, runtime_seconds, status, failures_json)`
- **`bugs`**: Stores semantic descriptions of historical hardware bugs.
  - Schema: `(bug_id, summary, module, root_cause, fix_details, embedding BLOB)`
