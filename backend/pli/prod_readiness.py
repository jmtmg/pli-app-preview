"""Production readiness checks for PLI.

The checks are intentionally secret-safe: they validate presence, shape and
obvious dummy/default values, but never expose the value of any credential.
"""

from __future__ import annotations

import base64
import ipaddress
import json
import socket
from collections.abc import Mapping
from dataclasses import dataclass
from enum import StrEnum
from typing import Literal
from urllib.parse import urlparse

Severity = Literal["blocker", "warning", "info"]
Target = Literal["local-v1", "cloud-v1"]
DeployEnv = Literal["staging", "production"]

_SECRET_KEYS = (
    "SECRET",
    "TOKEN",
    "PASSWORD",
    "DATABASE_URL",
    "PRIVATE",
    "KEY",
    "DSN",
)

_DUMMY_MARKERS = (
    "change-me",
    "changeme",
    "dev-only",
    "dummy",
    "example",
    "test_dummy",
    "***",
    "minioadmin",
)

_LOCAL_HOSTS = {"localhost", "127.0.0.1", "0.0.0.0", "::1"}


class Status(StrEnum):
    READY = "ready"
    BLOCKED = "blocked"


@dataclass(frozen=True)
class Finding:
    severity: Severity
    code: str
    message: str
    action: str


@dataclass(frozen=True)
class ReadinessReport:
    target: Target
    deploy_env: DeployEnv
    status: Status
    findings: tuple[Finding, ...]

    @property
    def blockers(self) -> tuple[Finding, ...]:
        return tuple(f for f in self.findings if f.severity == "blocker")

    @property
    def warnings(self) -> tuple[Finding, ...]:
        return tuple(f for f in self.findings if f.severity == "warning")


def _env_bool(raw: str | None) -> bool:
    return (raw or "").strip().lower() in {"1", "true", "yes", "on"}


def _get(env: Mapping[str, str], key: str) -> str:
    return (env.get(key) or "").strip()


def _is_dummy(value: str) -> bool:
    low = value.strip().lower()
    return not low or any(marker in low for marker in _DUMMY_MARKERS)


def _has_good_secret(env: Mapping[str, str], key: str, *, min_len: int = 24) -> bool:
    value = _get(env, key)
    return len(value) >= min_len and not _is_dummy(value)


def _is_legacy_ipv4_literal(value: str) -> bool:
    if not value or not value[0].isdigit():
        return False
    if any(char not in "0123456789abcdefABCDEFxX." for char in value):
        return False
    try:
        socket.inet_aton(value)
    except OSError:
        return False
    return True


def _host_is_non_public(value: str) -> bool:
    parsed = urlparse(value if "://" in value else f"//{value}")
    host = (parsed.hostname or "").lower().rstrip(".")
    if not host:
        return True
    if host == "*" or host.startswith("*.") or host in _LOCAL_HOSTS or host.endswith(".local"):
        return True
    if "." not in host or host.endswith((".internal", ".lan", ".home", ".localhost")):
        return True
    try:
        address = ipaddress.ip_address(host)
    except ValueError:
        return _is_legacy_ipv4_literal(host)
    return not address.is_global


def _is_public_https_url(value: str) -> bool:
    parsed = urlparse(value)
    return parsed.scheme == "https" and bool(parsed.netloc) and not _host_is_non_public(value)


def _is_fernet_key(value: str) -> bool:
    try:
        decoded = base64.urlsafe_b64decode(value.encode("ascii"))
    except (ValueError, UnicodeEncodeError):
        return False
    return len(value) == 44 and len(decoded) == 32


def _json_string_list(value: str) -> list[str] | None:
    try:
        parsed = json.loads(value)
    except json.JSONDecodeError:
        return None
    if isinstance(parsed, list) and parsed and all(isinstance(item, str) and item for item in parsed):
        return parsed
    return None


