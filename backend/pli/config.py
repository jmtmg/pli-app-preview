"""Configuration PLI - pilotee par environnement (M2).

Mode de deploiement :
    PLI_MODE=local   -> SQLite dans ~/.pli/, FastAPI sur 127.0.0.1:RANDOM
    PLI_MODE=cloud   -> PostgreSQL, FastAPI derriere LB, JWT, Stripe
"""

from __future__ import annotations

from pathlib import Path
from typing import Literal

from pydantic import Field, SecretStr
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_prefix="PLI_",
        env_file=".env",
        extra="ignore",
        case_sensitive=False,
    )

    # Mode
    mode: Literal["local", "cloud"] = "local"
    debug: bool = False
    secret_key: SecretStr = Field(default=SecretStr("change-me-dev-only"))

    # DB
    db_path: Path = Field(default_factory=lambda: Path.home() / ".pli" / "db.sqlite")
    database_url: str | None = None
    sqlcipher_key: SecretStr | None = None

    # Attachments (local)
    attachments_dir: Path = Field(default_factory=lambda: Path.home() / ".pli" / "att")

    # Cloud storage S3-compatible (cloud only)
    s3_endpoint_url: str | None = None
    s3_access_key: SecretStr | None = None
    s3_secret_key: SecretStr | None = None
    s3_bucket: str | None = None
    s3_region: str = "eu-west-3"

    # Crypto at rest (cloud)
    cloud_crypto_key: SecretStr | None = None

    # API server
    host: str = "127.0.0.1"
    port: int = 0
    base_url: str = "http://localhost:8000"
    app_url: str = "http://localhost:5173"

    # CORS (cloud only)
    cors_origins: list[str] = ["http://localhost:5173"]

    # Providers - Gmail
    gmail_client_id: str = ""
    gmail_client_secret: SecretStr = SecretStr("")
    gmail_redirect_uri: str = "http://localhost:8000/auth/gmail/callback"

    # Providers - Microsoft
    ms_client_id: str = ""
    ms_client_secret: SecretStr = SecretStr("")
    ms_redirect_uri: str = "http://localhost:8000/auth/microsoft/callback"
    ms_tenant_id: str = "common"

    # Sync
    initial_sync_days: int = 30
    incremental_sync_interval_s: int = 60
    sync_max_retries: int = 4

    # Stripe (cloud only)
    stripe_secret_key: SecretStr | None = None
    stripe_webhook_secret: SecretStr | None = None
    stripe_price_monthly: str = ""
    stripe_price_yearly: str = ""
    stripe_trial_days: int = 14

    # Emails
    email_provider: Literal["memory", "smtp", "sendgrid", "postmark"] = "memory"
    email_api_key: SecretStr | None = None
    email_from: str = "noreply@pli.app"
    email_smtp_host: str = "localhost"
    email_smtp_port: int = 1025
    email_smtp_user: str | None = None
    email_smtp_password: SecretStr | None = None

    # Licences (PLI Plus Local)
    license_signing_key: SecretStr | None = None

    # Telemetry
    sentry_dsn: str | None = None

    # Feature flags (cf. ADR 0007 - kill-switch rollout M2)
    # PLI_ENABLE_M2=1|true|yes -> monte billing/auth_pli/licensing/tenancy
    enable_m2: bool = False

    def ensure_dirs(self) -> None:
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        self.attachments_dir.mkdir(parents=True, exist_ok=True)


settings = Settings()
