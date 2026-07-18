import os
from typing import Dict, Any, List, Optional
from parsers.vcd_parser import VCDParser
from parsers.fsdb_parser import FSDBParser
from models.waveform import WaveformTrace, SignalTransition

class WaveformService:
    def __init__(self):
        self._parsed_cache: Dict[str, WaveformTrace] = {}

    def parse_waveform(self, filepath: str, force: bool = False) -> WaveformTrace:
        if not force and filepath in self._parsed_cache:
            return self._parsed_cache[filepath]

        if filepath.endswith(".fsdb"):
            trace = FSDBParser.parse_file(filepath)
        else:
            trace = VCDParser.parse_file(filepath)

        if trace:
            self._parsed_cache[filepath] = trace
        return trace

    def get_signal_history(self, filepath: str, signal_name: str, start_time: int = 0, end_time: Optional[int] = None) -> List[Dict[str, Any]]:
        trace = self.parse_waveform(filepath)
        if signal_name not in trace.transitions:
            # Let's check for hierarchical name matches or array slice matches
            matched_name = None
            for sig in trace.signals:
                if sig.endswith(signal_name) or signal_name in sig:
                    matched_name = sig
                    break
            if not matched_name:
                return []
            signal_name = matched_name

        transitions = trace.transitions[signal_name]
        history = []
        
        # We need to evaluate the value at each timestamp in range
        last_val = "x"
        end = end_time if end_time is not None else trace.max_time
        
        # Sort transitions by time just in case
        sorted_trans = sorted(transitions, key=lambda x: x.time)
        
        # Pre-populate initial state
        idx = 0
        current_val = "x"
        
        for t in range(start_time, end + 1):
            # Advance transition index to the current timestamp
            while idx < len(sorted_trans) and sorted_trans[idx].time <= t:
                current_val = sorted_trans[idx].value
                idx += 1
            
            history.append({
                "time": t,
                "value": current_val
            })
            
        return history

    def compare_waveforms(self, file_a: str, file_b: str, signals: List[str]) -> Dict[str, Any]:
        """
        Compares signals in two waveform traces and returns differences.
        """
        trace_a = self.parse_waveform(file_a)
        trace_b = self.parse_waveform(file_b)

        differences = {}
        
        max_time = min(trace_a.max_time, trace_b.max_time)
        if max_time == 0:
            max_time = 100 # Default fallback comparison window

        for sig in signals:
            hist_a = {h["time"]: h["value"] for h in self.get_signal_history(file_a, sig, 0, max_time)}
            hist_b = {h["time"]: h["value"] for h in self.get_signal_history(file_b, sig, 0, max_time)}
            
            sig_diffs = []
            for t in range(max_time + 1):
                val_a = hist_a.get(t, "x")
                val_b = hist_b.get(t, "x")
                if val_a != val_b:
                    sig_diffs.append({
                        "time": t,
                        "value_a": val_a,
                        "value_b": val_b
                    })
            if sig_diffs:
                differences[sig] = sig_diffs

        return {
            "compared_signals": signals,
            "max_compare_time": max_time,
            "has_mismatches": len(differences) > 0,
            "differences": differences
        }
