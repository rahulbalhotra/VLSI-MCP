from pydantic import BaseModel, Field
from typing import List, Optional

class Assertion(BaseModel):
    name: str
    property_expression: str = Field(..., description="SystemVerilog assertion expression, e.g., 'assert property (@(posedge clk) req |-> ##[1:5] gnt)'")
    module: str = Field(..., description="Module this assertion is placed in")
    status: str = Field("unknown", description="unknown, proven, failed, vacuous, disabled")
    coverage: float = Field(0.0, description="Assertion functional coverage percentage")

class LintResult(BaseModel):
    assertion_name: str
    has_error: bool
    errors: List[str] = Field(default_factory=list)
    warnings: List[str] = Field(default_factory=list)
    vacuity_risk: bool = False
    overlapping_implications: bool = False

class AssertionOptimization(BaseModel):
    assertion_name: str
    original_expression: str
    optimized_expression: str
    rationale: str
    complexity_reduction: str = Field(..., description="e.g. 'Reduced clock cycles', 'Removed state dependance'")
