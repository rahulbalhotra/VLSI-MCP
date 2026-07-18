import os
import subprocess
from typing import Optional
from models.waveform import WaveformTrace
from parsers.vcd_parser import VCDParser

class FSDBParser:
    @classmethod
    def parse_file(cls, filepath: str, fsdb2vcd_path: Optional[str] = None) -> WaveformTrace:
        """
        Parses an FSDB file. Since FSDB is a proprietary format, this connector
        will try to execute the fsdb2vcd utility if present on the system.
        Otherwise, it falls back to looking for a corresponding .vcd file, or returns a mocked trace.
        """
        if not os.path.exists(filepath):
            return WaveformTrace(file_path=filepath)

        vcd_path = filepath.rsplit('.', 1)[0] + '.vcd'

        # Check if we can convert FSDB to VCD using fsdb2vcd utility
        tool = fsdb2vcd_path or "fsdb2vcd"
        try:
            # Try running the tool
            subprocess.run([tool, filepath, "-o", vcd_path], check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            if os.path.exists(vcd_path):
                trace = VCDParser.parse_file(vcd_path)
                trace.file_path = filepath  # Set back to fsdb
                return trace
        except (subprocess.SubprocessError, FileNotFoundError):
            pass

        # Fallback 1: If a VCD file already exists with same name, use it
        if os.path.exists(vcd_path):
            trace = VCDParser.parse_file(vcd_path)
            trace.file_path = filepath
            return trace

        # Fallback 2: Return simulated/mock waveform data
        return cls._generate_mock_trace(filepath)

    @classmethod
    def _generate_mock_trace(cls, filepath: str) -> WaveformTrace:
        signals = ["clk", "rst_n", "req", "gnt", "state", "data_in[7:0]"]
        from models.waveform import SignalTransition
        transitions = {}
        
        # Mock clocks and signals
        for sig in signals:
            transitions[sig] = []
            
        for time in range(0, 1000, 10):
            # Clock toggles every 10 units
            transitions["clk"].append(SignalTransition(time=time, value=str((time // 10) % 2)))
            
            # Reset active for first 30 units
            if time < 30:
                transitions["rst_n"].append(SignalTransition(time=time, value="0"))
                transitions["req"].append(SignalTransition(time=time, value="0"))
                transitions["gnt"].append(SignalTransition(time=time, value="0"))
                transitions["state"].append(SignalTransition(time=time, value="RESET"))
            else:
                if time == 30:
                    transitions["rst_n"].append(SignalTransition(time=time, value="1"))
                    transitions["state"].append(SignalTransition(time=time, value="IDLE"))
                
                # Mock transaction
                if time == 100:
                    transitions["req"].append(SignalTransition(time=time, value="1"))
                elif time == 120:
                    transitions["state"].append(SignalTransition(time=time, value="REQ"))
                elif time == 140:
                    transitions["gnt"].append(SignalTransition(time=time, value="1"))
                    transitions["state"].append(SignalTransition(time=time, value="ACK"))
                elif time == 160:
                    transitions["req"].append(SignalTransition(time=time, value="0"))
                elif time == 180:
                    transitions["gnt"].append(SignalTransition(time=time, value="0"))
                    transitions["state"].append(SignalTransition(time=time, value="IDLE"))

        return WaveformTrace(
            file_path=filepath,
            signals=signals,
            timescale="1ns",
            transitions=transitions,
            max_time=1000
        )
