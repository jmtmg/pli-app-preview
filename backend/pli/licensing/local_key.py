"""Licences hors-ligne signées Ed25519 pour PLI Plus (mode Local).

Format fichier `~/.pli/license.json` :
    {
      "payload": { ... base64-url ... },
      "sig":     "base64-url signature"
    }

Le `payload` contient :
    - user_hash    : sha256(email) tronqué à 16 octets hex — rattache la licence
                     à un compte sans stocker l'email en clair.
    - plan         : "plus_monthly" | "plus_yearly" | "plus_trial"
    - issued_at    : ISO 8601 UTC
    - expires_at   : ISO 8601 UTC (None pour lifetime)
    - version      : 1

Clé signing (Ed25519) émise côté serveur Cloud au checkout. Clé publique
embarquée dans le binaire PLI (constante `EMBEDDED_PUBLIC_KEY`).
"""

from __future__ import annotations

import base64
import hashlib
import json
from dataclasses import asdict, dataclass
from datetime import UTC, datetime
from pathlib import Path

from cryptography.exceptions import InvalidSignature
from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PrivateKey, Ed25519PublicKey

from ..config import settings

LICENSE_VERSION = 1


@dataclass(frozen=True, slots=True)
class LocalLicense:
    user_hash: str
    plan: str
    issued_at: str  # ISO 8601 UTC
    expires_at: str | None
    version: int = LICENSE_VERSION

    def is_expired(self, now: datetime | None = None) -> bool:
        if self.expires_at is None:
            return False
        now = now or datetime.now(tz=UTC)
        exp = datetime.fromisoformat(self.expires_at)
        return now >= exp


# ---------------------------------------------------------------------------
# Keypair — script scripts/generate_license_keypair.py consomme ceci
# ---------------------------------------------------------------------------


def generate_keypair() -> tuple[str, str]:
    """Retourne (private_b64, public_b64) pour stockage hors-binaire."""
    sk = Ed25519PrivateKey.generate()
    pk = sk.public_key()
    sk_bytes = sk.private_bytes_raw()
    pk_bytes = pk.public_bytes_raw()
    return (
        base64.b64encode(sk_bytes).decode("ascii"),
        base64.b64encode(pk_bytes).decode("ascii"),
    )


def _b64url(data: bytes) -> str:
    return base64.urlsafe_b64encode(data).decode("ascii").rstrip("=")


def _b64url_decode(s: str) -> bytes:
    pad = "=" * (-len(s) % 4)
    return base64.urlsafe_b64decode(s + pad)


def user_hash_for(email: str) -> str:
    return hashlib.sha256(email.lower().strip().encode("utf-8")).hexdigest()[:32]


# ---------------------------------------------------------------------------
# Emission (côté serveur Cloud — endpoint /licenses/issue)
# ---------------------------------------------------------------------------


def issue_local_license(
    *,
    email: str,
    plan: str,
    valid_until: datetime | None,
    signing_key_b64: str,
) -> dict:
    """Émet une licence signée. Retourne le dict {payload, sig} à renvoyer au client."""
    payload = LocalLicense(
        user_hash=user_hash_for(email),
        plan=plan,
        issued_at=datetime.now(tz=UTC).isoformat(),
        expires_at=valid_until.astimezone(UTC).isoformat() if valid_until else None,
    )
    payload_bytes = json.dumps(asdict(payload), separators=(",", ":"), sort_keys=True).encode(
        "utf-8"
    )
    sk = Ed25519PrivateKey.from_private_bytes(base64.b64decode(signing_key_b64))
    sig = sk.sign(payload_bytes)
    return {
        "payload": _b64url(payload_bytes),
        "sig": _b64url(sig),
    }


# ---------------------------------------------------------------------------
# Verification (côté client — démarrage appli Local)
# ---------------------------------------------------------------------------


def verify_license(
    license_blob: dict,
    *,
    public_key_b64: str,
    expected_email: str | None = None,
) -> LocalLicense:
    """Décode + vérifie la signature + renvoie la licence.

    Lève ValueError pour toute anomalie (signature invalide, email mismatch,
    version inconnue). L'appelant gère l'expiration séparément.
    """
    try:
        payload_bytes = _b64url_decode(license_blob["payload"])
        sig = _b64url_decode(license_blob["sig"])
    except (KeyError, ValueError) as exc:
        raise ValueError("Licence illisible") from exc

    pk = Ed25519PublicKey.from_public_bytes(base64.b64decode(public_key_b64))
    try:
        pk.verify(sig, payload_bytes)
    except InvalidSignature as exc:
        raise ValueError("Signature de licence invalide") from exc

    try:
        data = json.loads(payload_bytes.decode("utf-8"))
        lic = LocalLicense(**data)
    except Exception as exc:
        raise ValueError("Payload de licence invalide") from exc

    if lic.version != LICENSE_VERSION:
        raise ValueError(f"Version de licence inconnue : {lic.version}")

    if expected_email and lic.user_hash != user_hash_for(expected_email):
        raise ValueError("Licence émise pour une autre adresse email")

    return lic


# ---------------------------------------------------------------------------
# Persistence (client Local)
# ---------------------------------------------------------------------------


def license_path() -> Path:
    return settings.db_path.parent / "license.json"


def save_license(license_blob: dict) -> Path:
    path = license_path()
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(license_blob), encoding="utf-8")
    path.chmod(0o600)
    return path


def load_license() -> dict | None:
    path = license_path()
    if not path.exists():
        return None
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except Exception:
        return None
