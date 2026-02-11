"""Tests for sandboxed code execution."""

import queue
import threading

import pytest
import pandas as pd

from src.llm.exceptions import SandboxError, SandboxTimeoutError
from src.llm.sandbox import execute_in_sandbox


class TestExecuteInSandbox:
    """Tests for sandbox execution."""

    @pytest.fixture()
    def sample_df(self):
        return pd.DataFrame(
            {
                "name": ["Alice", "Bob", "Charlie"],
                "age": [30, 25, 35],
                "salary": [50000.0, 60000.0, 70000.0],
            }
        )

    # --- Normal cases ---

    def test_simple_assignment(self, sample_df):
        """result variable simple assignment works."""
        code = "result = df['age'].mean()"
        result = execute_in_sandbox(code, sample_df)
        assert result == 30.0

    def test_pandas_operations(self, sample_df):
        """pandas operations execute correctly."""
        code = "result = df.groupby('name')['salary'].sum().to_dict()"
        result = execute_in_sandbox(code, sample_df)
        assert result == {"Alice": 50000.0, "Bob": 60000.0, "Charlie": 70000.0}

    def test_numpy_operations(self, sample_df):
        """numpy operations execute correctly."""
        code = "result = float(np.std(df['age']))"
        result = execute_in_sandbox(code, sample_df)
        assert isinstance(result, float)

    def test_builtin_functions(self, sample_df):
        """Allowed builtin functions work."""
        code = "result = len(df)"
        result = execute_in_sandbox(code, sample_df)
        assert result == 3

    def test_multiline_code(self, sample_df):
        """Multiline code executes correctly."""
        code = """
filtered = df[df['age'] > 28]
result = len(filtered)
"""
        result = execute_in_sandbox(code, sample_df)
        assert result == 2

    def test_df_is_copy(self, sample_df):
        """Passed df is a copy; original data is not modified."""
        code = "df['new_col'] = 1\nresult = list(df.columns)"
        result = execute_in_sandbox(code, sample_df)
        assert "new_col" in result
        assert "new_col" not in sample_df.columns

    # --- Security: blocked patterns ---

    def test_block_import(self, sample_df):
        """import statement is blocked."""
        code = "import os\nresult = os.listdir('.')"
        with pytest.raises(SandboxError, match="import"):
            execute_in_sandbox(code, sample_df)

    def test_block_from_import(self, sample_df):
        """from-import statement is blocked."""
        code = "from pathlib import Path\nresult = str(Path('.'))"
        with pytest.raises(SandboxError, match="import"):
            execute_in_sandbox(code, sample_df)

    def test_block_open(self, sample_df):
        """open() is blocked."""
        code = "result = open('/etc/passwd').read()"
        with pytest.raises(SandboxError, match="open"):
            execute_in_sandbox(code, sample_df)

    def test_block_exec(self, sample_df):
        """exec/eval are blocked."""
        code = "result = eval('1+1')"
        with pytest.raises(SandboxError, match="eval"):
            execute_in_sandbox(code, sample_df)

    def test_block_dunder(self, sample_df):
        """__class__, __subclasses__ etc. dunder access is blocked."""
        code = "result = df.__class__.__subclasses__()"
        with pytest.raises(SandboxError, match="__"):
            execute_in_sandbox(code, sample_df)

    def test_block_os_system(self, sample_df):
        """os.system patterns are blocked."""
        code = "import os; result = os.system('ls')"
        with pytest.raises(SandboxError):
            execute_in_sandbox(code, sample_df)

    def test_block_numpy_memmap(self, sample_df):
        """np.memmap is blocked to prevent filesystem access."""
        code = "result = np.memmap('/tmp/x.dat', dtype='float32', mode='r')"
        with pytest.raises(SandboxError, match="np.memmap"):
            execute_in_sandbox(code, sample_df)

    def test_block_numpy_open_memmap(self, sample_df):
        """np.lib.format.open_memmap is blocked."""
        code = "result = np.lib.format.open_memmap('/tmp/x.npy', mode='r')"
        with pytest.raises(SandboxError, match="open_memmap"):
            execute_in_sandbox(code, sample_df)

    # --- Timeout ---

    def test_timeout(self, sample_df):
        """Infinite loop times out."""
        code = "while True: pass\nresult = None"
        with pytest.raises(SandboxTimeoutError):
            execute_in_sandbox(code, sample_df, timeout_seconds=1)

    # --- Missing result variable ---

    def test_no_result_variable(self, sample_df):
        """Error when result variable is not defined."""
        code = "x = df['age'].mean()"
        with pytest.raises(SandboxError, match="result"):
            execute_in_sandbox(code, sample_df)

    # --- Thread safety ---

    def test_execute_from_non_main_thread(self, sample_df):
        """Sandbox execution works when called from a non-main thread."""
        result_queue: queue.Queue = queue.Queue()
        error_queue: queue.Queue = queue.Queue()

        def _runner():
            try:
                result_queue.put(execute_in_sandbox("result = int(df['age'].mean())", sample_df))
            except Exception as e:  # pragma: no cover - test asserts no exception
                error_queue.put(e)

        thread = threading.Thread(target=_runner)
        thread.start()
        thread.join(timeout=5)

        assert not thread.is_alive()
        assert error_queue.empty(), f"unexpected error: {error_queue.get()}"
        assert result_queue.get_nowait() == 30

    def test_timeout_from_non_main_thread(self, sample_df):
        """Timeout is enforced when sandbox is called from a non-main thread."""
        result_queue: queue.Queue = queue.Queue()
        error_queue: queue.Queue = queue.Queue()

        def _runner():
            try:
                result_queue.put(
                    execute_in_sandbox(
                        "while True: pass\nresult = None",
                        sample_df,
                        timeout_seconds=1,
                    )
                )
            except Exception as e:
                error_queue.put(e)

        thread = threading.Thread(target=_runner)
        thread.start()
        thread.join(timeout=5)

        assert not thread.is_alive()
        assert result_queue.empty()
        error = error_queue.get_nowait()
        assert isinstance(error, SandboxTimeoutError)
