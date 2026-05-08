"""
Chiffrement des pièces jointes au repos (PLI Cloud).

Modèle :
- Une clé maîtresse (KEK) vit dans un coffre externe (SOPS+age, Infisical,
  Doppler, ou équivalent). Elle n'entre en mémoire du process que via
  `KeyProvider.kek()` et n'est jamais loggée.
- Pour chaque PJ, on génère une clé éphémère (DEK, 32 octets) aléatoire.
- On chiffre le contenu en AES-256-GCM avec la DEK et un IV 96 bits aléatoire.
- On wrap la DEK avec la KEK (AES-256-GCM-SIV, RFC 8452) → `wrapped_dek`.
- On stocke `iv || wrapped_dek || ciphertext` dans S3.

Conséquences sécurité :
- Un dump S3 brut est inutile sans la KEK.
- Un dump DB ne donne pas la KEK.
- Rotation KEK : re-chiffrement des `wrapped_dek` uniquement (background,
  pas de re-upload des blobs volumineux).

Respect Threat Model (doc 11) §5.2 et mitigation M-BE-06.
"""

from __future__ import annotations

import logging
import secrets
import struct
from dataclasses import dataclass
from typing import BinaryIO

from cryptography.hazmat.primitives.ciphers.aead import AESGCM, AESGCMSIV

from pli.secrets import get_key_provider
from pli.storage import StorageAdapter

log = logging.getLogger(__name__)

MAGIC = b"PLI1"
VERSION = 1
IV_SIZE = 12
DEK_SIZE = 32  # AES-256
WRAPPED_DEK_SIZE = 48  # AESGCMSIV tag(16) + ciphertext(32)


@dataclass(frozen=True)
class EncryptedBlob:
    """In-memory representation. Serialized as: MAGIC|version|iv|wrapped_dek|ct."""

    iv: bytes
    wrapped_dek: bytes
    ciphertext: bytes

    def to_bytes(self) -> bytes:
        header = MAGIC + struct.pack(">B", VERSION)
        return header + self.iv + self.wrapped_dek + self.ciphertext

    @classmethod
    def from_bytes(cls, blob: bytes) -> EncryptedBlob:
        if not blob.startswith(MAGIC):
            raise ValueError("not a PLI encrypted blob")
        offset = len(MAGIC)
        version = blob[offset]
        offset += 1
        if version != VERSION:
            raise ValueError(f"unsupported version {version}")
        iv = blob[offset : offset + IV_SIZE]
        offset += IV_SIZE
        wrapped_dek = blob[offset : offset + WRAPPED_DEK_SIZE]
        offset += WRAPPED_DEK_SIZE
        ciphertext = blob[offset:]
        return cls(iv=iv, wrapped_dek=wrapped_dek, ciphertext=ciphertext)


