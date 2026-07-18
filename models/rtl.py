from pydantic import BaseModel, Field
from typing import List, Dict, Optional, Any

class Port(BaseModel):
    name: str
    direction: str = Field(..., description="input, output, or inout")
    width: str = Field("1", description="Bit width, e.g., '1', '[7:0]', '[WIDTH-1:0]'")

class Parameter(BaseModel):
    name: str
    value: Optional[str] = None
    default_value: Optional[str] = None

class Signal(BaseModel):
    name: str
    width: str = "1"
    type: str = Field("wire", description="wire, reg, logic, etc.")
    drivers: List[str] = Field(default_factory=list, description="Files/Lines or statements driving this signal")
    loads: List[str] = Field(default_factory=list, description="Files/Lines or statements loading this signal")
    module: str = Field(..., description="Module this signal belongs to")

class Instance(BaseModel):
    name: str
    module_name: str = Field(..., description="Type of submodule instantiated")
    port_mapping: Dict[str, str] = Field(default_factory=dict, description="Mapping of submodule port -> parent signal")
    parameters: Dict[str, str] = Field(default_factory=dict, description="Overridden parameters for this instance")

class Module(BaseModel):
    name: str
    source_file: str
    ports: List[Port] = Field(default_factory=list)
    parameters: List[Parameter] = Field(default_factory=list)
    signals: List[Signal] = Field(default_factory=list)
    instances: List[Instance] = Field(default_factory=list)
    hierarchy: List[str] = Field(default_factory=list, description="Hierarchical path if part of a parsed design")