def _has_only_public_https_origins(value: str) -> bool:
    origins = _json_string_list(value)
    return origins is not None and all(origin != "*" and _is_public_https_url(origin) for origin in origins)


def _host_is_local(value: str) -> bool:
    parsed = urlparse(value if "://" in value else f"//{value}")
    host = (parsed.hostname or "").lower()
    return host in _LOCAL_HOSTS or host.endswith(".local")


def _add_if(
    findings: list[Finding],
    condition: bool,
    *,
    severity: Severity,
    code: str,
    message: str,
    action: str,
) -> None:
    if condition:
        findings.append(Finding(severity=severity, code=code, message=message, action=action))


def _check_common(env: Mapping[str, str], findings: list[Finding], *, deploy_env: DeployEnv) -> None:
    _add_if(
        findings,
        _env_bool(_get(env, "PLI_DEBUG")),
        severity="blocker",
        code="debug-enabled",
        message="PLI_DEBUG est actif.",
        action="Mettre PLI_DEBUG=false pour tout environnement prod/staging exposé.",
    )
    _add_if(
        findings,
        _env_bool(_get(env, "PLI_DEMO")),
        severity="blocker",
        code="demo-enabled",
        message="PLI_DEMO est actif.",
        action="Mettre PLI_DEMO=false avant tout déploiement exposé.",
    )
    _add_if(
        findings,
        not _has_good_secret(env, "PLI_SECRET_KEY", min_len=32),
        severity="blocker",
        code="secret-key-missing-or-default",
        message="PLI_SECRET_KEY est absent, trop court, ou ressemble à une valeur de démonstration.",
        action="Générer une vraie valeur via `openssl rand -base64 64` et la stocker dans le gestionnaire de secrets.",
    )


def _check_local_v1(env: Mapping[str, str], findings: list[Finding]) -> None:
    _add_if(
        findings,
        _get(env, "PLI_MODE") != "local",
        severity="blocker",
        code="local-mode-required",
        message="La cible local-v1 exige PLI_MODE=local.",
        action="Utiliser PLI_MODE=local pour la release locale v1, ou choisir la cible cloud-v1.",
    )
    _add_if(
        findings,
        not _get(env, "PLI_DB_PATH"),
        severity="blocker",
        code="local-db-path-missing",
        message="PLI_DB_PATH est absent.",
        action="Définir un chemin de base SQLite dédié à la release locale.",
    )
    _add_if(
        findings,
        not _get(env, "PLI_ATTACHMENTS_DIR"),
        severity="blocker",
        code="attachments-dir-missing",
        message="PLI_ATTACHMENTS_DIR est absent.",
        action="Définir un répertoire de stockage des pièces jointes locales.",
    )
    _add_if(
        findings,
        not _get(env, "PLI_SQLCIPHER_KEY"),
        severity="warning",
        code="sqlcipher-key-missing",
        message="PLI_SQLCIPHER_KEY est absent.",
        action="Ajouter SQLCipher/pysqlcipher3 et une clé locale si la release doit stocker des emails réels.",
    )


