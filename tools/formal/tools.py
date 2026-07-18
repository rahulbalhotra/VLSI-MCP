from typing import List, Dict, Any, Optional
from app.config import formal_service, rtl_service, llm_service, RTL_SEARCH_DIRS

def run_formal(
    engine: str,
    rtl_files: List[str],
    assertion_files: List[str],
    constraints_files: List[str],
    top_module: Optional[str] = None,
    work_dir: Optional[str] = None
) -> Dict[str, Any]:
    """
    Executes a formal verification run using the specified engine (e.g. 'JasperGold', 'VCFormal', 'Questa')
    and parses results.
    """
    return formal_service.run_formal(
        engine=engine,
        rtl_files=rtl_files,
        assertion_files=assertion_files,
        constraints_files=constraints_files,
        top_module=top_module,
        work_dir=work_dir
    )

def generate_constraints(module_name: str) -> str:
    """
    Automatically infers clocks, resets, and basic assumptions to generate a formal constraints template for a module.
    """
    clocks = rtl_service.find_clock_domains(module_name, RTL_SEARCH_DIRS)
    resets = rtl_service.find_reset_tree(module_name, RTL_SEARCH_DIRS)
    mod = rtl_service.get_module(module_name, RTL_SEARCH_DIRS)
    
    # Formulate a prompt for LLM to write constraints
    prompt = (
        f"Generate a formal constraints file (TCL/SVA format) for the module '{module_name}'.\n"
        f"Parsed Clocks: {clocks['clocks']}\n"
        f"Parsed Resets: {resets['resets']}\n"
        f"RTL signature: {mod.model_dump_json() if mod else 'Unknown ports'}\n"
        f"Provide clock definitions, reset assertions, and standard setup assumptions."
    )
    system_instruction = "You are a senior formal verification engineer. Output only the TCL / SystemVerilog constraints code block."
    
    response = llm_service.generate_text(prompt, system_instruction)
    return response

def analyze_counterexample(counterexample_trace: str) -> str:
    """
    Analyzes a formal counterexample trace/log and provides a plain English root cause summary.
    """
    prompt = f"Analyze this formal verification counterexample trace log and summarize the failure root cause:\n\n{counterexample_trace}"
    system_instruction = "You are an expert VLSI debugger. Identify the cycle of failure, the violated signals, and the likely root cause."
    
    response = llm_service.generate_text(prompt, system_instruction)
    return response

def compare_runs(run_a: Dict[str, Any], run_b: Dict[str, Any]) -> Dict[str, Any]:
    """
    Compares two formal verification execution reports.
    """
    return formal_service.compare_runs(run_a, run_b)
