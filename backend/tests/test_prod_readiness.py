"""Production readiness guardrails for secret-safe PLI deploy preflight."""

from __future__ import annotations

from pli.prod_readiness import Status, evaluate_prod_readiness, redact_env_keys

_VALID_TEST_FERNET_KEY = "MDAwMDAwMDAwMDAwMDAwMDAwMDAwMDAwMDAwMDAwMDA="


def _base_env(**overrides: str) -> dict[str, str]:
    env = {
        "PLI_MODE": "cloud",
        "PLI_DEBUG": "false",
        "PLI_DEMO": "false",
        "PLI_SECRET_KEY": "s" * 48,
        "PLI_BASE_URL": "https://api.pli.example.com",
        "PLI_APP_URL": "https://app.pli.example.com",
        "PLI_DATABASE_URL": "postgresql://pli_user:strong_password@db.pli.internal:5432/pli",
        "PLI_CLOUD_CRYPTO_KEY": _VALID_TEST_FERNET_KEY,
        "PLI_S3_ENDPOINT_URL": "https://s3.eu-west-3.pli-prod.net",
        "PLI_S3_ACCESS_KEY": "access-key-prod",
        "PLI_S3_SECRET_KEY": "s3-secret-prod-value",
        "PLI_S3_BUCKET": "pli-prod",
        "PLI_CORS_ORIGINS": '["https://app.pli.example.com"]',
        "PLI_EMAIL_PROVIDER": "smtp",
        "PLI_EMAIL_SMTP_HOST": "smtp.transactional.example.com",
        "PLI_GMAIL_CLIENT_ID": "gmail-client-id.apps.googleusercontent.com",
        "PLI_GMAIL_CLIENT_SECRET": "gmail-client-secret-prod",
        "PLI_GMAIL_REDIRECT_URI": "https://api.pli.example.com/auth/gmail/callback",
        "PLI_MS_CLIENT_ID": "microsoft-client-id",
        "PLI_MS_CLIENT_SECRET": "microsoft-client-secret-prod",
        "PLI_MS_REDIRECT_URI": "https://api.pli.example.com/auth/microsoft/callback",
        "PLI_ENABLE_M2": "false",
    }
    env.update(overrides)
    return env


def test_cloud_production_ready_when_required_secret_handles_are_present() -> None:
    report = evaluate_prod_readiness(_base_env(), target="cloud-v1", deploy_env="production")

    assert report.status is Status.READY
    assert report.blockers == ()
    assert any(f.code == "m2-disabled" and f.severity == "info" for f in report.findings)


def test_cloud_production_blocks_dev_defaults_and_missing_providers() -> None:
    report = evaluate_prod_readiness(
        _base_env(
            PLI_DEBUG="true",
            PLI_SECRET_KEY="change-me-dev-only",
            PLI_BASE_URL="http://localhost:8000",
            PLI_APP_URL="http://localhost:5173",
            PLI_DATABASE_URL="postgresql://pli:pli@localhost:5432/pli",
            PLI_S3_SECRET_KEY="minioadmin",
            PLI_CORS_ORIGINS="*",
            PLI_EMAIL_PROVIDER="memory",
            PLI_GMAIL_CLIENT_SECRET="",
        ),
        target="cloud-v1",
        deploy_env="production",
    )

    codes = {finding.code for finding in report.blockers}
    assert report.status is Status.BLOCKED
    assert "debug-enabled" in codes
    assert "secret-key-missing-or-default" in codes
    assert "base-url-not-https" in codes
    assert "app-url-not-https" in codes
    assert "database-url-localhost" in codes
    assert "pli_s3_secret_key-missing-or-dummy" in codes
    assert "cors-origins-unsafe" in codes
    assert "email-provider-memory" in codes
    assert "gmail-oauth-missing" in codes


def test_cloud_production_blocks_malformed_fernet_key() -> None:
    report = evaluate_prod_readiness(
        _base_env(PLI_CLOUD_CRYPTO_KEY="not-a-valid-fernet-key-but-long-enough"),
        target="cloud-v1",
        deploy_env="production",
    )

    codes = {finding.code for finding in report.blockers}
    assert report.status is Status.BLOCKED
    assert "cloud-crypto-key-missing" in codes


def test_cloud_production_blocks_non_json_cors_origins() -> None:
    report = evaluate_prod_readiness(
        _base_env(PLI_CORS_ORIGINS="https://app.pli.example.com"),
        target="cloud-v1",
        deploy_env="production",
    )

    codes = {finding.code for finding in report.blockers}
    assert report.status is Status.BLOCKED
    assert "cors-origins-unsafe" in codes


def test_cloud_staging_blocks_localhost_http_urls_and_oauth_redirects() -> None:
    report = evaluate_prod_readiness(
        _base_env(
            PLI_BASE_URL="http://localhost:8000",
            PLI_APP_URL="http://127.0.0.1:5173",
            PLI_GMAIL_REDIRECT_URI="http://localhost:8000/auth/gmail/callback",
            PLI_MS_REDIRECT_URI="http://127.0.0.1:8000/auth/microsoft/callback",
        ),
        target="cloud-v1",
        deploy_env="staging",
    )

    codes = {finding.code for finding in report.blockers}
    assert report.status is Status.BLOCKED
    assert "base-url-not-https" in codes
    assert "app-url-not-https" in codes
    assert "gmail-redirect-not-https" in codes
    assert "microsoft-redirect-not-https" in codes


