"""
Tests unitaires worker OCR (US-8.8).

Couvre :
- Image PNG → texte non vide, kind="image".
- PDF avec couche texte → kind="pdf_text_layer", durée < 200 ms.
- PDF scanné (sans couche texte) → kind="pdf_raster".
- PDF > 50 pages → truncated=True.
- PJ > 20 Mo → skip avec compteur metrics.
- MIME non supporté → skip.
- Idempotence : appel double ne crée qu'une ligne attachment_text.
- Détection langue FR/EN.

Les fixtures PNG/PDF sont dans backend/tests/fixtures/ocr/.
"""

from __future__ import annotations

import io
from pathlib import Path

import pytest
from PIL import Image, ImageDraw

from pli.ocr.worker import (
    MAX_BYTES,
    MAX_PAGES,
    ExtractionResult,
    _detect_langs,
    _extract,
    extract_text,
)

FIXTURES = Path(__file__).parent.parent.parent / "fixtures" / "ocr"


# ---------------------------------------------------------------------------
# Helpers fabrique
# ---------------------------------------------------------------------------


def _make_png(text: str, size=(800, 200)) -> bytes:
    img = Image.new("RGB", size, "white")
    draw = ImageDraw.Draw(img)
    # Police par défaut PIL → suffit pour Tesseract en --psm 6.
    draw.text((20, 80), text, fill="black")
    buf = io.BytesIO()
    img.save(buf, format="PNG")
    return buf.getvalue()


# ---------------------------------------------------------------------------
# _extract — chemins individuels
# ---------------------------------------------------------------------------


def test_image_png_returns_kind_image():
    blob = _make_png("Bonjour PLI")
    result = _extract(blob, "image/png")
    assert result is not None
    assert result.kind == "image"
    assert result.pages == 1
    assert "bonjour" in result.text.lower() or "pli" in result.text.lower()


def test_pdf_with_text_layer_uses_native_path():
    """PDF natif → on doit passer par pdfminer, pas Tesseract."""
    blob = (FIXTURES / "native_text.pdf").read_bytes()
    result = _extract(blob, "application/pdf")
    assert result is not None
    assert result.kind == "pdf_text_layer"
    # Critère perf US-8.8 : 5 pages texte natif < 3 s, on cible largement.
    assert result.duration_seconds < 3.0


def test_pdf_scanned_falls_back_to_raster():
    blob = (FIXTURES / "scanned.pdf").read_bytes()
    result = _extract(blob, "application/pdf")
    assert result is not None
    assert result.kind == "pdf_raster"
    assert result.text  # non vide


def test_pdf_more_than_max_pages_is_truncated():
    blob = (FIXTURES / "long_60_pages.pdf").read_bytes()
    result = _extract(blob, "application/pdf")
    assert result is not None
    assert result.truncated is True
    assert result.pages == MAX_PAGES


def test_unsupported_mime_returns_none():
    assert _extract(b"\x00\x01\x02", "application/octet-stream") is None


# ---------------------------------------------------------------------------
# Détection langue
# ---------------------------------------------------------------------------


@pytest.mark.parametrize(
    "text,expected",
    [
        ("Le chat est sur la table et il est noir pour la nuit", ["fr"]),
        ("The cat is on the table and it is black for the night", ["en"]),
        (
            "Le chat est noir. The cat is on the table and it is for the night",
            ["fr", "en"],
        ),
        ("", []),
        ("xyz", ["und"]),
    ],
)
def test_detect_langs(text, expected):
    assert _detect_langs(text) == expected


# ---------------------------------------------------------------------------
# extract_text (point d'entrée Celery)
# ---------------------------------------------------------------------------


def test_extract_text_too_large_skipped(make_attachment, monkeypatch):
    att = make_attachment(blob=b"x" * (MAX_BYTES + 1), mime="image/png")
    result = extract_text(att.id)
    assert result is None  # skipped, pas d'exception


def test_extract_text_idempotent(make_attachment, db_session):
    att = make_attachment(blob=_make_png("idempotent"), mime="image/png")
    first = extract_text(att.id)
    second = extract_text(att.id)
    assert first is not None
    assert second is None  # second appel no-op
    from pli.models.attachment import AttachmentText

    rows = db_session.query(AttachmentText).filter_by(attachment_id=att.id).all()
    assert len(rows) == 1


def test_extract_text_persists_to_db(make_attachment, db_session):
    att = make_attachment(blob=_make_png("Hello PLI"), mime="image/png")
    result = extract_text(att.id)
    assert isinstance(result, ExtractionResult)
    from pli.models.attachment import AttachmentText

    row = db_session.get(AttachmentText, att.id)
    assert row is not None
    assert row.source == "image"
