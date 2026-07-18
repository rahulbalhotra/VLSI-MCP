import re
import os
from typing import Dict, List, Tuple
from models.waveform import WaveformTrace, SignalTransition

class VCDParser:
    @classmethod
    def parse_file(cls, filepath: str) -> WaveformTrace:
        if not os.path.exists(filepath):
            return WaveformTrace(file_path=filepath)

        with open(filepath, 'r', encoding='utf-8', errors='ignore') as f:
            lines = f.readlines()

        timescale = "1ns"
        symbol_to_name = {}
        name_to_symbol = {}
        transitions: Dict[str, List[SignalTransition]] = {}
        current_time = 0

        in_definitions = True

        for line in lines:
            line = line.strip()
            if not line:
                continue

            if in_definitions:
                if line.startswith('$timescale'):
                    # e.g., $timescale 1ns $end or $timescale 1 ps $end
                    match = re.search(r'\$timescale\s+([0-9]+\s*[a-z]+)', line)
                    if match:
                        timescale = match.group(1).replace(' ', '')
                elif line.startswith('$var'):
                    # e.g., $var wire 1 ! clk $end or $var reg 8 ) data [7:0] $end
                    parts = line.split()
                    if len(parts) >= 6:
                        # var type size symbol name [range]
                        symbol = parts[3]
                        name = parts[4]
                        # Join name and range if present
                        if parts[5] != '$end':
                            name = f"{name}{parts[5]}"
                        symbol_to_name[symbol] = name
                        name_to_symbol[name] = symbol
                        transitions[name] = []
                elif line.startswith('$enddefinitions'):
                    in_definitions = False
            else:
                # Value change or timestamp
                if line.startswith('#'):
                    # Timestamp, e.g., #100
                    try:
                        current_time = int(line[1:])
                    except ValueError:
                        pass
                else:
                    # e.g. 1! or b00000000 ) or x!
                    if line.startswith('b') or line.startswith('B'):
                        # Vector value change, format: b<val> <symbol>
                        parts = line.split()
                        if len(parts) == 2:
                            val = parts[0][1:] # strip 'b'
                            symbol = parts[1]
                            if symbol in symbol_to_name:
                                name = symbol_to_name[symbol]
                                transitions[name].append(SignalTransition(time=current_time, value=val))
                    else:
                        # Scalar value change, format: <val><symbol>
                        # Value is first character: 0, 1, x, z, X, Z
                        val = line[0]
                        symbol = line[1:]
                        if symbol in symbol_to_name:
                            name = symbol_to_name[symbol]
                            transitions[name].append(SignalTransition(time=current_time, value=val))

        max_time = current_time

        return WaveformTrace(
            file_path=filepath,
            signals=list(transitions.keys()),
            timescale=timescale,
            transitions=transitions,
            max_time=max_time
        )
