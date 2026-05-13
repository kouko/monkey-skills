#!/usr/bin/env python3
# /// script
# requires-python = ">=3.10"
# dependencies = []
# ///
"""
cld_simulator.py — manager-grade stock-flow simulator (v0.10).

Pedagogical companion to the systems-thinking-toolkit simulation-modeling skill.
Reads a JSON spec describing stocks, flows, and parameters; integrates with
Euler stepping; emits CSV time-series and/or ASCII line charts.

Honest caveats:
  - Euler integration only (no RK4 / adaptive step). Sufficient for learning,
    not for stiff / oscillatory systems requiring high accuracy.
  - Stdlib only (math + json + csv + argparse + ast + sys). No numpy / matplotlib.
  - Pedagogical, not research-grade. For PySD / BPTK-Py scale work, switch tool.
  - Equation parser is safe: a whitelisted AST evaluator that rejects imports,
    dunder access, attribute access, calls to non-whitelisted names, etc.

Usage:
    uv run cld_simulator.py spec.json [--output csv|ascii-chart|both]
                                       [--out FILE]
                                       [--duration N] [--dt 0.1]

JSON spec schema (informal):
    {
      "name": "exponential-growth",
      "duration": 50,
      "dt": 0.1,
      "stocks": { "StockName": initial_value, ... },
      "flows":  { "FlowName": { "to": "StockName"            (inflow),
                                "from": "StockName"          (outflow),
                                "equation": "expr over stocks+params" }, ... },
      "parameters": { "ParamName": numeric_value, ... },
      "outputs": ["StockName", ...]   (optional; defaults to all stocks)
    }

A flow may have both "to" and "from" (transfer between stocks).
"""

from __future__ import annotations

import argparse
import ast
import csv
import io
import json
import math
import sys
from typing import Any


# ---------------------------------------------------------------------------
# Safe expression evaluator (whitelisted AST walk).
# ---------------------------------------------------------------------------

# Math functions exposed inside equations. Add sparingly — every name here is
# an attack surface if it can mutate state or touch the filesystem.
SAFE_FUNCS: dict[str, Any] = {
    "abs": abs,
    "min": min,
    "max": max,
    "round": round,
    "exp": math.exp,
    "log": math.log,
    "sqrt": math.sqrt,
    "sin": math.sin,
    "cos": math.cos,
    "tan": math.tan,
    "pi": math.pi,
    "e": math.e,
}

# Whitelisted AST node types. Anything not in this set is rejected.
_ALLOWED_NODES = (
    ast.Expression,
    ast.BinOp, ast.UnaryOp,
    ast.Add, ast.Sub, ast.Mult, ast.Div, ast.FloorDiv, ast.Mod, ast.Pow,
    ast.USub, ast.UAdd,
    ast.Constant,
    ast.Name, ast.Load,
    ast.Call,
    ast.Compare,
    ast.Lt, ast.LtE, ast.Gt, ast.GtE, ast.Eq, ast.NotEq,
    ast.BoolOp, ast.And, ast.Or, ast.Not,
    ast.IfExp,
)


class EquationError(ValueError):
    """Raised when an equation is malformed or references an unknown name."""


def _validate_ast(tree: ast.AST, equation: str) -> None:
    """Walk the tree and reject any disallowed node (incl. attribute access)."""
    for node in ast.walk(tree):
        if isinstance(node, ast.Attribute):
            raise EquationError(
                f"attribute access not allowed in equation {equation!r} "
                f"(got `.{node.attr}`)"
            )
        if isinstance(node, ast.Name) and node.id.startswith("_"):
            raise EquationError(
                f"underscore-prefixed name not allowed in equation "
                f"{equation!r} (got {node.id!r})"
            )
        if isinstance(node, ast.Call):
            # Function must be a plain Name node (e.g. exp(x), not foo.bar(x)).
            if not isinstance(node.func, ast.Name):
                raise EquationError(
                    f"only simple function calls allowed in equation "
                    f"{equation!r}"
                )
            if node.func.id not in SAFE_FUNCS:
                raise EquationError(
                    f"function {node.func.id!r} not in safe whitelist "
                    f"({sorted(SAFE_FUNCS)})"
                )
        if not isinstance(node, _ALLOWED_NODES):
            raise EquationError(
                f"syntax node {type(node).__name__} not allowed in equation "
                f"{equation!r}"
            )


def compile_equation(equation: str) -> ast.Expression:
    """Parse + validate; return the AST. Raises EquationError on rejection."""
    try:
        tree = ast.parse(equation, mode="eval")
    except SyntaxError as e:
        raise EquationError(f"equation {equation!r} has syntax error: {e}") from e
    _validate_ast(tree, equation)
    return tree