def test_cloud_staging_blocks_localhost_cors_origin() -> None:
    report = evaluate_prod_readiness(
        _base_env(PLI_CORS_ORIGINS='["http://localhost:5173"]'),
        target="cloud-v1",
        deploy_env="staging",
    )

    codes = {finding.code for finding in report.blockers}
    assert report.status is Status.BLOCKED
    assert "cors-origins-unsafe" in codes


def test_cloud_staging_and_production_block_local_or_non_https_s3_endpoints() -> None:
    for deploy_env in ("staging", "production"):
        report = evaluate_prod_readiness(
            _base_env(PLI_S3_ENDPOINT_URL="http://minio:9000"),
            target="cloud-v1",
            deploy_env=deploy_env,
        )

        codes = {finding.code for finding in report.blockers}
        assert report.status is Status.BLOCKED
        assert "s3-endpoint-not-public-https" in codes


def test_cloud_staging_blocks_internal_single_label_https_endpoints() -> None:
    report = evaluate_prod_readiness(
        _base_env(
            PLI_BASE_URL="https://api:8443",
            PLI_APP_URL="https://web:443",
            PLI_GMAIL_REDIRECT_URI="https://api/auth/gmail/callback",
            PLI_MS_REDIRECT_URI="https://api/auth/microsoft/callback",
            PLI_CORS_ORIGINS='["https://web:443"]',
            PLI_S3_ENDPOINT_URL="https://minio:9000",
        ),
        target="cloud-v1",
        deploy_env="staging",
    )

    codes = {finding.code for finding in report.blockers}
    assert report.status is Status.BLOCKED
    assert "base-url-not-https" in codes
    assert "app-url-not-https" in codes
    assert "gmail-redirect-not-https" in codes
    assert "microsoft-redirect-not-https" in codes
    assert "cors-origins-unsafe" in codes
    assert "s3-endpoint-not-public-https" in codes


def test_cloud_staging_blocks_legacy_ipv4_shorthand_endpoints() -> None:
    report = evaluate_prod_readiness(
        _base_env(
            PLI_BASE_URL="https://127.1:8443",
            PLI_APP_URL="https://10.1:443",
            PLI_GMAIL_REDIRECT_URI="https://127.0.1/auth/gmail/callback",
            PLI_MS_REDIRECT_URI="https://0.0.0/auth/microsoft/callback",
            PLI_CORS_ORIGINS='["https://192.168.1:443"]',
            PLI_S3_ENDPOINT_URL="https://10.1:9000",
        ),
        target="cloud-v1",
        deploy_env="staging",
    )

    codes = {finding.code for finding in report.blockers}
    assert report.status is Status.BLOCKED
    assert "base-url-not-https" in codes
    assert "app-url-not-https" in codes
    assert "gmail-redirect-not-https" in codes
    assert "microsoft-redirect-not-https" in codes
    assert "cors-origins-unsafe" in codes
    assert "s3-endpoint-not-public-https" in codes


def test_cloud_production_blocks_stripe_test_key_when_m2_enabled() -> None:
    report = evaluate_prod_readiness(
        _base_env(
            PLI_ENABLE_M2="true",
            PLI_STRIPE_SECRET_KEY="sk_test_1234567890abcdef",
            PLI_STRIPE_WEBHOOK_SECRET="whsec_1234567890abcdef",
            PLI_STRIPE_PRICE_MONTHLY="price_live_monthly",
            PLI_STRIPE_PRICE_YEARLY="price_live_yearly",
        ),
        target="cloud-v1",
        deploy_env="production",
    )

    codes = {finding.code for finding in report.blockers}
    assert report.status is Status.BLOCKED
    assert "stripe-secret-not-live" in codes


def test_local_v1_requires_local_paths_but_warns_for_optional_sqlcipher() -> None:
    report = evaluate_prod_readiness(
        {
            "PLI_MODE": "local",
            "PLI_DEBUG": "false",
            "PLI_DEMO": "false",
            "PLI_SECRET_KEY": "l" * 48,
            "PLI_BASE_URL": "http://localhost:8000",
            "PLI_APP_URL": "http://localhost:5173",
            "PLI_DB_PATH": "/tmp/pli-v1.sqlite",
            "PLI_ATTACHMENTS_DIR": "/tmp/pli-att",
        },
        target="local-v1",
        deploy_env="staging",
    )

    assert report.status is Status.READY
    assert report.blockers == ()
    assert [finding.code for finding in report.warnings] == ["sqlcipher-key-missing"]


def test_redact_env_keys_never_returns_secret_values() -> None:
    env = _base_env(PLI_PUBLIC_LABEL="PLI", OTHER_SECRET="ignore-me")

    redacted = redact_env_keys(env)

    assert redacted["PLI_SECRET_KEY"] == "[SET]"
    assert redacted["PLI_DATABASE_URL"] == "[SET]"
    assert redacted["PLI_GMAIL_CLIENT_SECRET"] == "[SET]"
    assert redacted["PLI_PUBLIC_LABEL"] == "PLI"
    assert "OTHER_SECRET" not in redacted
    assert "postgresql://" not in repr(redacted)
    assert "gmail-client-secret-prod" not in repr(redacted)
