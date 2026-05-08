"""Normalisation `RawMessage` → persistance.

Logique centrale :
    * déduplique les contacts par `email_normalized` (lowercase, strip alias +xxx)
    * détermine la direction `in`/`out` en comparant au compte propriétaire
    * classifie `human` vs `notif` (heuristique prefix : noreply, notification, no-reply, …)
    * extrait `snippet` si manquant depuis body_text (200 premiers chars)
"""

from __future__ import annotations

import re
from dataclasses import dataclass

NOTIF_PREFIXES = (
    "no-reply",
    "noreply",
    "notification",
    "notifications",
    "mailer-daemon",
    "support+",
    "no.reply",
    "bounces",
    "newsletter",
    "updates",
    "digest",
)


def normalize_email(email: str) -> str:
    """`Foo.Bar+tag@GMAIL.com` → `foo.bar@gmail.com`."""
    e = email.strip().lower()
    local, _, domain = e.partition("@")
    local = local.split("+", 1)[0]
    return f"{local}@{domain}" if domain else local


def classify_kind(email: str) -> str:
    """Retourne 'notif' ou 'human' selon l'adresse de l'expéditeur."""
    e = email.lower()
    local = e.split("@", 1)[0]
    if any(local.startswith(p) or p in local for p in NOTIF_PREFIXES):
        return "notif"
    return "human"


@dataclass
class Snippet:
    text: str

    @classmethod
    def from_body(cls, body_text: str | None, max_len: int = 200) -> Snippet:
        if not body_text:
            return cls("")
        clean = re.sub(r"\s+", " ", body_text.strip())
        return cls(clean[:max_len])