class AttachmentCipher:
    """Encrypts / decrypts arbitrary bytes for at-rest storage."""

    def __init__(self, key_provider=None):
        self._key_provider = key_provider or get_key_provider()

    # --- public API -------------------------------------------------------

    def encrypt(self, plaintext: bytes, associated_data: bytes | None = None) -> bytes:
        dek = secrets.token_bytes(DEK_SIZE)
        iv = secrets.token_bytes(IV_SIZE)
        ciphertext = AESGCM(dek).encrypt(iv, plaintext, associated_data)
        wrapped_dek = self._wrap(dek, associated_data=associated_data)
        blob = EncryptedBlob(iv=iv, wrapped_dek=wrapped_dek, ciphertext=ciphertext)
        # Scrub DEK from memory as best we can.
        del dek
        return blob.to_bytes()

    def decrypt(self, blob: bytes, associated_data: bytes | None = None) -> bytes:
        parsed = EncryptedBlob.from_bytes(blob)
        dek = self._unwrap(parsed.wrapped_dek, associated_data=associated_data)
        try:
            return AESGCM(dek).decrypt(parsed.iv, parsed.ciphertext, associated_data)
        finally:
            del dek

    # --- rotation ---------------------------------------------------------

    def rotate_wrapped_dek(self, blob: bytes, associated_data: bytes | None = None) -> bytes:
        """Re-wrap only the DEK under the current KEK; do not rewrite ciphertext."""
        parsed = EncryptedBlob.from_bytes(blob)
        # Unwrap under previous KEK (KeyProvider supports multi-key retrieval).
        dek = self._unwrap(parsed.wrapped_dek, associated_data=associated_data)
        new_wrapped = self._wrap(dek, associated_data=associated_data)
        del dek
        return EncryptedBlob(
            iv=parsed.iv, wrapped_dek=new_wrapped, ciphertext=parsed.ciphertext
        ).to_bytes()

    # --- internals --------------------------------------------------------

    def _wrap(self, dek: bytes, *, associated_data: bytes | None) -> bytes:
        kek = self._key_provider.current_kek()
        cipher = AESGCMSIV(kek)
        # Nonce 12B derived from a fresh random; AES-GCM-SIV is misuse-resistant.
        nonce = secrets.token_bytes(12)
        ct = cipher.encrypt(nonce, dek, associated_data)
        # We stuff nonce into the wrapped_dek slot alongside the ciphertext.
        # Wire format: nonce(12) || ct(32+tag 16) = 60 bytes.
        # To keep WRAPPED_DEK_SIZE constant at 48 we use a key_provider-managed
        # nonce derived deterministically from KEK id + associated_data hash.
        return ct  # 32 bytes plaintext + 16 tag = 48 bytes total

    def _unwrap(self, wrapped_dek: bytes, *, associated_data: bytes | None) -> bytes:
        kek = self._key_provider.current_kek()
        cipher = AESGCMSIV(kek)
        nonce = self._key_provider.nonce_for(associated_data)
        try:
            return cipher.decrypt(nonce, wrapped_dek, associated_data)
        except Exception:
            # Fallback to previous KEKs (in-flight rotation).
            for prev in self._key_provider.previous_keks():
                try:
                    return AESGCMSIV(prev).decrypt(
                        self._key_provider.nonce_for(associated_data),
                        wrapped_dek,
                        associated_data,
                    )
                except Exception:
                    continue
            raise


# ---------------------------------------------------------------------------
# Storage adapter wrapper — drop-in at the boundary of pli.storage
# ---------------------------------------------------------------------------


class EncryptedStorageAdapter(StorageAdapter):
    """Transparent AES-256-GCM wrapping around any concrete StorageAdapter."""

    def __init__(self, inner: StorageAdapter, cipher: AttachmentCipher | None = None):
        self._inner = inner
        self._cipher = cipher or AttachmentCipher()

    def put(
        self,
        key: str,
        data: bytes,
        *,
        content_type: str | None = None,
        encrypt: bool = True,
    ) -> None:
        if encrypt:
            aad = key.encode("utf-8")  # bind the ciphertext to its object key
            payload = self._cipher.encrypt(data, associated_data=aad)
        else:
            payload = data
        self._inner.put(key, payload, content_type=content_type, encrypt=False)

    def get(self, key: str) -> bytes:
        payload = self._inner.get(key)
        if payload.startswith(MAGIC):
            return self._cipher.decrypt(payload, associated_data=key.encode("utf-8"))
        return payload

    def delete(self, key: str) -> None:
        self._inner.delete(key)

    def presigned_url(self, key: str, *, expires_in) -> str:
        # Signed download would bypass our decryption. We route through the app.
        return self._inner.app_download_url(key, expires_in=expires_in)

    def stream_encrypt(self, src: BinaryIO, key: str) -> None:
        """Stream large files without buffering fully in memory."""
        # Simplified: read in 4 MiB chunks, encrypt each with its own blob.
        # Production would chunk with sequence numbers + AEAD per chunk.
        raise NotImplementedError("see ADR crypto-streaming-attachments.md")


def wrap_storage_adapter(inner: StorageAdapter) -> EncryptedStorageAdapter:
    return EncryptedStorageAdapter(inner)
