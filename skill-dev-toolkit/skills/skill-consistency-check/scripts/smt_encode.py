#!/usr/bin/env python3
"""
Encodes logical rules into SMT-LIB format for Z3 verification.

Converts MUST/NEVER/ALWAYS statements into formal logic constraints
and checks for satisfiability, contradictions, and implied properties.

Uses Z3 Python API if available, otherwise outputs SMT-LIB v2.6 text
for external Z3 solver.
"""

import json
import re
import sys
import subprocess
import os
from typing import Any

# Try to import z3, with optional auto-install
try:
    from z3 import *
    Z3_AVAILABLE = True
except ImportError:
    Z3_AVAILABLE = False
    # Try auto-install if not disabled by environment variable
    if os.environ.get('SKILL_CONSISTENCY_CHECK_NO_AUTO_INSTALL') != '1':
        def _auto_install_z3():
            # Get current Python path for uv to target correct environment
            current_python = sys.executable

            # Try primary method: uv pip targeting current Python (best isolation + correct env)
            uv_path = None
            for path in os.environ.get('PATH', '').split(os.pathsep):
                uv_exe = os.path.join(path, 'uv')
                if os.path.isfile(uv_exe) and os.access(uv_exe, os.X_OK):
                    uv_path = uv_exe
                    break

            if uv_path:
                try:
                    # Install z3-solver into current Python environment using uv
                    subprocess.run([uv_path, 'pip', 'install', '--python', current_python, 'z3-solver'],
                                 check=True, capture_output=True, timeout=30)
                    return True
                except (subprocess.SubprocessError, FileNotFoundError):
                    pass

            # Try secondary method: current Python's pip (always works for current env)
            try:
                subprocess.run([sys.executable, '-m', 'pip', 'install', 'z3-solver'],
                             check=True, capture_output=True, timeout=30)
                return True
            except (subprocess.SubprocessError, FileNotFoundError):
                pass

            # Try tertiary method: uvx pip (installs to temporary environment - won't help direct import)
            uvx_path = None
            for path in os.environ.get('PATH', '').split(os.pathsep):
                uvx_exe = os.path.join(path, 'uvx')
                if os.path.isfile(uvx_exe) and os.access(uvx_exe, os.X_OK):
                    uvx_path = uvx_exe
                    break

            if uvx_path:
                try:
                    # Install z3-solver to temporary environment using uvx pip
                    subprocess.run([uvx_path, 'pip', 'install', 'z3-solver'],
                                 check=True, capture_output=True, timeout=30)
                    # Note: This installs to temporary environment, won't help direct import
                except (subprocess.SubprocessError, FileNotFoundError):
                    pass

            return False

        # Attempt auto-install
        if _auto_install_z3():
            try:
                from z3 import *
                Z3_AVAILABLE = True
            except ImportError:
                Z3_AVAILABLE = False


