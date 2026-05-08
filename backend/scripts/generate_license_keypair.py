#!/usr/bin/env python
"""Génère une paire Ed25519 pour signer les licences PLI Plus offline.

Usage :
    python scripts/generate_license_keypair.py

La clé privée va dans PLI_LICENSE_SIGNING_KEY (secret côté serveur Cloud).
La clé publique va dans le binaire PLI (constante EMBEDDED_PUBLIC_KEY_B64)
ou dans la variable d'env PLI_LICENSE_PUBLIC_KEY côté client.
"""
from __future__ import annotations

from pli.licensing.local_key import generate_keypair


def main() -> None:
    sk, pk = generate_keypair()
    print("# PLI — clé de signature Ed25519 pour licences offline")
    print("# Généré le :", __import__("datetime").datetime.utcnow().isoformat(), "UTC")
    print()
    print("# À définir côté serveur Cloud (SECRET, jamais committer) :")
    print(f"PLI_LICENSE_SIGNING_KEY={sk}")
    print()
    print("# À embarquer dans le client Local (public, peut être committé) :")
    print(f"PLI_LICENSE_PUBLIC_KEY={pk}")


if __name__ == "__main__":
    main()