def evaluate(tree: ast.Expression, scope: dict[str, float]) -> float:
    """Evaluate a pre-validated equation AST against a scope of stock/param values."""
    # scope contains only numbers; SAFE_FUNCS provides math functions.
    # We assemble a combined namespace and use eval() on the compiled AST.
    # Safety: tree is already validated; no `import`, no attr access, no dunder,
    # no non-whitelisted calls. eval cannot reach module globals because we pass
    # __builtins__: {}.
    namespace = {"__builtins__": {}}
    namespace.update(SAFE_FUNCS)
    namespace.update(scope)
    try:
        code = compile(tree, filename="<equation>", mode="eval")
        result = eval(code, namespace)
    except NameError as e:
        # Extract the bad name; raise our typed error.
        msg = str(e)
        raise EquationError(f"undefined variable in equation: {msg}") from e
    except ZeroDivisionError as e:
        raise EquationError(f"division by zero in equation: {e}") from e
    if not isinstance(result, (int, float)) or isinstance(result, bool):
        raise EquationError(f"equation did not return a number, got {result!r}")
    return float(result)


# ---------------------------------------------------------------------------
# Spec loading and validation.
# ---------------------------------------------------------------------------

class SpecError(ValueError):
    """Raised when a JSON spec is structurally invalid."""


def load_spec(path: str) -> dict[str, Any]:
    try:
        with open(path) as f:
            spec = json.load(f)
    except FileNotFoundError:
        raise SpecError(f"spec file not found: {path}")
    except json.JSONDecodeError as e:
        raise SpecError(f"spec {path!r} has invalid JSON: {e}")
    if not isinstance(spec, dict):
        raise SpecError(f"spec must be a JSON object at top level (got {type(spec).__name__})")
    for required in ("stocks", "flows"):
        if required not in spec:
            raise SpecError(f"spec missing required key {required!r}")
    if not isinstance(spec["stocks"], dict) or not spec["stocks"]:
        raise SpecError("spec.stocks must be a non-empty object")
    if not isinstance(spec["flows"], dict):
        raise SpecError("spec.flows must be an object")
    # validate stocks are numeric
    for name, val in spec["stocks"].items():
        if not isinstance(val, (int, float)) or isinstance(val, bool):
            raise SpecError(f"stock {name!r} initial value must be numeric (got {val!r})")
    # validate parameters
    params = spec.get("parameters", {})
    if not isinstance(params, dict):
        raise SpecError("spec.parameters must be an object")
    for name, val in params.items():
        if not isinstance(val, (int, float)) or isinstance(val, bool):
            raise SpecError(f"parameter {name!r} must be numeric (got {val!r})")
    # validate flows
    stock_names = set(spec["stocks"].keys())
    for fname, fdef in spec["flows"].items():
        if not isinstance(fdef, dict):
            raise SpecError(f"flow {fname!r} must be an object")
        if "equation" not in fdef:
            raise SpecError(f"flow {fname!r} missing required key 'equation'")
        if not isinstance(fdef["equation"], str):
            raise SpecError(f"flow {fname!r} equation must be a string")
        if "to" not in fdef and "from" not in fdef:
            raise SpecError(f"flow {fname!r} needs at least one of 'to' / 'from'")
        for direction in ("to", "from"):
            target = fdef.get(direction)
            if target is not None:
                if not isinstance(target, str):
                    raise SpecError(f"flow {fname!r} {direction!r} must be a string")
                if target not in stock_names:
                    raise SpecError(
                        f"flow {fname!r} {direction!r}={target!r} references unknown stock"
                    )
    return spec


# ---------------------------------------------------------------------------
# Simulation core (Euler integration).
# ---------------------------------------------------------------------------

def simulate(spec: dict[str, Any], duration: float | None = None,
             dt: float | None = None) -> tuple[list[float], dict[str, list[float]]]:
    """Run Euler integration. Returns (times, {stock: [values per step]}).

    CLI override values (duration, dt) take precedence over the spec values.
    """
    sim_duration = duration if duration is not None else float(spec.get("duration", 10.0))
    sim_dt = dt if dt is not None else float(spec.get("dt", 0.1))
    if sim_duration <= 0:
        raise SpecError(f"duration must be > 0 (got {sim_duration})")
    if sim_dt <= 0:
        raise SpecError(f"dt must be > 0 (got {sim_dt})")

    stocks = {name: float(val) for name, val in spec["stocks"].items()}
    params = {name: float(val) for name, val in spec.get("parameters", {}).items()}

    # Pre-compile all flow equations so syntax/whitelist failures fail early.
    compiled_flows = {}
    for fname, fdef in spec["flows"].items():
        compiled_flows[fname] = {
            "ast": compile_equation(fdef["equation"]),
            "to": fdef.get("to"),
            "from": fdef.get("from"),
        }

    # Number of steps. Include both endpoints (t=0 and t=duration), so
    # steps = round(duration / dt) + 1.
    n_steps = int(round(sim_duration / sim_dt)) + 1

    times: list[float] = [0.0]
    history: dict[str, list[float]] = {name: [stocks[name]] for name in stocks}

    for step in range(1, n_steps):
        t = step * sim_dt
        # Compute scope (current stock values + params).
        scope = dict(params)
        scope.update(stocks)
        # Compute every flow's rate at the start of the interval.
        rates = {fname: evaluate(f["ast"], scope) for fname, f in compiled_flows.items()}
        # Apply rates to stocks: Euler step.
        new_stocks = dict(stocks)
        for fname, f in compiled_flows.items():
            rate = rates[fname]
            delta = rate * sim_dt
            if f["to"] is not None:
                new_stocks[f["to"]] = new_stocks[f["to"]] + delta
            if f["from"] is not None:
                new_stocks[f["from"]] = new_stocks[f["from"]] - delta
        stocks = new_stocks
        times.append(t)
        for name, val in stocks.items():
            history[name].append(val)

    return times, history


