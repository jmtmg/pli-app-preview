"""Orchestration de la synchronisation.

- `service.sync_account(account_id, kind)` — point d'entrée unifié
- `parser.raw_to_message(raw, account)` — normalisation + déduplication contact
"""

from .service import sync_account

__all__ = ["sync_account"]
