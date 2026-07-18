from typing import Dict, Any, List
from app.config import rtl_service, llm_service, RTL_SEARCH_DIRS

def summarize_design(top_module: str) -> str:
    """
    Generates a high-level architectural summary of the design under the specified top module.
    """
    hierarchy = rtl_service.show_hierarchy(top_module, RTL_SEARCH_DIRS)
    prompt = (
        f"Generate a high-level architectural design summary for the design hierarchy starting at top module '{top_module}':\n\n"
        f"Hierarchy: {hierarchy}\n"
    )
    system_instruction = "You are a senior hardware design architect. Describe the design's block diagram and architecture."
    
    response = llm_service.generate_text(prompt, system_instruction)
    return response

def explain_module(module_name: str) -> str:
    """
    Generates an explanation of a module's ports, signals, instances, and basic function.
    """
    mod = rtl_service.get_module(module_name, RTL_SEARCH_DIRS)
    if not mod:
        return f"Module '{module_name}' not found."

    prompt = (
        f"Explain the functionality and interface of Verilog module '{module_name}':\n\n"
        f"AST Structure: {mod.model_dump_json()}"
    )
    system_instruction = "You are a professional hardware engineer. Explain the module interface and ports."
    
    response = llm_service.generate_text(prompt, system_instruction)
    return response

def generate_documentation(module_name: str) -> str:
    """
    Generates structured Markdown documentation for a Verilog module.
    """
    mod = rtl_service.get_module(module_name, RTL_SEARCH_DIRS)
    if not mod:
        return f"Module '{module_name}' not found."

    prompt = (
        f"Generate complete Markdown documentation for the module '{module_name}':\n\n"
        f"Module interface details: {mod.model_dump_json()}\n\n"
        f"Include sections: Interface Description, Port Table, Parameter Table, Internal Architecture, and Verification Suggestions."
    )
    system_instruction = "You are a professional technical writer and hardware architect. Output structured, professional Markdown."
    
    response = llm_service.generate_text(prompt, system_instruction)
    return response

def dependency_graph(top_module: str) -> Dict[str, Any]:
    """
    Generates a list of edges representing dependencies between module instantiations.
    """
    edges = []
    visited = set()

    def traverse(mod_name: str):
        if mod_name in visited:
            return
        visited.add(mod_name)
        mod = rtl_service.get_module(mod_name, RTL_SEARCH_DIRS)
        if not mod:
            return
        for inst in mod.instances:
            edges.append({
                "parent": mod_name,
                "child": inst.module_name,
                "instance": inst.name
            })
            traverse(inst.module_name)

    traverse(top_module)
    return {
        "top_module": top_module,
        "nodes": list(visited),
        "edges": edges
    }