# ---------------------------------------------------------------------------
# Output: CSV.
# ---------------------------------------------------------------------------

def emit_csv(times: list[float], history: dict[str, list[float]],
             outputs: list[str], stream) -> None:
    writer = csv.writer(stream)
    writer.writerow(["time"] + outputs)
    for i, t in enumerate(times):
        row = [f"{t:.6g}"] + [f"{history[name][i]:.6g}" for name in outputs]
        writer.writerow(row)


# ---------------------------------------------------------------------------
# Output: ASCII line chart.
# ---------------------------------------------------------------------------

def emit_ascii_chart(times: list[float], history: dict[str, list[float]],
                     outputs: list[str], stream,
                     height: int = 20, max_width: int = 80) -> None:
    """Render a simple ASCII chart per stock.

    Algorithm: downsample to max_width columns, normalize each series to
    [0, height-1], plot '*' at the data row and '.' elsewhere. Y-axis labels
    show min/max; x-axis labels show t_min / t_max.
    """
    n = len(times)
    if n == 0:
        stream.write("(no data)\n")
        return
    # Downsample column indices.
    width = min(n, max_width)
    if n <= width:
        col_idx = list(range(n))
    else:
        # uniform sample
        col_idx = [int(round(i * (n - 1) / (width - 1))) for i in range(width)]

    for name in outputs:
        series = history[name]
        sampled = [series[i] for i in col_idx]
        vmin = min(sampled)
        vmax = max(sampled)
        span = vmax - vmin
        # Build grid: row 0 is top (vmax), row height-1 is bottom (vmin).
        grid = [[" "] * width for _ in range(height)]
        for x, v in enumerate(sampled):
            if span == 0:
                y = height // 2
            else:
                y = int(round((vmax - v) / span * (height - 1)))
            y = max(0, min(height - 1, y))
            grid[y][x] = "*"

        # Header.
        stream.write(f"\n{name}: min={vmin:.4g} max={vmax:.4g} "
                     f"t=[{times[0]:.4g}, {times[-1]:.4g}] "
                     f"n={n} (downsampled to {width})\n")
        # Y-axis: label first row with vmax, last row with vmin.
        label_max = f"{vmax:8.4g} |"
        label_min = f"{vmin:8.4g} |"
        label_blank = " " * (len(label_max) - 1) + "|"
        for row in range(height):
            prefix = label_max if row == 0 else (label_min if row == height - 1 else label_blank)
            stream.write(prefix + "".join(grid[row]) + "\n")
        # X-axis baseline.
        stream.write(" " * (len(label_max) - 1) + "+" + "-" * width + "\n")
        stream.write(" " * len(label_max) + f"t={times[0]:<.4g}"
                     + " " * max(0, width - 12 - len(f"{times[-1]:.4g}"))
                     + f" t={times[-1]:.4g}\n")


# ---------------------------------------------------------------------------
# CLI.
# ---------------------------------------------------------------------------

def build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(
        prog="cld_simulator",
        description="Manager-grade stock-flow simulator (pedagogical companion "
                    "to simulation-modeling skill).")
    p.add_argument("spec", help="JSON spec file path")
    p.add_argument("--output", choices=("csv", "ascii-chart", "both"),
                   default="ascii-chart",
                   help="Output format (default: ascii-chart)")
    p.add_argument("--out", default=None,
                   help="Write CSV to this file (only meaningful with "
                        "--output csv|both). Default: stdout.")
    p.add_argument("--duration", type=float, default=None,
                   help="Override spec.duration")
    p.add_argument("--dt", type=float, default=None,
                   help="Override spec.dt")
    return p


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)

    try:
        spec = load_spec(args.spec)
    except SpecError as e:
        print(f"ERROR: spec invalid: {e}", file=sys.stderr)
        return 2

    try:
        times, history = simulate(spec, duration=args.duration, dt=args.dt)
    except (SpecError, EquationError) as e:
        print(f"ERROR: simulation failed: {e}", file=sys.stderr)
        return 3

    outputs = spec.get("outputs") or list(spec["stocks"].keys())
    # validate outputs are real stocks
    for name in outputs:
        if name not in history:
            print(f"ERROR: output {name!r} is not a known stock", file=sys.stderr)
            return 4

    if args.output in ("csv", "both"):
        if args.out:
            with open(args.out, "w", newline="") as f:
                emit_csv(times, history, outputs, f)
            print(f"wrote CSV to {args.out}", file=sys.stderr)
        else:
            emit_csv(times, history, outputs, sys.stdout)
    if args.output in ("ascii-chart", "both"):
        emit_ascii_chart(times, history, outputs, sys.stdout)

    return 0


if __name__ == "__main__":
    sys.exit(main())
