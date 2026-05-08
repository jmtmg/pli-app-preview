"""Cryptographic primitives for PLI.

Deux couches distinctes :
- `oauth` — chiffrement des secrets OAuth au niveau applicatif (Fernet)
  ▸ utilise Sprint 1, mode local
- `attachments` / `backups` — chiffrement enveloppe (AES-GCM + KEK externe)
  ▸ utilise mode cloud, depend de `pli.secrets` (non livre Sprint 1)

Les sous-modules cloud sont **lazy-loaded** pour que `from pli.crypto import
decrypt_str` fonctionne meme quand `pli.secrets` n'existe pas encore.
"""

from pli.crypto.oauth import decrypt_str, encrypt_str, get_crypto

__all__ = [
    "get_crypto",
    "encrypt_str",
    "decrypt_str",
    "AttachmentCipher",
    "wrap_storage_adapter",
]


def __getattr__(name):
    """PEP 562 — charge les symboles cloud a la demande."""
    if name in ("AttachmentCipher", "wrap_storage_adapter"):
        from pli.crypto.attachments import AttachmentCipher, wrap_storage_adapter

        return {
            "AttachmentCipher": AttachmentCipher,
            "wrap_storage_adapter": wrap_storage_adapter,
        }[name]
    raise AttributeError(f"module 'pli.crypto' has no attribute {name!r}")
