from typing import List, Dict, Any, Optional
from connectors.jasper import JasperConnector
from connectors.vcformal import VCFormalConnector
from connectors.questa import QuestaConnector

class FormalService:
    def __init__(self):
        self.jasper = JasperConnector()
        self.vcformal = VCFormalConnector()
        self.questa = QuestaConnector()

    def run_formal(
        self,
        engine: str,
        rtl_files: List[str],
        assertion_files: List[str],
        constraints_files: List[str],
        top_module: Optional[str] = None,
        work_dir: Optional[str] = None
    ) -> Dict[str, Any]:
        engine_lower = engine.lower()
        if "jasper" in engine_lower:
            return self.jasper.run_formal(rtl_files, assertion_files, constraints_files, top_module, work_dir)
        elif "vc" in engine_lower:
            return self.vcformal.run_formal(rtl_files, assertion_files, constraints_files, top_module, work_dir)
        elif "questa" in engine_lower:
            return self.questa.run_formal(rtl_files, assertion_files, constraints_files, top_module, work_dir)
        else:
            # Default to Jasper
            return self.jasper.run_formal(rtl_files, assertion_files, constraints_files, top_module, work_dir)

    def compare_runs(self, run_a: Dict[str, Any], run_b: Dict[str, Any]) -> Dict[str, Any]:
        """
        Compares two formal runs.
        """
        proven_a = set(run_a.get("proven", []))
        proven_b = set(run_b.get("proven", []))
        failed_a = set(run_a.get("failed", []))
        failed_b = set(run_b.get("failed", []))

        newly_proven = list(proven_b - proven_a)
        newly_failed = list(failed_b - failed_a)
        resolved_failures = list(failed_a - failed_b)

        runtime_diff = run_b.get("runtime", 0.0) - run_a.get("runtime", 0.0)

        return {
            "newly_proven": newly_proven,
            "newly_failed": newly_failed,
            "resolved_failures": resolved_failures,
            "runtime_difference_seconds": runtime_diff,
            "status_change": f"{run_a.get('status')} -> {run_b.get('status')}"
        }
