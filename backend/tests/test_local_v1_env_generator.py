"""Local-v1 runtime env generator guardrails."""

from __future__ import annotations

import importlib.util
import json
import stat
from pathlib import Path


def _load_generator():
    repo_root = Path(__file__).resolve().parents[2]
    script_path = repo_root / "scripts" / "generate_local_v1_env.py"
    assert script_path.exists(), "local-v1 env generator script is missing"
    spec = importlib.util.spec_from_file_location("generate_local_v1_env", script_path)
    assert spec and spec.loader
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def test_build_env_uses_local_v1_paths_and_no_demo_defaults(tmp_path: Path) -> None:
    module = _load_generator()

    env = module.build_env(tmp_path, secret_key="s" * 48, sqlcipher_key="")

    assert env["PLI_MODE"] == "local"
    assert env["PLI_DEBUG"] == "false"
    assert env["PLI_DEMO"] == "false"
    assert env["PLI_DB_PATH"] == str(tmp_path / ".pli-local-v1" / "db.sqlite")
    assert env["PLI_ATTACHMENTS_DIR"] == str(tmp_path / ".pli-local-v1" / "attachments")
    assert env["PLI_BASE_URL"] == "http://localhost:8000"
    assert env["PLI_APP_URL"] == "http://localhost:5173"
    assert json.loads(env["PLI_CORS_ORIGINS"]) == ["http://localhost:5173"]


def test_write_local_v1_env_is_secret_safe_and_private(tmp_path: Path) -> None:
    module = _load_generator()

    env_path = module.write_local_v1_env(tmp_path, secret_key="s" * 48, sqlcipher_key="")

    text = env_path.read_text(encoding="utf-8")
    mode = stat.S_IMODE(env_path.stat().st_mode)
    assert mode == 0o600
    assert "PLI_SECRET_KEY=" in text
    assert "PLI_DEBUG=false" in text
    assert "PLI_DEMO=false" in text
    assert str(tmp_path / ".pli-local-v1" / "db.sqlite") in text
    assert (tmp_path / ".pli-local-v1" / "attachments").is_dir()
    assert "sk_test_" not in text
    assert "minioadmin" not in text
