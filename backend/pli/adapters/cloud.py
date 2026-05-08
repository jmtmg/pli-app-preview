"""Adapters pour mode Cloud — multi-tenant, PostgreSQL, stockage objet S3."""

from __future__ import annotations

import hashlib
from collections.abc import AsyncIterator

import boto3
from botocore.client import Config
from fastapi import HTTPException, Request

from ..config import settings
from .base import (
    CryptoAdapter,
    Principal,
    SearchAdapter,
    SettingsStore,
    StorageAdapter,
    StorageNotFound,
    StoredObject,
    TenantIsolationError,
)

# ---------------------------------------------------------------------------
# Storage S3-compatible
# ---------------------------------------------------------------------------


class CloudStorageAdapter(StorageAdapter):
    """S3-compatible (AWS S3, Cloudflare R2, Scaleway Object Storage, MinIO).

    Contrainte d'isolation : toutes les clés sont préfixées `t/<tenant_id>/`.
    Une clé hors de ce préfixe est refusée.
    """

    def __init__(
        self,
        *,
        endpoint_url: str | None = None,
        access_key: str | None = None,
        secret_key: str | None = None,
        bucket: str | None = None,
        region: str = "auto",
    ) -> None:
        self.bucket = bucket or settings.s3_bucket or "pli-staging-attachments"
        self.client = boto3.client(
            "s3",
            endpoint_url=endpoint_url or settings.s3_endpoint_url,
            aws_access_key_id=access_key
            or (settings.s3_access_key.get_secret_value() if settings.s3_access_key else None),
            aws_secret_access_key=secret_key
            or (settings.s3_secret_key.get_secret_value() if settings.s3_secret_key else None),
            region_name=region,
            config=Config(signature_version="s3v4"),
        )

    @staticmethod
    def _scoped(tenant_id: str, key: str) -> str:
        if not tenant_id or "/" in tenant_id:
            raise TenantIsolationError("Invalid tenant_id")
        if key.startswith("t/"):
            raise TenantIsolationError("Key must not include tenant prefix manually")
        return f"t/{tenant_id}/{key}"

    async def put(
        self,
        *,
        tenant_id: str,
        key: str,
        data: bytes,
        content_type: str | None = None,
    ) -> StoredObject:
        full = self._scoped(tenant_id, key)
        self.client.put_object(
            Bucket=self.bucket,
            Key=full,
            Body=data,
            ContentType=content_type or "application/octet-stream",
            ServerSideEncryption="AES256",
        )
        sha = hashlib.sha256(data).hexdigest()
        return StoredObject(key=key, size_bytes=len(data), content_type=content_type, sha256=sha)

    async def get(self, *, tenant_id: str, key: str) -> bytes:
        full = self._scoped(tenant_id, key)
        try:
            resp = self.client.get_object(Bucket=self.bucket, Key=full)
        except self.client.exceptions.NoSuchKey as e:
            raise StorageNotFound(key) from e
        return resp["Body"].read()

    async def delete(self, *, tenant_id: str, key: str) -> None:
        full = self._scoped(tenant_id, key)
        self.client.delete_object(Bucket=self.bucket, Key=full)

    async def presigned_url(self, *, tenant_id: str, key: str, ttl_seconds: int = 300) -> str:
        full = self._scoped(tenant_id, key)
        return self.client.generate_presigned_url(
            "get_object",
            Params={"Bucket": self.bucket, "Key": full},
            ExpiresIn=ttl_seconds,
        )

    async def iter_tenant(self, *, tenant_id: str) -> AsyncIterator[StoredObject]:
        prefix = f"t/{tenant_id}/"
        paginator = self.client.get_paginator("list_objects_v2")
        for page in paginator.paginate(Bucket=self.bucket, Prefix=prefix):
            for obj in page.get("Contents", []):
                yield StoredObject(
                    key=obj["Key"].removeprefix(prefix),
                    size_bytes=obj["Size"],
                    content_type=None,
                    sha256=obj.get("ETag", "").strip('"'),
                )


# ---------------------------------------------------------------------------
# Search — PostgreSQL tsvector
# ---------------------------------------------------------------------------


