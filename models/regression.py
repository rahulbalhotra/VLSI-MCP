from pydantic import BaseModel, Field
from typing import List, Dict, Optional

class RegressionRun(BaseModel):
    run_id: str
    timestamp: str
    commit_hash: str
    total_properties: int
    passed_properties: int
    failed_properties: int
    vacuous_properties: int
    runtime_seconds: float
    status: str = Field(..., description="passed, failed, partial")
    failures: List[str] = Field(default_factory=list, description="List of failing assertion names")

class RegressionSummary(BaseModel):
    runs_compared: List[str]
    new_failures: List[str]
    resolved_failures: List[str]
    runtime_diff_seconds: float
    trends: Dict[str, str] = Field(default_factory=dict, description="e.g. {'pass_rate': 'increased by 5%'}")
    