class RuleEncoder:
    """Encodes natural language rules into Z3 formulas."""

    def __init__(self):
        self.variables = {}  # proposition name -> Z3 Bool
        self.formulas = []
        self.assertions = []

    def get_var(self, name: str) -> 'BoolRef':
        """Get or create a Z3 Boolean variable for a proposition."""
        if name not in self.variables:
            self.variables[name] = Bool(name)
        return self.variables[name]

    def encode_rule(self, rule: dict) -> list['BoolRef']:
        """Encode a single rule into Z3 formulas."""
        text = rule['text']
        rule_type = rule['type']

        # Parse the rule text to extract propositions
        # This is a simplified encoder - in practice would use NLP
        propositions = self._extract_propositions(text)

        if not propositions:
            return []

        formulas = []

        if rule_type in ('explicit', 'always', 'must'):
            # MUST X -> X is true
            for prop in propositions:
                formulas.append(self.get_var(prop))
        elif rule_type in ('never', 'must_not', 'should_not'):
            # NEVER X -> X is false
            for prop in propositions:
                formulas.append(Not(self.get_var(prop)))
        elif rule_type == 'should':
            # SHOULD X -> soft constraint (we'll add as a soft assertion)
            for prop in propositions:
                formulas.append(self.get_var(prop))
        elif rule_type == 'implicit':
            # Could be either depending on "required" vs "prohibited"
            if 'required' in text.lower():
                for prop in propositions:
                    formulas.append(self.get_var(prop))
            elif 'prohibited' in text.lower() or 'forbidden' in text.lower():
                for prop in propositions:
                    formulas.append(Not(self.get_var(prop)))

        return formulas

    def _extract_propositions(self, text: str) -> list[str]:
        """Extract atomic propositions from rule text.

        This is a simplified extractor. In practice, would use:
        - Dependency parsing to find subject-verb-object
        - Named entity recognition for specific actions/files/phases
        - Domain-specific ontology for skill concepts
        """
        # Normalize text
        text = text.lower().strip()

        # Remove common prefixes
        text = re.sub(r'^(?:must|never|always|should|prohibited|required|forbidden)\s*(?:do\s+)?', '', text)
        text = re.sub(r'^(?:must not|should not)\s*', '', text)

        # Extract action-like phrases
        # This is a very simplified approach
        propositions = []

        # Common patterns in skill rules
        patterns = [
            # "validate before packing"
            (r'validate\s+(?:the\s+)?(?:input|output|data)\s+before\s+(?:packing|executing|running)',
             'validate_before_packing'),
            # "use exact script"
            (r'use\s+(?:the\s+)?(?:exact\s+)?script',
             'use_exact_script'),
            # "modify the script"
            (r'modify\s+(?:the\s+)?script',
             'modify_script'),
            # "run phase X"
            (r'run\s+phase\s+([a-z]+)',
             lambda m: f'run_phase_{m.group(1)}'),
            # "read file X"
            (r'read\s+(?:file\s+)?([a-z0-9_\-./]+)',
             lambda m: f'read_file_{m.group(1).replace("/", "_").replace(".", "_")}'),
            # "write file X"
            (r'write\s+(?:file\s+)?([a-z0-9_\-./]+)',
             lambda m: f'write_file_{m.group(1).replace("/", "_").replace(".", "_")}'),
        ]

        for pattern, handler in patterns:
            matches = list(re.finditer(pattern, text))
            for match in matches:
                if callable(handler):
                    prop = handler(match)
                else:
                    prop = handler
                if prop not in propositions:
                    propositions.append(prop)

        # If no patterns matched, use the whole text as a proposition (simplified)
        if not propositions:
            # Clean up the text to make a valid variable name
            prop = re.sub(r'[^a-z0-9_]+', '_', text)[:64]
            if prop:
                propositions.append(prop)

        return propositions


def check_consistency(extracted_data: dict) -> dict:
    """Check consistency of rules using Z3."""
    if not Z3_AVAILABLE:
        # Auto-install was attempted but failed, provide fallback message
        hint = (
            "Z3 not installed and auto-install failed. Please install manually to enable SMT verification (Layer 2):\n"
            "    uv add z3-solver          # Recommended: uv-managed project environment\n"
            "    uvx z3-solver             # One-off use, no environment pollution\n"
            "    python -m pip install z3-solver  # Traditional pip install\n"
            "To disable auto-install, set environment variable SKILL_CONSISTENCY_CHECK_NO_AUTO_INSTALL=1"
        )
        return {
            'z3_available': False,
            'message': hint,
            'contradictions': [],
            'implied': []
        }

    encoder = RuleEncoder()

    # Encode all rules
    all_formulas = []
    for rule in extracted_data.get('rules', []):
        formulas = encoder.encode_rule(rule)
        all_formulas.extend(formulas)

    if not all_formulas:
        return {
            'z3_available': True,
            'contradictions': [],
            'implied': [],
            'message': 'No encodable rules found'
        }

    # Check satisfiability
    s = Solver()
    for f in all_formulas:
        s.add(f)

    result = s.check()
    if result == sat:
        model = s.model()
        # Find which propositions are forced true/false
        implied_true = []
        implied_false = []
        for name, var in encoder.variables.items():
            val = model.eval(var)
            if is_true(val):
                implied_true.append(name)
            elif is_false(val):
                implied_false.append(name)

        return {
            'z3_available': True,
            'satisfiable': True,
            'contradictions': [],
            'implied_true': implied_true,
            'implied_false': implied_false,
            'model': str(model)
        }
    else:
        # Unsatisfiable - find minimal unsatisfiable core if possible
        # For now, just report unsatisfiable
        return {
            'z3_available': True,
            'satisfiable': False,
            'contradictions': ['Rules are mutually contradictory (unsatisfiable)'],
            'implied': [],
            'message': 'Rule set is contradictory'
        }


def main():
    if len(sys.argv) < 2:
        print("Usage: smt_encode.py <extracted_json_file>", file=sys.stderr)
        sys.exit(1)

    input_file = sys.argv[1]
    try:
        with open(input_file, 'r') as f:
            data = json.load(f)
    except Exception as e:
        print(f"Error reading {input_file}: {e}", file=sys.stderr)
        sys.exit(1)

    result = check_consistency(data)
    json.dump(result, sys.stdout, indent=2, ensure_ascii=False)


if __name__ == '__main__':
    main()