"""Accesseur singleton du `CryptoAdapter` — pour le chiffrement OAuth local.

Sprint 1 (local) :
    * En mode `local` → `LocalCryptoAdapter` (Fernet + clé `~/.pli/crypto.key`)
    * En mode `cloud` → à brancher M3 (KMS, via pli.secrets + KeyProvider)

Utilisation :
    from pli.crypto import get_crypto, encrypt_str, decrypt_str
    token_enc = encrypt_str("access_token_value")
"""

from __future__ import annotations

from functools import lru_cache

from ..adapters.base import CryptoAdapter
from ..config import settings


@lru_cache(maxsize=1)
def get_crypto() -> CryptoAdapter:
    """Retourne l'instance `CryptoAdapter` adaptée au mode courant.

    Le lru_cache garantit qu'on n'instancie qu'une fois par process — les
    LocalCryptoAdapter lisent/écrivent une clé sur disque, il serait coûteux
    (et inutile) de la recharger à chaque requête.
    """
    if settings.mode == "local":
        from ..adapters.local import LocalCryptoAdapter

        return LocalCryptoAdapter()
    raise RuntimeError("CryptoAdapter cloud non implémenté — prévu M3 (branchement KMS).")


def encrypt_str(plaintext: str) -> str:
    """Chiffre une chaîne utf-8 et retourne un token Fernet ASCII."""
    return get_crypto().encrypt(plaintext.encode("utf-8")).decode("ascii")


def decrypt_str(ciphertext: str) -> str:
    """Inverse de `encrypt_str`. Lève `InvalidToken` si altéré ou clé différente."""
    return get_crypto().decrypt(ciphertext.encode("ascii")).decode("utf-8")
