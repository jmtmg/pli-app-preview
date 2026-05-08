#!/usr/bin/env python3
"""
Agrège les 3 sorties JSON (pip-audit, npm audit, trivy) en un SUMMARY.md
lisible direction, avec exit 1 si Critical ou High > 0.

Invoqué par run-vuln-scans.sh. Séparé dans son propre fichier pour être
testable isolément (tests/scripts/test_summarize_scans.py).
"""

from __future__ import annotations

import argparse
import json
import sys
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any


@dataclass
class ScanResult:
    tool: str
    critical: int = 0
    high: int = 0
    medium: int = 0
    low: int = 0
    # (cve_id, package, severity, fixed_version)
    findings: list[tuple[str, str, str, str]] = field(default_factory=list)


def _severity_bucket(raw: str) -> str:
    s = (raw or "").lower()
    if s in ("critical",):
        return "critical"
    if s in ("high",):
        return "high"
    if s in ("medium", "moderate"):
        return "medium"
    return "low"


def parse_pip_audit(path: Path) -> ScanResult:
    r = ScanResult(tool="pip-audit")
    if not path.exists() or path.stat().st_size == 0:
        return r
    data = json.loads(path.read_text())
    # pip-audit JSON schema : { "dependencies": [ { "name", "version", "vulns":[...] } ] }
    for dep in data.get("dependencies", []):
        for vuln in dep.get("vulns", []):
            # pip-audit n'expose pas toujours severity — on déduit via ID si possible.
            sev = _severity_bucket(vuln.get("severity", "") or "medium")
            setattr(r, sev, getattr(r, sev) + 1)
            r.findings.append(
                (
                    vuln.get("id", "?"),
                    f"{dep.get('name')}@{dep.get('version')}",
                    sev,
                    ",".join(vuln.get("fix_versions", [])) or "n/a",
                )
            )
    return r


def parse_npm_audit(path: Path) -> ScanResult:
    r = ScanResult(tool="npm-audit")
    if not path.exists() or path.stat().st_size == 0:
        return r
    try:
        data = json.loads(path.read_text())
    except json.JSONDecodeError:
        # npm audit écrit parfois du texte stdout+JSON collé — on skip propre.
        return r
    # npm audit v7+ : { "vulnerabilities": { "<pkg>": { "severity", "via": [...], "fixAvailable" } } }
    for pkg, v in (data.get("vulnerabilities") or {}).items():
        sev = _severity_bucket(v.get("severity", "low"))
        setattr(r, sev, getattr(r, sev) + 1)
        fix = v.get("fixAvailable")
        fix_str = fix.get("version") if isinstance(fix, dict) else ("yes" if fix else "no")
        r.findings.append((v.get("url", "?"), pkg, sev, fix_str))
    return r


def parse_trivy(path: Path) -> ScanResult:
    r = ScanResult(tool="trivy")
    if not path.exists() or path.stat().st_size == 0:
        return r
    data = json.loads(path.read_text())
    # trivy JSON : { "Results": [ { "Vulnerabilities": [ { "VulnerabilityID", "PkgName", ... } ] } ] }
    for result in data.get("Results", []) or []:
        for v in result.get("Vulnerabilities", []) or []:
            sev = _severity_bucket(v.get("Severity", "low"))
            setattr(r, sev, getattr(r, sev) + 1)
            r.findings.append(
                (
                    v.get("VulnerabilityID", "?"),
                    f"{v.get('PkgName')}@{v.get('InstalledVersion')}",
                    sev,
                    v.get("FixedVersion", "n/a"),
                )
            )
    return r


def render(results: list[ScanResult]) -> str:
    critical = sum(r.critical for r in results)
    high = sum(r.high for r in results)
    medium = sum(r.medium for r in results)
    low = sum(r.low for r in results)

    gate = "PASS" if critical == 0 and high == 0 else "FAIL"
    status_line = f"**Gate direction (0 Critical / 0 High) : {gate}**"

    lines = [
        "# Scan vulns — Re-baseline M3",
        "",
        status_line,
        "",
        f"- Critical : {critical}",
        f"- High     : {high}",
        f"- Medium   : {medium}",
        f"- Low      : {low}",
        "",
        "## Détail par outil",
        "",
    ]
    for r in results:
        lines.append(f"### {r.tool}")
        lines.append("")
        lines.append(
            f"Critical={r.critical} · High={r.high} · Medium={r.medium} · Low={r.low}",
        )
        lines.append("")
        if r.findings:
            lines.append("| ID | Package | Severity | Fix |")
            lines.append("|---|---|---|---|")
            # Afficher en priorité Critical + High (les Medium/Low sont dans les rapports bruts).
            prio = [f for f in r.findings if f[2] in ("critical", "high")]
            for cve, pkg, sev, fix in prio[:50]:
                lines.append(f"| {cve} | {pkg} | {sev} | {fix} |")
            if len(prio) > 50:
                lines.append(f"| … | { len(prio) - 50 } autres | | |")
        else:
            lines.append("_Aucun finding._")
        lines.append("")
    return "\n".join(lines)


def main(argv: list[str] | None = None) -> int:
    p = argparse.ArgumentParser()
    p.add_argument("--pip-audit", type=Path, required=True)
    p.add_argument("--npm-audit", type=Path, required=True)
    p.add_argument("--trivy", type=Path, required=True)
    p.add_argument("--output", type=Path, required=True)
    args = p.parse_args(argv)

    results = [
        parse_pip_audit(args.pip_audit),
        parse_npm_audit(args.npm_audit),
        parse_trivy(args.trivy),
    ]
    args.output.write_text(render(results))

    critical = sum(r.critical for r in results)
    high = sum(r.high for r in results)
    return 0 if (critical + high) == 0 else 1


if __name__ == "__main__":
    sys.exit(main())
