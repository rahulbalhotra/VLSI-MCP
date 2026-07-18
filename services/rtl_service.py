import os
from typing import Dict, List, Optional, Any
from parsers.verilog_parser import VerilogParser
from models.rtl import Module, Signal

class RTLService:
    def __init__(self):
        # Cache mapping file_path -> List[Module]
        self._parsed_cache: Dict[str, List[Module]] = {}

    def parse_file(self, filepath: str, force: bool = False) -> List[Module]:
        if not force and filepath in self._parsed_cache:
            return self._parsed_cache[filepath]

        modules = VerilogParser.parse_file(filepath)
        if modules:
            self._parsed_cache[filepath] = modules
        return modules

    def get_module(self, module_name: str, search_dirs: List[str]) -> Optional[Module]:
        # First check in cache
        for modules in self._parsed_cache.values():
            for m in modules:
                if m.name == module_name:
                    return m

        # If not cached, search in directories
        for d in search_dirs:
            if not os.path.exists(d):
                continue
            for root, _, files in os.walk(d):
                for f in files:
                    if f.endswith((".v", ".sv")):
                        path = os.path.join(root, f)
                        modules = self.parse_file(path)
                        for m in modules:
                            if m.name == module_name:
                                return m
        return None

    def find_signal(self, signal_name: str, module_name: str, search_dirs: List[str]) -> Optional[Signal]:
        mod = self.get_module(module_name, search_dirs)
        if not mod:
            return None
            
        for sig in mod.signals:
            if sig.name == signal_name:
                return sig
                
        # Also check if it's in ports list
        for port in mod.ports:
            if port.name == signal_name:
                return Signal(
                    name=port.name,
                    width=port.width,
                    type="port",
                    drivers=[f"module input port" if port.direction == "input" else "internal assignment"],
                    loads=[],
                    module=module_name
                )
        return None

    def show_hierarchy(self, top_module: str, search_dirs: List[str]) -> Dict[str, Any]:
        """
        Builds recursive module hierarchy representation.
        """
        def build_tree(mod_name: str, path: List[str]) -> Dict[str, Any]:
            mod = self.get_module(mod_name, search_dirs)
            if not mod or mod_name in path: # avoid circular reference
                return {"module": mod_name, "instances": []}
                
            instances = []
            for inst in mod.instances:
                sub_tree = build_tree(inst.module_name, path + [mod_name])
                sub_tree["instance_name"] = inst.name
                instances.append(sub_tree)
                
            return {
                "module": mod_name,
                "file": mod.source_file if mod else "unknown",
                "instances": instances
            }

        return build_tree(top_module, [])

    def get_fsm(self, module_name: str, search_dirs: List[str]) -> Dict[str, Any]:
        mod = self.get_module(module_name, search_dirs)
        if not mod:
            return {"states": [], "transitions": [], "reset_state": None, "outputs": []}
        return VerilogParser.extract_fsm(mod.source_file, module_name)

    def find_clock_domains(self, module_name: str, search_dirs: List[str]) -> Dict[str, Any]:
        mod = self.get_module(module_name, search_dirs)
        if not mod:
            return {"clocks": [], "generated_clocks": [], "asynchronous_domains": []}

        clocks = []
        # Basic heuristics to find clocks
        # Port names containing 'clk', 'clock'
        for port in mod.ports:
            if 'clk' in port.name.lower() or 'clock' in port.name.lower():
                clocks.append(port.name)

        # Internal wires containing clk
        for sig in mod.signals:
            if 'clk' in sig.name.lower() or 'clock' in sig.name.lower():
                if sig.name not in clocks:
                    clocks.append(sig.name)

        return {
            "clocks": clocks,
            "generated_clocks": [],
            "asynchronous_domains": ["domain_main"] if len(clocks) > 0 else []
        }

    def find_reset_tree(self, module_name: str, search_dirs: List[str]) -> Dict[str, Any]:
        mod = self.get_module(module_name, search_dirs)
        if not mod:
            return {"resets": [], "reset_topology": {}}

        resets = []
        # Basic reset detection
        for port in mod.ports:
            if 'rst' in port.name.lower() or 'reset' in port.name.lower():
                resets.append(port.name)

        return {
            "resets": resets,
            "reset_topology": {r: "active_low" if 'rst_n' in r or 'rstn' in r else "active_high" for r in resets}
        }
