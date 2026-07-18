from typing import Dict, Any
from app.config import llm_service
from parsers.assertion_parser import AssertionParser

def generate_assertion(requirement: str) -> str:
    """
    Converts a natural language requirement into a SystemVerilog Assertion (SVA).
    """
    prompt = f"Convert the following natural language requirement into a SystemVerilog Assertion (SVA):\n\nRequirement: {requirement}\n\nFormat your output inside a ```systemverilog code block."
    system_instruction = "You are a professional VLSI formal verification engineer. Output only the SystemVerilog Assertion code itself without conversational text."
    
    response = llm_service.generate_text(prompt, system_instruction)
    return response

def explain_assertion(property_expr: str) -> str:
    """
    Provides a plain English explanation of the given SystemVerilog Assertion (SVA).
    """
    prompt = f"Explain the following SystemVerilog Assertion (SVA) in plain English:\n\nSVA Expression:\n{property_expr}"
    system_instruction = "You are a professional VLSI formal verification engineer explaining complex temporal assertions clearly to junior designers."
    
    response = llm_service.generate_text(prompt, system_instruction)
    return response

def lint_assertion(name: str, property_expr: str) -> Dict[str, Any]:
    """
    Analyzes an SVA expression for syntax errors, vacuity issues, or unsupported constructs.
    """
    res = AssertionParser.lint_assertion(name, property_expr)
    return res.model_dump()

def optimize_assertion(property_expr: str) -> str:
    """
    Suggests optimizations to simplify an SVA property and reduce formal solver search space.
    """
    prompt = f"Optimize the following SystemVerilog Assertion (SVA) to reduce formal verification complexity or solver runtime:\n\nSVA Expression:\n{property_expr}"
    system_instruction = "You are an expert in formal verification solver strategies. Recommend improvements or equivalent simpler formulations."
    
    response = llm_service.generate_text(prompt, system_instruction)
    return response
