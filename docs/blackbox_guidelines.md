# Guidelines for Claude: Using the `blackbox_module` Tool

This document outlines the formal verification strategy for blackboxing submodules. Follow these guidelines to determine when and how to invoke the `blackbox_module` tool during a verification session.

---

## 🔍 What is Blackboxing?
Blackboxing is replacing a complex submodule (e.g. RAMs, floating-point units, third-party IP) with an empty shell (stub). The formal tool treats all outputs of a blackbox as completely unconstrained random inputs. 
To prevent false-positive failures (spurious counterexamples), you must add **interface assumptions** (`assume property`) to constrain the blackbox outputs.

---

## ⚡ When to Invoke `blackbox_module`

You should invoke the `blackbox_module` tool in the following scenarios:

### 1. Solver Timeouts / State Space Explosion
If the formal solver (JasperGold, VC Formal, Questa) fails to complete a proof within a reasonable time (timeout), look for complex arithmetic or storage submodules to blackbox:
- **Math Blocks**: Multipliers, dividers, floating-point units, DSPs.
- **Large Memories**: RAMs, register files, large ROMs.
- **Symmetric Blocks**: If the design has multiple identical channels, blackbox all but the one under verification.

### 2. Missing or Encrypted IP Blocks
If a submodule is encrypted (e.g., PCIe PHY, DDR Controller) or has not yet been implemented, blackbox the block to enable formal verification on the surrounding glue logic.

### 3. Out-of-Scope Modules
If the properties being verified only concern the control plane, blackbox data-plane modules (like payload FIFO buffers or packet parsers) that do not influence the control logic.

---

## 🛠️ How to Use `blackbox_module`

When the user asks you to **"simplify verification"**, **"reduce state space"**, or **"resolve a solver bottleneck"**:

1. **Identify the Instances**: Run `find_module` or `show_hierarchy` to locate submodules and their instance names.
2. **Execute the Tool**: Run `blackbox_module` with the parent module name and the list of instances to blackbox.
3. **Apply the Output**:
   - Save the returned TCL commands (e.g., `blackbox -set <inst_name>`) in the formal configuration/TCL script.
   - Include the generated SystemVerilog interface assumptions (`assume property`) in your formal constraint file to bound the outputs of the blackbox.
