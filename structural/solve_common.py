"""Minimal shared solve plumbing, reused by every structural study driver.

Deliberately small: only the mechanics that are IDENTICAL across every
solve regardless of which study is running (fresh AMPL instance, per-worker
scratch dir, Threads=1, drop the bilinear monotonicity constraint, solve).
Everything study-specific (which axes vary, what gets extracted, output
shape) stays in each study's own run_*.py -- duplicating that here would
just be a different flavor of the copy-paste risk this file exists to avoid.
"""
import pathlib
import tempfile

HERE = pathlib.Path(__file__).resolve().parent
ROOT = HERE.parent


def new_ampl():
    """Fresh AMPL instance, cwd set to repo root, per-worker scratch dir.
    One instance per solve -- see run_matrix.py's module docstring for why
    reusing an instance across solves is unsafe (frozen `default` params)."""
    from amplpy import AMPL
    ampl = AMPL()
    ampl.cd(str(ROOT))
    ampl.set_option("solver_msg", 0)
    try:
        ampl.set_option("TMPDIR", tempfile.mkdtemp(prefix="amplwk_"))
    except Exception:
        pass
    return ampl


def solve(ampl, solver="gurobi"):
    """Apply the standard solver settings and solve. Returns solve_result."""
    ampl.eval(f"option solver {solver};")
    if solver == "gurobi":
        ampl.eval("option gurobi_options 'Threads=1';")
    ampl.eval("drop emission_monotonic;")
    ampl.eval("solve;")
    return ampl.get_value("solve_result")
