"""Script admin : émission d'un batch d'invitations + envoi email.

Usage :
    PLI_ENV=prod python -m scripts.issue_batch --batch 1 --dry-run
    PLI_ENV=prod python -m scripts.issue_batch --batch 1
"""
from __future__ import annotations

import argparse
import asyncio
import sys
from pathlib import Path

# Rendre le package 'pli' importable quand on lance depuis backend/
sys.path.insert(0, str(Path(__file__).parent.parent))

from pli.beta import batches
from pli.db.session import SessionLocal
from pli.emails.provider import send_invitation_email


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--batch", type=int, required=True, choices=[1, 2, 3, 4])
    parser.add_argument("--dry-run", action="store_true", help="n'émet pas les emails")
    args = parser.parse_args()

    session = SessionLocal()
    try:
        issued = batches.issue_batch(session, batch_number=args.batch)
        print(f"[ok] Batch #{args.batch} : {len(issued)} codes générés")

        if args.dry_run:
            for inv in issued[:3]:
                print(f"  - {inv.email}  {inv.code}  exp={inv.expires_at.isoformat()}")
            print("[dry-run] transaction annulée")
            session.rollback()
            return 0

        session.commit()
        print(f"[ok] Transaction committée — envoi emails …")
        asyncio.run(_send_all(issued))
        print(f"[ok] {len(issued)} emails envoyés")
        return 0
    except Exception as e:
        session.rollback()
        print(f"[err] {e}", file=sys.stderr)
        return 1
    finally:
        session.close()


async def _send_all(issued) -> None:
    for inv in issued:
        await send_invitation_email(email=inv.email, code=inv.code, batch_number=inv.batch_number)


if __name__ == "__main__":
    sys.exit(main())
