import os
from typing import Dict, Any, List
from app.config import rtl_service, RTL_SEARCH_DIRS

def find_module(module_name: str) -> Dict[str, Any]:
    """
    Finds a module definition and returns its details (ports, parameters, signals, instances).
    """
    mod = rtl_service.get_module(module_name, RTL_SEARCH_DIRS)
    if not mod:
        return {"error": f"Module '{module_name}' not found."}
    return mod.model_dump()

def find_signal(signal_name: str, module_name: str) -> Dict[str, Any]:
    """
    Searches for a signal inside a module and returns its declaration, width, type, drivers, and loads.
    """
    sig = rtl_service.find_signal(signal_name, module_name, RTL_SEARCH_DIRS)
    if not sig:
        return {"error": f"Signal '{signal_name}' not found in module '{module_name}'."}
    return sig.model_dump()

def show_hierarchy(top_module: str) -> Dict[str, Any]:
    """
    Returns the complete module instantiation hierarchy starting from the top module.
    """
    return rtl_service.show_hierarchy(top_module, RTL_SEARCH_DIRS)

def show_fsm(module_name: str) -> Dict[str, Any]:
    """
    Extracts the finite state machine (states, transitions, reset state, outputs) for the specified module.
    """
    return rtl_service.get_fsm(module_name, RTL_SEARCH_DIRS)

def list_modules() -> List[Dict[str, str]]:
    """
    Lists all Verilog/SystemVerilog modules found in the workspace.
    """
    modules_list = []
    # Trigger parsing of all files in search dirs to populate cache
    for d in RTL_SEARCH_DIRS:
        if not os.path.exists(d):
            continue
        for root, _, files in os.walk(d):
            # Skip hidden dirs like .venv
            if '.venv' in root or '.git' in root:
                continue
            for f in files:
                if f.endswith((".v", ".sv")):
                    path = os.path.join(root, f)
                    parsed = rtl_service.parse_file(path)
                    for m in parsed:
                        modules_list.append({
                            "name": m.name,
                            "file": os.path.relpath(path, d)
                        })
    return modules_list

def find_clock_domains(module_name: str) -> Dict[str, Any]:
    """
    Identifies clocks, generated clocks, and asynchronous clock domains inside a module.
    """
    return rtl_service.find_clock_domains(module_name, RTL_SEARCH_DIRS)

def find_reset_tree(module_name: str) -> Dict[str, Any]:
    """
    Identifies the resets and reset topologies inside a module.
    """
    return rtl_service.find_reset_tree(module_name, RTL_SEARCH_DIRS)
