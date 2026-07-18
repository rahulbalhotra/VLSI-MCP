from typing import List, Dict, Any, Optional
from app.config import rag_service, llm_service

def search_spec(query: str, protocol: Optional[str] = None) -> List[Dict[str, Any]]:
    """
    Searches indexed protocol specifications (AXI, APB, PCIe, etc.) using semantic search.
    """
    return rag_service.search_spec(query, protocol)

def explain_protocol(protocol: str, concept: str) -> str:
    """
    Explains a protocol concept (e.g. 'AXI outstanding address write', 'APB setup cycle') using specification context.
    """
    # 1. Retrieve relevant spec snippets
    snippets = rag_service.search_spec(concept, protocol, top_k=2)
    snippet_text = "\n\n".join([f"[{s['section']}]: {s['content']}" for s in snippets])
    
    prompt = (
        f"Explain the following concept for the '{protocol}' protocol:\n"
        f"Concept: {concept}\n\n"
        f"Reference Specs Context:\n{snippet_text if snippet_text else 'No direct specification snippet found.'}\n\n"
        f"Provide a clear, detailed explanation of the concept's behavior, signals involved, and protocol rules."
    )
    system_instruction = "You are an expert system-on-chip architect and protocols expert. Explain behavior clearly."
    
    response = llm_service.generate_text(prompt, system_instruction)
    return response

def requirement_to_property(requirement: str) -> str:
    """
    Translates a verification requirement into SystemVerilog Assertions by matching it with protocol specifications.
    """
    # 1. Search specs database to find relevant protocol details
    snippets = rag_service.search_spec(requirement, top_k=2)
    context = "\n".join([f"Source: {s['document_name']} Section: {s['section']}\nText: {s['content']}" for s in snippets])

    prompt = (
        f"Convert the requirement into a SystemVerilog Assertion (SVA) using the provided protocol specification context:\n\n"
        f"Requirement: {requirement}\n\n"
        f"Specification Context:\n{context if context else 'No spec details found.'}\n\n"
        f"Output only the SystemVerilog Assertion code block."
    )
    system_instruction = "You are a professional VLSI formal verification engineer. Translate requirements to assertions."
    
    response = llm_service.generate_text(prompt, system_instruction)
    return response
