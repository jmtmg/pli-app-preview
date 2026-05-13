#!/usr/bin/env python3
"""Secret-safe PLI production readiness check.

Usage:
  python scripts/prod_readiness_check.py --target cloud-v1 --env production
  python scripts/prod_readiness_check.py --target local-v1 --env staging --json
"""

from __future__ import annotations

import argparse
import json
import os
import sys
from dataclasses import asdict
from pathlib import Path
from typing import Any

# Allow running from a source checkout without installing first.
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from pli.prod_readiness import evaluate_prod_readiness, redact_env_keys  # noqa: E402


def _load_dotenv(path: Path) -> dict[str, str]:
    values: dict[str, str] = {}
    if not path.exists():
        return values
    for raw in path.read_text(encoding="utf-8").splitlines():
        line = raw.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, value = line.split("=", 1)
        values[key.strip()] = value.strip().strip('"').strip("'")
    return values


def _report_to_dict(report: Any) -> dict[str, Any]:
    return {
        "target": report.target,
        "deploy_env": report.deploy_env,
        "status": report.status.value,
        "blockers": [asdict(f) for f in report.blockers],
        "warnings": [asdict(f) for f in report.warnings],
        "findings": [asdict(f) for f in report.findings],
    }


def main() -> int:
    parser = argparse.ArgumentParser(description="PLI production readiness check")
    parser.add_argument("--target", choices=["local-v1", "cloud-v1"], default="cloud-v1")
    parser.add_argument("--env", choices=["staging", "production"], default="production")
    parser.add_argument("--dotenv", type=Path, default=None, help="Optional .env file to read")
    parser.add_argument("--json", action="store_true", help="Emit JSON")
    parser.add_argument("--show-env-keys", action="store_true", help="Show PLI_* keys with secrets redacted")
    args = parser.parse_args()

    merged = dict(os.environ)
    if args.dotenv:
        merged.update(_load_dotenv(args.dotenv))

    report = evaluate_prod_readiness(merged, target=args.target, deploy_env=args.env)
    payload = _report_to_dict(report)
    if args.show_env_keys:
        payload["env_keys"] = redact_env_keys(merged)

    if args.json:
        print(json.dumps(payload, ensure_ascii=False, indent=2))
    else:
        print(f"PLI prod readiness — target={args.target} env={args.env} status={report.status.value}")
        if report.findings:
            for finding in report.findings:
                print(f"- [{finding.severity}] {finding.code}: {finding.message}")
                print(f"  action: {finding.action}")
        else:
            print("- [info] no-findings: aucun blocage détecté par le check statique.")
        if args.show_env_keys:
            print("\nPLI_* keys (secret-safe):")
            for key, value in payload["env_keys"].items():
                print(f"- {key}={value}")

    return 0 if report.status.value == "ready" else 2


if __name__ == "__main__":
    raise SystemExit(main())
