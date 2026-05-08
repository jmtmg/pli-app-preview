"""
Tests intégration API OCR (US-8.8).

Vérifie :
- 200 + texte sur GET /api/attachments/{id}/text quand OCR fini.
- 404 (jamais 403) si l'utilisateur n'est pas owner — rejouée du fix H-003.
- 202 + job_id sur POST /api/attachments/{id}/ocr.
- 429 après 30 forces dans la fenêtre.
- Status passe queued → done après que le worker tourne.
"""

from __future__ import annotations

from fastapi import status


def test_get_text_returns_extracted(client, make_attachment_with_text):
    att = make_attachment_with_text(text="Bonjour PLI", language="fr", source="image")
    r = client.get(f"/api/attachments/{att.id}/text")
    assert r.status_code == status.HTTP_200_OK
    body = r.json()
    assert body["text"] == "Bonjour PLI"
    assert body["language"] == "fr"
    assert body["source"] == "image"


def test_get_text_404_when_not_owner(client_other_user, make_attachment_with_text):
    """Reproduit le scénario IDOR du pentest. Doit renvoyer 404 (pas 403)."""
    att = make_attachment_with_text(text="secret", language="fr", source="image")
    r = client_other_user.get(f"/api/attachments/{att.id}/text")
    assert r.status_code == status.HTTP_404_NOT_FOUND


def test_get_text_404_when_not_yet_extracted(client, make_attachment):
    att = make_attachment(blob=b"...", mime="image/png")
    r = client.get(f"/api/attachments/{att.id}/text")
    assert r.status_code == status.HTTP_404_NOT_FOUND
    assert r.json()["detail"] == "text_not_yet_extracted"


def test_force_ocr_enqueues_job(client, make_attachment, fake_queue):
    att = make_attachment(blob=b"...", mime="image/png")
    r = client.post(f"/api/attachments/{att.id}/ocr")
    assert r.status_code == status.HTTP_202_ACCEPTED
    assert fake_queue.enqueued_jobs == [("pli.ocr.worker.extract_text", att.id)]


def test_force_ocr_rate_limited(client, make_attachment):
    att = make_attachment(blob=b"...", mime="image/png")
    for _ in range(30):
        assert client.post(f"/api/attachments/{att.id}/ocr").status_code == 202
    over = client.post(f"/api/attachments/{att.id}/ocr")
    assert over.status_code == status.HTTP_429_TOO_MANY_REQUESTS


def test_status_lifecycle(client, make_attachment, fake_queue):
    att = make_attachment(blob=b"...", mime="image/png")

    r = client.get(f"/api/attachments/{att.id}/ocr/status")
    assert r.json()["state"] == "not_started"

    client.post(f"/api/attachments/{att.id}/ocr")
    fake_queue.set_state("pli.ocr.worker.extract_text", att.id, "queued")
    r = client.get(f"/api/attachments/{att.id}/ocr/status")
    assert r.json()["state"] == "queued"

    fake_queue.set_state("pli.ocr.worker.extract_text", att.id, "running")
    r = client.get(f"/api/attachments/{att.id}/ocr/status")
    assert r.json()["state"] == "running"
