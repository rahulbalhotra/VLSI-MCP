from pydantic import BaseModel, Field
from typing import List, Dict, Any

class SignalTransition(BaseModel):
    time: int = Field(..., description="Simulation time/cycle of the change")
    value: str = Field(..., description="New value, e.g. '0', '1', 'x', 'z', '1010'")

class WaveformTrace(BaseModel):
    file_path: str
    signals: List[str] = Field(default_factory=list, description="List of signal names in the trace")
    timescale: str = "1ns"
    transitions: Dict[str, List[SignalTransition]] = Field(
        default_factory=dict, 
        description="Mapping of signal name -> list of transition events"
    )
    max_time: int = 0
