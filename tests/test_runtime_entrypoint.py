import os
import subprocess
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]


def test_keyless_root_module_reports_configuration_error() -> None:
    environment = os.environ.copy()
    environment.pop("OPENAI_API_KEY", None)
    environment.pop("OPENAI_MODEL", None)

    result = subprocess.run(
        ["uv", "run", "--offline", "python", "-m", "async_lcel_question_chain"],
        cwd=PROJECT_ROOT,
        env=environment,
        capture_output=True,
        text=True,
        check=False,
    )

    assert result.returncode != 0
    assert "RuntimeConfigurationError" in result.stderr
    assert "OPENAI_API_KEY must be configured" in result.stderr
    assert "ModuleNotFoundError" not in result.stderr
