"""Fixtures pytest partagées — isolation DB + crypto + settings.

NB compat 3.10/3.11 : `datetime.UTC` n'existe qu'à partir de 3.11. La CI
tourne en 3.11 mais la sandbox de dev est parfois 3.10 ; on backfille
`datetime.UTC = datetime.timezone.utc` avant toute collection pytest
pour éviter les ImportError au niveau des modules testés (cf. ticket
`M2-unblock-auth.md` §Journal 2026-04-22).

Réparation 2026-04-22 (T1.6, session M1) : le fichier sur disque était
tronqué (49 lignes — coupé en plein commentaire de l'isolated_settings),
ce qui empêchait toute collection pytest des suites Sprint 1 (`fixture
'client' not found`). Reconstruction de la queue + ajout du fixture
`client` manquant. Cf. daily M1-2026-04-22.md §T1.6.
"""

from __future__ import annotations

import datetime as _dt

if not hasattr(_dt, "UTC"):  # pragma: no cover — Python 3.10 backfill
    _dt.UTC = _dt.timezone.utc  # type: ignore[attr-defined]

from collections.abc import Iterator
from pathlib import Path

import pytest


@pytest.fixture
def isolated_settings(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> Iterator[Path]:
    """Isole `~/.pli/` dans un tmp_path par test.

    - db_path  → tmp_path/db.sqlite
    - attachments_dir → tmp_path/att
    - crypto.key       → tmp_path/crypto.key (créé par LocalCryptoAdapter)
    - secrets OAuth → valeurs factices
    - get_crypto()     → cache vidé après le test pour éviter la fuite entre tests
    """
    from pli.config import settings

    monkeypatch.setattr(settings, "mode", "local")
    monkeypatch.setattr(settings, "db_path", tmp_path / "db.sqlite")
    monkeypatch.setattr(settings, "attachments_dir", tmp_path / "att")
    monkeypatch.setattr(settings, "gmail_client_id", "test-client-id.apps.googleusercontent.com")
    from pydantic import SecretStr

    monkeypatch.setattr(settings, "gmail_client_secret", SecretStr("test-secret"))
    monkeypatch.setattr(settings, "gmail_redirect_uri", "http://localhost:8000/auth/gmail/callback")
    monkeypatch.setattr(settings, "app_url", "http://localhost:5173")

    from pli.db import init_db_local

    init_db_local()

    from pli import crypto

    crypto.get_crypto.cache_clear()

    yield tmp_path

    crypto.get_crypto.cache_clear()


@pytest.fixture
def client(isolated_settings: Path):  # type: ignore[no-untyped-def]
    """TestClient FastAPI sur l'app PLI, avec DB et crypto isolés."""
    from fastapi.testclient import TestClient

    from pli.main import app

    return TestClient(app, follow_redirects=False)