class CloudSearchAdapter(SearchAdapter):
    """Utilise la colonne `fts` (tsvector) + trigger de maintenance,
    filtrée systématiquement par `user_id`.
    """

    async def index_message(
        self, *, tenant_id: str, message_id: str, subject: str, body: str, from_: str
    ) -> None:
        # Trigger DB maintient fts — rien à faire.
        return None

    async def query(self, *, tenant_id: str, q: str, limit: int = 50) -> list[dict]:
        from ..db import get_pg_conn

        async with get_pg_conn() as conn:
            rows = await conn.fetch(
                """
                SELECT id, subject,
                       ts_headline('simple', body_text, plainto_tsquery('simple', $1),
                                   'StartSel=[,StopSel=],MaxWords=15,MinWords=5') AS snip
                FROM messages
                WHERE user_id = $2
                  AND fts @@ plainto_tsquery('simple', $1)
                ORDER BY ts_rank(fts, plainto_tsquery('simple', $1)) DESC
                LIMIT $3
                """,
                q,
                tenant_id,
                limit,
            )
        return [dict(r) for r in rows]

    async def delete_message(self, *, tenant_id: str, message_id: str) -> None:
        return None


# ---------------------------------------------------------------------------
# Principal resolver — JWT
# ---------------------------------------------------------------------------


async def cloud_principal_resolver(request: Request) -> Principal:
    """Extrait le Principal depuis l'access JWT dans l'header Authorization."""
    from ..auth.jwt import TokenError, decode_access_token

    auth_header = request.headers.get("authorization") or ""
    if not auth_header.lower().startswith("bearer "):
        raise HTTPException(status_code=401, detail="missing_bearer_token")
    token = auth_header.split(" ", 1)[1].strip()
    try:
        claims = decode_access_token(token)
    except TokenError as e:
        raise HTTPException(status_code=401, detail=f"invalid_token:{e}") from e
    return Principal(
        tenant_id=claims["sub"],
        user_id=claims["sub"],
        plan=claims.get("plan", "free"),
        email=claims.get("email"),
    )


# ---------------------------------------------------------------------------
# Settings store — PG table user_settings
# ---------------------------------------------------------------------------


class CloudSettingsStore(SettingsStore):
    async def get(self, *, tenant_id: str, key: str) -> str | None:
        from ..db import get_pg_conn

        async with get_pg_conn() as conn:
            row = await conn.fetchrow(
                "SELECT value FROM user_settings WHERE user_id = $1 AND key = $2",
                tenant_id,
                key,
            )
        return row["value"] if row else None

    async def set(self, *, tenant_id: str, key: str, value: str) -> None:
        from ..db import get_pg_conn

        async with get_pg_conn() as conn:
            await conn.execute(
                """
                INSERT INTO user_settings (user_id, key, value)
                VALUES ($1, $2, $3)
                ON CONFLICT (user_id, key) DO UPDATE SET value = EXCLUDED.value
                """,
                tenant_id,
                key,
                value,
            )

    async def delete(self, *, tenant_id: str, key: str) -> None:
        from ..db import get_pg_conn

        async with get_pg_conn() as conn:
            await conn.execute(
                "DELETE FROM user_settings WHERE user_id = $1 AND key = $2",
                tenant_id,
                key,
            )


# ---------------------------------------------------------------------------
# Crypto — KMS (simplifié pour M2 : clé maître env var,
# M3 passera en vrai KMS AWS / Scaleway)
# ---------------------------------------------------------------------------


class CloudCryptoAdapter(CryptoAdapter):
    def __init__(self) -> None:
        from cryptography.fernet import Fernet

        key = settings.cloud_crypto_key
        if not key:
            raise RuntimeError("PLI_CLOUD_CRYPTO_KEY manquant en mode Cloud")
        self._fernet = Fernet(key.get_secret_value().encode())

    def encrypt(self, plaintext: bytes) -> bytes:
        return self._fernet.encrypt(plaintext)

    def decrypt(self, ciphertext: bytes) -> bytes:
        return self._fernet.decrypt(ciphertext)
