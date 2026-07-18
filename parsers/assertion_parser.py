import re
from typing import List
from models.assertion import LintResult

class AssertionParser:
    @classmethod
    def lint_assertion(cls, name: str, property_expr: str) -> LintResult:
        """
        Lints a SystemVerilog Assertion (SVA) expression.
        Checks:
        1. Matching braces, parentheses, and brackets.
        2. Trivial vacuity (e.g., constant 1 or 0, or check if implication antecedent is simple true/false).
        3. Syntax check (e.g., presence of assert, property, clocking).
        4. Overlapping implications (e.g. multiple |-> or |=> on same path).
        """
        errors: List[str] = []
        warnings: List[str] = []
        vacuity_risk = False
        overlapping_implications = False

        # 1. Bracket Matching Check
        brackets = {'(': ')', '{': '}', '[': ']'}
        stack = []
        for char in property_expr:
            if char in brackets.keys():
                stack.append(char)
            elif char in brackets.values():
                if not stack or brackets[stack.pop()] != char:
                    errors.append("Mismatched parentheses/braces/brackets.")
                    break
        if stack and not errors:
            errors.append("Unclosed parentheses/braces/brackets.")

        # 2. Syntax Check
        if not re.search(r'\bassert\s+property\b', property_expr) and not re.search(r'\bcover\s+property\b', property_expr):
            warnings.append("Expression does not contain 'assert property' or 'cover property' wrapper.")

        if not re.search(r'@\s*\(\s*(?:posedge|negedge)\b', property_expr):
            warnings.append("No clock triggering event (e.g. '@(posedge clk)') detected.")

        # 3. Vacuity check
        # Check if the consequent is trivial (e.g., |-> 1 or |-> true or is a simple constant)
        # Check if it has an implication: |-> or |=>
        implication_match = re.search(r'(\|\-\>|\|\=\>)\s*(.*)$', property_expr)
        if implication_match:
            consequent = implication_match.group(2).strip()
            # Remove ending semicolon or parenthesis if any
            consequent_clean = re.sub(r'[;\)]+$', '', consequent).strip()
            if consequent_clean in ["1", "1'b1", "true", "TRUE"]:
                warnings.append("Trivial vacuity risk: Consequent is always true.")
                vacuity_risk = True
            
            # Antecedent check
            antecedent = property_expr.split(implication_match.group(1))[0]
            # If antecedent contains a constant 0, it will never trigger
            if re.search(r'\b0\b|\b0\'b0\b|\bfalse\b', antecedent, re.IGNORECASE):
                warnings.append("Vacuity risk: Antecedent contains a constant false, assertion will never trigger.")
                vacuity_risk = True
        else:
            # No implication, check if the whole expression has trivial constant
            body_match = re.search(r'property\s*\(\s*(.*?)\s*\)', property_expr)
            if body_match:
                expr_body = body_match.group(1).strip()
                if expr_body in ["1", "1'b1", "true", "0", "1'b0", "false"]:
                    warnings.append(f"Assertion property body is a constant: '{expr_body}'")
                    vacuity_risk = True

        # 4. Overlapping Implications Check
        # e.g., req |-> gnt |-> ack
        if len(re.findall(r'\|\-\>|\|\=\>', property_expr)) > 1:
            warnings.append("Overlapping implications: Multiple implication operators (|-> or |=>) detected in single property.")
            overlapping_implications = True

        # Unsupported construct check
        unsupported_keywords = ['expect', 'strong', 'weak', 'restrict']
        for kw in unsupported_keywords:
            if re.search(rf'\b{kw}\b', property_expr):
                warnings.append(f"Construct '{kw}' might not be supported by all formal engines.")

        has_error = len(errors) > 0

        return LintResult(
            assertion_name=name,
            has_error=has_error,
            errors=errors,
            warnings=warnings,
            vacuity_risk=vacuity_risk,
            overlapping_implications=overlapping_implications
        )
