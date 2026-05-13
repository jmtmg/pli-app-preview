"""Tests US-1.9 — /health complet + middleware de logs HTTP."""

from __future__ import annotations

import re

import pytest

# Supprime les codes ANSI de coloration pour que les assertions ne soient pas
# fragiles vis-a-vis du renderer console pretty.
_ANSI_RE = re.compile(r"\x1b\[[0-9;]*m")


def _clean(s: str) -> str:
    return _ANSI_RE.sub("", s)


def test_health_returns_ok_structure(client, isolated_settings):  # type: ignore[no-untyped-def]
    r = client.get("/health")
    assert r.status_code == 200
    data = r.json()
    assert data["status"] == "ok"
    assert "version" in data
    assert data["mode"] == "local"
    assert data["db"]["ok"] is True
    # Pas de comptes seed → 0 actifs
    assert data["accounts"]["active"] == 0
    assert data["accounts"]["last_sync_at"] is None
    assert isinstance(data["latency_ms"], (int, float))


def test_health_reports_connected_accounts(client, isolated_settings):  # type: ignore[no-untyped-def]
    from pli.db import get_conn

    with get_conn() as conn:
        conn.execute(
            "INSERT INTO accounts (id, provider, email, is_active, last_sync_at) "
            "VALUES ('a1', 'gmail', 'x@y.z', 1, 1000)"
        )
        conn.execute(
            "INSERT INTO accounts (id, provider, email, is_active) "
            "VALUES ('a2', 'gmail', 'x2@y.z', 0)"  # desactive → non compte
        )
        conn.commit()
    r = client.get("/health").json()
    assert r["accounts"]["active"] == 1
    assert r["accounts"]["last_sync_at"] == 1000


def test_root_returns_version(client, isolated_settings):  # type: ignore[no-untyped-def]
    r = client.get("/").json()
    assert r["name"] == "PLI"
    assert "version" in r
    assert r["mode"] == "local"


@pytest.mark.asyncio
async def test_cloud_lifespan_initializes_and_closes_pg_pool(monkeypatch):  # type: ignore[no-untyped-def]
    from pli import main
    from pli.config import settings

    calls: list[str] = []

    async def fake_init_cloud() -> None:
        calls.append("init_cloud")

    async def fake_close_cloud() -> None:
        calls.append("close_cloud")

    monkeypatch.setattr(settings, "mode", "cloud")
    monkeypatch.setattr(main, "init_db", lambda: calls.append("init_dispatch"))
    monkeypatch.setattr(main, "init_db_cloud", fake_init_cloud)
    monkeypatch.setattr(main, "close_db_cloud", fake_close_cloud)

    async with main.lifespan(main.app):
        calls.append("running")

    assert calls == ["init_dispatch", "init_cloud", "running", "close_cloud"]


# --------------------------------------------------------------------------
# Middleware request logging
# --------------------------------------------------------------------------


def test_request_middleware_generates_request_id_when_absent(client, isolated_settings, capsys):  # type: ignore[no-untyped-def]
    """Sans X-Request-Id, le middleware en genere un et le logge."""
    client.get("/")
    out = _clean(capsys.readouterr().out)
    assert "request_id=" in out
    assert "http_request" in out


def test_request_middleware_honors_explicit_request_id(client, isolated_settings, capsys):  # type: ignore[no-untyped-def]
    """X-Request-Id fourni → reutilise comme correlation id."""
    client.get("/", headers={"X-Request-Id": "test-corr-123"})
    out = _clean(capsys.readouterr().out)
    assert "test-corr-123" in out


def test_request_middleware_logs_status_and_duration(client, isolated_settings, capsys):  # type: ignore[no-untyped-def]
    client.get("/health")
    out = _clean(capsys.readouterr().out)
    assert "status=200" in out
    assert "duration_ms=" in out


def test_request_middleware_uses_warning_for_4xx(client, isolated_settings, capsys):  # type: ignore[no-untyped-def]
    client.get("/this-route-does-not-exist")
    out = _clean(capsys.readouterr().out).lower()
    assert "status=404" in out
    assert "warning" in out
