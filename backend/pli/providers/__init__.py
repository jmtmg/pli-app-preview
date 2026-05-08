"""Adapters providers mail (pattern Strategy).

Chaque provider implémente `MailProvider` (base.py). On instancie via
`get_provider(account)` qui dispatch sur `gmail` ou `microsoft`.
"""

from .base import MailProvider, get_provider

__all__ = ["MailProvider", "get_provider"]
