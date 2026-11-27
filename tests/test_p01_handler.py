import subprocess
from pathlib import Path


def test_scoring_function():
    """Runs the JavaScript tests for the online scoring function."""
    result = subprocess.run(["node", "--test", str(Path(__file__).parent / "p01_handler.test.mjs")], capture_output=True, text=True, timeout=60)
    assert result.returncode == 0, result.stdout[-4000:] + result.stderr[-2000:]