def _check_cloud_v1(env: Mapping[str, str], findings: list[Finding], *, deploy_env: DeployEnv) -> None:
    base_url = _get(env, "PLI_BASE_URL")
    app_url = _get(env, "PLI_APP_URL")
    _add_if(
        findings,
        not _is_public_https_url(base_url),
        severity="blocker",
        code="base-url-not-https",
        message="PLI_BASE_URL n'est pas une URL publique HTTPS pour un cloud staging/prod exposé.",
        action="Configurer l'URL publique HTTPS de l'API, sans localhost ni IP privée.",
    )
    _add_if(
        findings,
        not _is_public_https_url(app_url),
        severity="blocker",
        code="app-url-not-https",
        message="PLI_APP_URL n'est pas une URL publique HTTPS pour un cloud staging/prod exposé.",
        action="Configurer l'origine publique HTTPS du frontend, sans localhost ni IP privée.",
    )
    _add_if(
        findings,
        _get(env, "PLI_MODE") != "cloud",
        severity="blocker",
        code="cloud-mode-required",
        message="La cible cloud-v1 exige PLI_MODE=cloud.",
        action="Définir PLI_MODE=cloud dans l'environnement de staging/prod.",
    )
    _add_if(
        findings,
        not _has_good_secret(env, "PLI_DATABASE_URL", min_len=18),
        severity="blocker",
        code="database-url-missing-or-dummy",
        message="PLI_DATABASE_URL est absent ou ressemble à une valeur factice.",
        action="Fournir une URL PostgreSQL réelle via le gestionnaire de secrets, sans l'imprimer.",
    )
    _add_if(
        findings,
        _host_is_local(_get(env, "PLI_DATABASE_URL")) and deploy_env == "production",
        severity="blocker",
        code="database-url-localhost",
        message="PLI_DATABASE_URL pointe vers localhost en production.",
        action="Utiliser un PostgreSQL managé/interne non-localhost pour la production.",
    )
    _add_if(
        findings,
        not _has_good_secret(env, "PLI_CLOUD_CRYPTO_KEY", min_len=32)
        or not _is_fernet_key(_get(env, "PLI_CLOUD_CRYPTO_KEY")),
        severity="blocker",
        code="cloud-crypto-key-missing",
        message="PLI_CLOUD_CRYPTO_KEY est absent, factice, ou n'est pas une clé Fernet valide.",
        action="Générer une clé Fernet et la stocker dans le gestionnaire de secrets.",
    )

    for key in ("PLI_S3_ENDPOINT_URL", "PLI_S3_ACCESS_KEY", "PLI_S3_SECRET_KEY", "PLI_S3_BUCKET"):
        _add_if(
            findings,
            not _has_good_secret(env, key, min_len=8),
            severity="blocker",
            code=f"{key.lower()}-missing-or-dummy",
            message=f"{key} est absent ou ressemble à une valeur de développement.",
            action=f"Configurer {key} via le gestionnaire de secrets / stockage objet de staging-prod.",
        )
    _add_if(
        findings,
        bool(_get(env, "PLI_S3_ENDPOINT_URL")) and not _is_public_https_url(_get(env, "PLI_S3_ENDPOINT_URL")),
        severity="blocker",
        code="s3-endpoint-not-public-https",
        message="PLI_S3_ENDPOINT_URL n'est pas un endpoint objet public HTTPS.",
        action="Utiliser l'endpoint HTTPS officiel du fournisseur S3-compatible ; garder MinIO/local pour une cible smoke locale séparée.",
    )

    cors = _get(env, "PLI_CORS_ORIGINS")
    _add_if(
        findings,
        not _has_only_public_https_origins(cors),
        severity="blocker",
        code="cors-origins-unsafe",
        message="PLI_CORS_ORIGINS est absent, wildcard, local/non-HTTPS, ou n'est pas une JSON list.",
        action="Limiter CORS aux origines HTTPS exactes du frontend, au format JSON list.",
    )

    email_provider = _get(env, "PLI_EMAIL_PROVIDER") or "memory"
    _add_if(
        findings,
        email_provider == "memory",
        severity="blocker",
        code="email-provider-memory",
        message="PLI_EMAIL_PROVIDER=memory n'envoie pas d'emails réels.",
        action="Configurer smtp, sendgrid ou postmark pour staging/prod.",
    )
    if email_provider in {"sendgrid", "postmark"}:
        _add_if(
            findings,
            not _has_good_secret(env, "PLI_EMAIL_API_KEY", min_len=16),
            severity="blocker",
            code="email-api-key-missing",
            message="La clé API email est absente ou factice.",
            action="Stocker la clé email dans le gestionnaire de secrets.",
        )
    if email_provider == "smtp":
        _add_if(
            findings,
            not _get(env, "PLI_EMAIL_SMTP_HOST") or _host_is_local(_get(env, "PLI_EMAIL_SMTP_HOST")),
            severity="blocker",
            code="smtp-host-local-or-missing",
            message="Le serveur SMTP est absent ou local.",
            action="Configurer un SMTP réel ou transactionnel.",
        )

    oauth_pairs = (
        ("gmail", "PLI_GMAIL_CLIENT_ID", "PLI_GMAIL_CLIENT_SECRET", "PLI_GMAIL_REDIRECT_URI"),
        ("microsoft", "PLI_MS_CLIENT_ID", "PLI_MS_CLIENT_SECRET", "PLI_MS_REDIRECT_URI"),
    )
    for provider, client_id, client_secret, redirect_uri in oauth_pairs:
        _add_if(
            findings,
            not _get(env, client_id) or not _has_good_secret(env, client_secret, min_len=16),
            severity="blocker",
            code=f"{provider}-oauth-missing",
            message=f"Configuration OAuth {provider} incomplète.",
            action=f"Créer l'app OAuth officielle {provider} et stocker client_id/client_secret via secrets.",
        )
        _add_if(
            findings,
            not _is_public_https_url(_get(env, redirect_uri)),
            severity="blocker",
            code=f"{provider}-redirect-not-https",
            message=f"Redirect URI OAuth {provider} non publique HTTPS en cloud staging/prod.",
            action=f"Configurer une redirect URI publique HTTPS officielle pour {provider}.",
        )

    if _env_bool(_get(env, "PLI_ENABLE_M2")):
        stripe_secret = _get(env, "PLI_STRIPE_SECRET_KEY")
        _add_if(
            findings,
            not _has_good_secret(env, "PLI_STRIPE_SECRET_KEY", min_len=16)
            or (deploy_env == "production" and stripe_secret.startswith("sk_test_")),
            severity="blocker",
            code="stripe-secret-not-live",
            message="Stripe est activé mais la clé est absente/factice/test en production.",
            action="Configurer la clé Stripe live uniquement via secrets, ou désactiver PLI_ENABLE_M2.",
        )
        for key in ("PLI_STRIPE_WEBHOOK_SECRET", "PLI_STRIPE_PRICE_MONTHLY", "PLI_STRIPE_PRICE_YEARLY"):
            _add_if(
                findings,
                not _has_good_secret(env, key, min_len=10),
                severity="blocker",
                code=f"{key.lower()}-missing",
                message=f"{key} est absent ou factice alors que M2/Stripe est activé.",
                action=f"Configurer {key} via secrets Stripe officiels.",
            )
    else:
        findings.append(
            Finding(
                severity="info",
                code="m2-disabled",
                message="PLI_ENABLE_M2 est désactivé : billing/auth cloud avancés ne seront pas exposés.",
                action="Correct pour une prod local-v1/API MVP ; à activer seulement après migration M2-M4 validée.",
            )
        )


def evaluate_prod_readiness(
    env: Mapping[str, str],
    *,
    target: Target = "cloud-v1",
    deploy_env: DeployEnv = "production",
) -> ReadinessReport:
    findings: list[Finding] = []
    _check_common(env, findings, deploy_env=deploy_env)
    if target == "local-v1":
        _check_local_v1(env, findings)
    else:
        _check_cloud_v1(env, findings, deploy_env=deploy_env)

    status = Status.BLOCKED if any(f.severity == "blocker" for f in findings) else Status.READY
    return ReadinessReport(
        target=target,
        deploy_env=deploy_env,
        status=status,
        findings=tuple(findings),
    )


def redact_env_keys(env: Mapping[str, str]) -> dict[str, str]:
    """Return secret-safe key presence metadata for diagnostics."""
    safe: dict[str, str] = {}
    for key, value in sorted(env.items()):
        if not key.startswith("PLI_"):
            continue
        if any(marker in key.upper() for marker in _SECRET_KEYS):
            safe[key] = "[SET]" if value else "[EMPTY]"
        else:
            safe[key] = value
    return safe
