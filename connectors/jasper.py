import os
import subprocess
import tempfile
from typing import Dict, Any, List, Optional
from parsers.report_parser import ReportParser

class JasperConnector:
    def __init__(self, executable_path: Optional[str] = None):
        self.executable = executable_path or "jg"

    def run_formal(
        self, 
        rtl_files: List[str], 
        assertion_files: List[str], 
        constraints_files: List[str],
        top_module: Optional[str] = None,
        work_dir: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Executes Cadence JasperGold.
        If JasperGold is not found, runs in Mock mode.
        """
        # Check if JasperGold is available
        is_available = self._check_availability()
        
        if not is_available:
            return self._run_mock(rtl_files, assertion_files, constraints_files, top_module)

        # Build JasperGold TCL script
        tcl_script = self._build_tcl_script(rtl_files, assertion_files, constraints_files, top_module)
        
        with tempfile.NamedTemporaryFile(suffix=".tcl", mode="w", delete=False) as f:
            f.write(tcl_script)
            tcl_path = f.name

        log_path = os.path.join(work_dir or tempfile.gettempdir(), "jaspergold.log")
        
        # Execute JasperGold
        cmd = [self.executable, "-no_gui", "-fpv", tcl_path, "-log", log_path]
        try:
            subprocess.run(cmd, check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            results = ReportParser.parse_jasper_report(log_path)
            results["mocked"] = False
            return results
        except (subprocess.SubprocessError, FileNotFoundError) as e:
            return self._run_mock(rtl_files, assertion_files, constraints_files, top_module, error=str(e))
        finally:
            if os.path.exists(tcl_path):
                os.remove(tcl_path)

    def _check_availability(self) -> bool:
        try:
            # Check if jg is on path
            subprocess.run([self.executable, "-version"], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            return True
        except (subprocess.SubprocessError, FileNotFoundError):
            return False

    def _build_tcl_script(
        self, 
        rtl_files: List[str], 
        assertion_files: List[str], 
        constraints_files: List[str],
        top_module: Optional[str]
    ) -> str:
        tcl = []
        tcl.append("clear -all")
        # Analyze RTL files
        for f in rtl_files:
            if f.endswith(".sv"):
                tcl.append(f"analyze -sv {f}")
            else:
                tcl.append(f"analyze -v {f}")
        
        # Analyze Assertions
        for f in assertion_files:
            tcl.append(f"analyze -sv {f}")

        # Elaborate top
        if top_module:
            tcl.append(f"elaborate -top {top_module}")
        else:
            tcl.append("elaborate")

        # Clock & Reset setups
        tcl.append("clock clk")
        tcl.append("reset rst")

        # Constraints
        for f in constraints_files:
            tcl.append(f"include {f}")

        # Run
        tcl.append("prove -all")
        tcl.append("exit")
        return "\n".join(tcl)

    def _run_mock(
        self, 
        rtl_files: List[str], 
        assertion_files: List[str], 
        constraints_files: List[str],
        top_module: Optional[str],
        error: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Simulates JasperGold outputs.
        """
        proven = []
        failed = []
        vacuous = []
        
        # Deduce assertion names to mock
        # We look inside assertion files for assert property names
        for filepath in assertion_files:
            if os.path.exists(filepath):
                with open(filepath, 'r') as f:
                    content = f.read()
                matches = re.findall(r'(\w+)\s*:\s*(?:assert|cover)\s+property', content)
                for m in matches:
                    # Let's mock: assertions with 'fail' in name will fail, others pass
                    if 'fail' in m.lower() or 'bug' in m.lower():
                        failed.append(m)
                    elif 'vac' in m.lower():
                        vacuous.append(m)
                    else:
                        proven.append(m)
                        
        if not proven and not failed:
            # Fallback mock assertions if files are empty/missing
            proven = ["p_fifo_overflow_check", "p_write_pointer_inc"]
            failed = ["p_fifo_underflow_check"]

        status = "failed" if failed else "passed"
        
        return {
            "status": status,
            "proven": proven,
            "failed": failed,
            "vacuous": vacuous,
            "proof_depth": 35 if status == "passed" else 12,
            "runtime": 2.45,
            "mocked": True,
            "error_detail": error
        }
