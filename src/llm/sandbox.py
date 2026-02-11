"""Sandboxed code execution for LLM-generated Python code."""

import logging
import multiprocessing
import queue
import re
import types
from typing import Any

import numpy as np
import pandas as pd

from src.llm.exceptions import SandboxError, SandboxTimeoutError

logger = logging.getLogger(__name__)

DEFAULT_TIMEOUT = 30

# Dangerous patterns to reject before execution
FORBIDDEN_PATTERNS: list[re.Pattern] = [
    re.compile(r"\bimport\b"),
    re.compile(r"\bopen\s*\("),
    re.compile(r"\bexec\s*\("),
    re.compile(r"\beval\s*\("),
    re.compile(r"\bcompile\s*\("),
    re.compile(r"__\w+__"),
    re.compile(r"\bos\s*\."),
    re.compile(r"\bsys\s*\."),
    re.compile(r"\bsubprocess\b"),
    re.compile(r"\bglobals\s*\("),
    re.compile(r"\blocals\s*\("),
    re.compile(r"\bgetattr\s*\("),
    re.compile(r"\bsetattr\s*\("),
    re.compile(r"\bdelattr\s*\("),
    re.compile(r"\bbreakpoint\s*\("),
    # Block file I/O via pandas
    re.compile(r"\.read_csv\s*\("),
    re.compile(r"\.read_parquet\s*\("),
    re.compile(r"\.read_json\s*\("),
    re.compile(r"\.read_excel\s*\("),
    re.compile(r"\.read_sql\s*\("),
    re.compile(r"\.read_html\s*\("),
    re.compile(r"\.read_fwf\s*\("),
    re.compile(r"\.read_clipboard\s*\("),
    re.compile(r"\.read_table\s*\("),
    re.compile(r"\.to_csv\s*\("),
    re.compile(r"\.to_parquet\s*\("),
    re.compile(r"\.to_json\s*\("),
    re.compile(r"\.to_excel\s*\("),
    re.compile(r"\.to_sql\s*\("),
    re.compile(r"\.to_html\s*\("),
    re.compile(r"\.to_clipboard\s*\("),
    re.compile(r"\.to_pickle\s*\("),
    re.compile(r"\.read_pickle\s*\("),
    # Block numpy file I/O and pickle-based deserialization
    re.compile(r"\bnp\.load\s*\("),
    re.compile(r"\bnp\.save\s*\("),
    re.compile(r"\bnp\.savez\s*\("),
    re.compile(r"\bnp\.savez_compressed\s*\("),
    re.compile(r"\bnp\.loadtxt\s*\("),
    re.compile(r"\bnp\.savetxt\s*\("),
    re.compile(r"\bnp\.genfromtxt\s*\("),
    re.compile(r"\bnp\.fromfile\s*\("),
    re.compile(r"\bnp\.memmap\s*\("),
    re.compile(r"\bnp\.lib\.format\.open_memmap\s*\("),
    re.compile(r"\bnp\.lib\.npyio\.NpzFile\s*\("),
    # Block pandas eval (expression evaluation engine)
    re.compile(r"\bpd\.eval\s*\("),
]

# File I/O-capable attributes blocked at runtime via guarded module proxy.
# This blocks alias-based escapes (e.g., "f = np.memmap; f(...)") that regex
# checks alone cannot reliably prevent.
BLOCKED_ATTRIBUTE_PATHS: set[str] = {
    # NumPy
    "np.load",
    "np.save",
    "np.savez",
    "np.savez_compressed",
    "np.loadtxt",
    "np.savetxt",
    "np.genfromtxt",
    "np.fromfile",
    "np.memmap",
    "np.lib.format.open_memmap",
    "np.lib.npyio.NpzFile",
    "np.ndarray.dump",
    "np.ndarray.tofile",
    # pandas module-level read APIs
    "pd.read_csv",
    "pd.read_parquet",
    "pd.read_json",
    "pd.read_excel",
    "pd.read_sql",
    "pd.read_html",
    "pd.read_fwf",
    "pd.read_clipboard",
    "pd.read_table",
    "pd.read_pickle",
    "pd.read_feather",
    "pd.read_hdf",
    "pd.read_orc",
    # pandas write/serialization APIs
    "pd.DataFrame.to_csv",
    "pd.DataFrame.to_parquet",
    "pd.DataFrame.to_json",
    "pd.DataFrame.to_excel",
    "pd.DataFrame.to_sql",
    "pd.DataFrame.to_html",
    "pd.DataFrame.to_clipboard",
    "pd.DataFrame.to_pickle",
    "pd.DataFrame.to_feather",
    "pd.DataFrame.to_hdf",
    "pd.DataFrame.to_orc",
    "pd.Series.to_csv",
    "pd.Series.to_json",
    "pd.Series.to_pickle",
}

