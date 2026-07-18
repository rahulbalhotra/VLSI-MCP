from typing import List, Dict, Any, Optional
from app.config import waveform_service, llm_service

def parse_vcd(file_path: str) -> Dict[str, Any]:
    """
    Loads and parses a VCD waveform file, returning metadata and signal list.
    """
    trace = waveform_service.parse_waveform(file_path)
    return {
        "file_path": trace.file_path,
        "signals": trace.signals,
        "timescale": trace.timescale,
        "max_time": trace.max_time
    }

def parse_fsdb(file_path: str) -> Dict[str, Any]:
    """
    Loads and parses an FSDB waveform file, returning metadata and signal list.
    """
    trace = waveform_service.parse_waveform(file_path)
    return {
        "file_path": trace.file_path,
        "signals": trace.signals,
        "timescale": trace.timescale,
        "max_time": trace.max_time
    }

def explain_waveform(file_path: str, signals: List[str]) -> str:
    """
    Analyzes a segment of waveform data and provides a natural-language description of signal transitions.
    """
    # Extract histories for the signals to explain
    histories = {}
    for sig in signals:
        hist = waveform_service.get_signal_history(file_path, sig, 0, 100) # Analyze first 100 cycles/ticks
        histories[sig] = [f"t={h['time']}:{h['value']}" for h in hist if h['time'] % 10 == 0 or h['time'] == 0] # Downsample slightly for prompt length
        
    prompt = (
        f"Explain the activity in this waveform segment:\n\n"
        f"Waveform File: {file_path}\n"
        f"Signal Transactions:\n{histories}\n\n"
        f"Describe the protocol flow, transactions, and any interesting handshakes."
    )
    system_instruction = "You are a professional digital design engineer. Summarize waveform activity clearly."
    
    response = llm_service.generate_text(prompt, system_instruction)
    return response

def signal_history(file_path: str, signal_name: str, start_time: int = 0, end_time: Optional[int] = None) -> List[Dict[str, Any]]:
    """
    Returns the historical values of a signal across cycles/simulation ticks.
    """
    return waveform_service.get_signal_history(file_path, signal_name, start_time, end_time)

def compare_waveforms(file_a: str, file_b: str, signals: List[str]) -> Dict[str, Any]:
    """
    Compares signal values between two waveform files and reports mismatches.
    """
    return waveform_service.compare_waveforms(file_a, file_b, signals)
