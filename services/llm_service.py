import os
from typing import Optional

try:
    import google.generativeai as genai
    HAS_GENAI = True
except ImportError:
    HAS_GENAI = False

class LLMService:
    def __init__(self, api_key: Optional[str] = None):
        self.api_key = api_key or os.environ.get("GEMINI_API_KEY")
        self.model_name = "gemini-1.5-flash"
        self._initialized = False

        if HAS_GENAI and self.api_key:
            try:
                genai.configure(api_key=self.api_key)
                self.model = genai.GenerativeModel(self.model_name)
                self._initialized = True
            except Exception:
                self._initialized = False

    def generate_text(self, prompt: str, system_instruction: Optional[str] = None) -> str:
        """
        Generates text using Gemini model with local fallbacks.
        """
        if self._initialized and HAS_GENAI:
            try:
                # Set up system instructions if supported
                if system_instruction:
                    model = genai.GenerativeModel(
                        self.model_name,
                        system_instruction=system_instruction
                    )
                else:
                    model = self.model

                response = model.generate_content(prompt)
                return response.text
            except Exception as e:
                # Fallback to local logic on API error
                pass

        return self._local_fallback(prompt)

    def _local_fallback(self, prompt: str) -> str:
        """
        Heuristic template-based fallbacks for offline execution.
        """
        prompt_lower = prompt.lower()
        
        # 1. SVA generation fallback
        if "systemverilog assertion" in prompt_lower or "sva" in prompt_lower:
            if "fifo overflow" in prompt_lower or "full" in prompt_lower:
                return (
                    "// Generated SystemVerilog Assertion (Offline Fallback)\n"
                    "property p_fifo_overflow;\n"
                    "  @(posedge clk) disable iff (!rst_n)\n"
                    "  (fifo_full && w_en) |-> (r_en);\n"
                    "endproperty\n"
                    "a_fifo_overflow: assert property (p_fifo_overflow);"
                )
            if "handshake" in prompt_lower or "req" in prompt_lower:
                return (
                    "// Generated SystemVerilog Assertion (Offline Fallback)\n"
                    "property p_handshake_response;\n"
                    "  @(posedge clk) disable iff (!rst_n)\n"
                    "  req |-> ##[1:5] gnt;\n"
                    "endproperty\n"
                    "a_handshake_response: assert property (p_handshake_response);"
                )
            return (
                "// Generated SystemVerilog Assertion (Offline Fallback)\n"
                "property p_generic_property;\n"
                "  @(posedge clk) disable iff (!rst_n)\n"
                "  signal_a |-> ##1 signal_b;\n"
                "endproperty\n"
                "a_generic: assert property (p_generic_property);"
            )

        # 2. SVA explanation fallback
        if "explain" in prompt_lower and ("property" in prompt_lower or "assert" in prompt_lower):
            return (
                "### SVA Explanation (Offline Fallback)\n"
                "This assertion checks a temporal relationship between design signals:\n"
                "- **Clocking**: Synced to the positive edge of the clock (`clk`).\n"
                "- **Trigger**: When the antecedent (trigger condition) is satisfied, it starts evaluating.\n"
                "- **Consequent**: The target condition must be satisfied within the specified clock cycle window."
            )

        # 3. Waveform explanation fallback
        if "waveform" in prompt_lower or "transition" in prompt_lower:
            return (
                "### Waveform Analysis (Offline Fallback)\n"
                "The trace shows typical transaction handshakes:\n"
                "1. `rst_n` deasserts, initializing the design.\n"
                "2. `req` transitions from 0 to 1, initiating a transaction.\n"
                "3. `state` transitions to REQ to await slave response.\n"
                "4. `gnt` is asserted to complete the handshake."
            )

        # 4. Optimization fallback
        if "optimize" in prompt_lower:
            return (
                "### SVA Optimization Suggestion (Offline Fallback)\n"
                "Consider the following optimizations:\n"
                "1. Restrict the delay range from unbounded (e.g. `##[1:$]`) to bounded (e.g. `##[1:100]`) to reduce formal solver search space.\n"
                "2. Ensure local variables are avoided unless strictly necessary."
            )

        return "This is a local fallback response. Configure GEMINI_API_KEY for real LLM output."