# Allowed builtins (whitelist)
ALLOWED_BUILTINS: dict[str, Any] = {
    "abs": abs,
    "all": all,
    "any": any,
    "bool": bool,
    "dict": dict,
    "enumerate": enumerate,
    "float": float,
    "int": int,
    "isinstance": isinstance,
    "len": len,
    "list": list,
    "max": max,
    "min": min,
    "range": range,
    "round": round,
    "set": set,
    "sorted": sorted,
    "str": str,
    "sum": sum,
    "tuple": tuple,
    "zip": zip,
    "True": True,
    "False": False,
    "None": None,
}


def _has_blocked_descendants(path: str) -> bool:
    """Return True when any blocked path is nested under the given path."""
    prefix = f"{path}."
    return any(blocked.startswith(prefix) for blocked in BLOCKED_ATTRIBUTE_PATHS)


class _GuardedProxy:
    """Guarded attribute proxy that blocks file I/O capable APIs."""

    def __init__(self, obj: Any, path: str):
        self._obj = obj
        self._path = path

    def __getattr__(self, name: str) -> Any:
        full_path = f"{self._path}.{name}"
        if full_path in BLOCKED_ATTRIBUTE_PATHS:
            raise SandboxError(f"Forbidden API access: '{full_path}'")

        attr = getattr(self._obj, name)
        if isinstance(attr, types.ModuleType) or _has_blocked_descendants(full_path):
            return _GuardedProxy(attr, full_path)
        return attr

    def __call__(self, *args: Any, **kwargs: Any) -> Any:
        return self._obj(*args, **kwargs)


def _check_forbidden_patterns(code: str) -> None:
    """Static check for dangerous patterns in code string."""
    for pattern in FORBIDDEN_PATTERNS:
        match = pattern.search(code)
        if match:
            raise SandboxError(f"Forbidden pattern detected: '{match.group()}'")


def _build_namespace(df: pd.DataFrame) -> dict[str, Any]:
    """Build restricted execution namespace."""
    return {
        "__builtins__": ALLOWED_BUILTINS,
        "df": df.copy(),
        "pd": _GuardedProxy(pd, "pd"),
        "np": _GuardedProxy(np, "np"),
    }


def _sandbox_worker(
    code: str,
    df: pd.DataFrame,
    result_queue: Any,
) -> None:
    """Execute user code in worker process and send structured result."""
    try:
        _check_forbidden_patterns(code)
        namespace = _build_namespace(df)
        exec(code, namespace)  # noqa: S102

        if "result" not in namespace:
            raise SandboxError("Code must assign a value to the 'result' variable")

        try:
            result_queue.put(
                {
                    "status": "ok",
                    "result": namespace["result"],
                }
            )
        except Exception:
            result_queue.put(
                {
                    "status": "exec_error",
                    "error_type": "UnserializableResult",
                }
            )
    except SandboxError as e:
        result_queue.put(
            {
                "status": "sandbox_error",
                "message": str(e),
            }
        )
    except Exception as e:
        result_queue.put(
            {
                "status": "exec_error",
                "error_type": type(e).__name__,
            }
        )


def execute_in_sandbox(
    code: str,
    df: pd.DataFrame,
    timeout_seconds: int = DEFAULT_TIMEOUT,
) -> Any:
    """Execute code in a restricted sandbox.

    Args:
        code: Python code string to execute. Must assign to ``result`` variable.
        df: DataFrame to make available as ``df`` (a copy is used).
        timeout_seconds: Maximum execution time in seconds.

    Returns:
        The value of the ``result`` variable after execution.

    Raises:
        SandboxError: If code contains forbidden patterns or result is not defined.
        SandboxTimeoutError: If execution exceeds timeout.
    """
    # Step 1: Static pattern check
    _check_forbidden_patterns(code)

    # Step 2: Execute in worker process with timeout-safe join.
    ctx = multiprocessing.get_context("spawn")
    result_queue = ctx.Queue(maxsize=1)
    worker = ctx.Process(
        target=_sandbox_worker,
        args=(code, df, result_queue),
        daemon=True,
    )

    worker.start()
    worker.join(timeout_seconds)

    if worker.is_alive():
        worker.terminate()
        worker.join()
        raise SandboxTimeoutError("Code execution timed out")

    try:
        payload = result_queue.get_nowait()
    except queue.Empty:
        logger.warning(
            "Sandbox worker exited without payload (exitcode=%s)",
            worker.exitcode,
        )
        raise SandboxError("Execution error: WorkerNoResponse") from None
    finally:
        result_queue.close()
        result_queue.join_thread()

    status = payload.get("status")
    if status == "ok":
        return payload["result"]
    if status == "sandbox_error":
        raise SandboxError(payload.get("message", "Sandbox execution failed"))
    if status == "exec_error":
        error_type = payload.get("error_type", "UnknownError")
        raise SandboxError(f"Execution error: {error_type}") from None

    raise SandboxError("Execution error: InvalidWorkerResponse")
