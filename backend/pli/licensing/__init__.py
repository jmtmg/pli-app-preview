"""Licences PLI — offline (Local mode) et in-process (Cloud lookup).

- `local_key`  : licence Ed25519, hors-ligne, stockée dans ~/.pli/license.json
                 Contient : {user_hash, plan, issued_at, expires_at, sig}
                 Permet de débloquer PLI Plus sur une machine désynchronisée.

- `remote_key` : en mode cloud, la table `licenses` est la source de vérité.
                 Pas de cryptographie asymétrique — le user est authentifié
                 par JWT et le serveur vérifie `subscriptions.plan`.
"""

from .local_key import (
    LocalLicense,
    generate_keypair,
    issue_local_license,
    load_license,
    save_license,
    verify_license,
)

__all__ = [
    "LocalLicense",
    "generate_keypair",
    "issue_local_license",
    "load_license",
    "save_license",
    "verify_license",
]
