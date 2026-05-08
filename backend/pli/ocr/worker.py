"""
Worker OCR Tesseract (Sprint 8 — US-8.8).

Pipeline :
    1. Charge la PJ chiffrée depuis le storage (déjà déchiffrée par
       EncryptedStorageAdapter).
    2. Détecte le type MIME via libmagic (pas l'extension : un .pdf
       envoyé en .jpg doit être traité comme PDF).
    3. Si PDF :
        a. Tente d'extraire la couche texte native via pdfminer.six.
           Si > 50 caractères / page, on shortcut et on retourne ce
           texte (3 s → 200 ms).
        b. Sinon, rasterise les 50 premières pages via pdf2image (DPI 200,
           compromis qualité/vitesse pour Tesseract).
        c. Concatène les sorties Tesseract avec délimiteur de page \f.
    4. Si image (PNG/JPG/TIFF/WEBP) : Tesseract direct.
    5. Stocke le texte dans la table `attachment_text` (FK vers
       `attachment.id`) — déjà couverte par RLS multi-tenant.
    6. Met à jour l'index FTS5 (déclencheur SQL existant en Local mode,
       trigger PostgreSQL `tsvector` en Cloud).

Sécurité :
- Le texte OCRisé est traité comme contenu utilisateur : pas d'eval,
  pas de transmission tierce.
- Tesseract est lancé sans modèle LSTM custom (uniquement les modèles
  fra/eng téléchargés via apt). Pas de chargement dynamique.
- Limite mémoire worker : 512 Mo (cgroup). pdf2image peut consommer
  beaucoup pour des PDF haute résolution → on impose --thread-limit 1.
"""

from __future__ import annotations

import io
import logging
import time
from collections.abc import Iterable
from dataclasses import dataclass, field

import magic
import pytesseract
from pdf2image import convert_from_bytes
from pdfminer.high_level import extract_text as pdf_extract_text
from PIL import Image

from pli.crypto.attachments import EncryptedStorageAdapter
from pli.db.session import session_scope
from pli.metrics import counter, histogram
from pli.models.attachment import Attachment, AttachmentText

logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Constantes & limites (justifiées dans SPRINT-8-BACKLOG.md US-8.8)
# ---------------------------------------------------------------------------

MAX_BYTES = 20 * 1024 * 1024  # 20 Mo
MAX_PAGES = 50
PDF_TEXT_LAYER_THRESHOLD = 50  # caractères / page : si plus, on skip OCR
TESSERACT_LANGS = "fra+eng"  # FR prioritaire, EN fallback (ordre important)
RASTER_DPI = 200

OCR_DURATION = histogram(
    "pli_ocr_duration_seconds",
    "Durée d'extraction OCR par PJ.",
    buckets=(0.1, 0.5, 1.0, 2.0, 3.0, 5.0, 10.0, 30.0),
    labels=("kind",),  # "image" | "pdf_text_layer" | "pdf_raster"
)
OCR_FAILURES = counter(
    "pli_ocr_failures_total",
    "Nombre d'échecs OCR (par cause).",
    labels=("reason",),
)
OCR_SKIPPED = counter(
    "pli_ocr_skipped_total",
    "Nombre de PJ ignorées (taille, type non supporté).",
    labels=("reason",),
)

SUPPORTED_IMAGE_MIMES = {
    "image/png",
    "image/jpeg",
    "image/tiff",
    "image/webp",
    "image/bmp",
}
SUPPORTED_PDF_MIMES = {"application/pdf"}


@dataclass
class ExtractionResult:
    """Résultat d'une extraction OCR.

    `kind` indique le chemin d'extraction utilisé (utile pour métriques
    et tests : on veut s'assurer que les PDF natifs ne passent pas par
    Tesseract).
    """

    text: str
    kind: str  # "image" | "pdf_text_layer" | "pdf_raster"
    pages: int
    truncated: bool = False
    duration_seconds: float = 0.0
    languages_detected: list[str] = field(default_factory=list)


# ---------------------------------------------------------------------------
# Point d'entrée Celery
# ---------------------------------------------------------------------------


def extract_text(attachment_id: str) -> ExtractionResult | None:
    """Tâche Celery : OCRise la PJ et persiste le texte.

    Idempotente : si `attachment_text` existe déjà pour cet ID, on no-op
    (utile pour replays). Renvoie le résultat pour les tests unitaires —
    Celery ignore la valeur de retour.
    """
    storage = EncryptedStorageAdapter.get_default()

    with session_scope() as session:
        att = session.get(Attachment, attachment_id)
        if att is None:
            logger.warning("attachment %s introuvable, skip OCR", attachment_id)
            return None

        existing = session.get(AttachmentText, attachment_id)
        if existing is not None:
            logger.debug("attachment %s déjà OCRisé, skip", attachment_id)
            return None

        try:
            blob = storage.download(att.storage_key)
        except FileNotFoundError:
            OCR_FAILURES.labels(reason="storage_missing").inc()
            logger.error("storage_key %s introuvable", att.storage_key)
            return None

        if len(blob) > MAX_BYTES:
            OCR_SKIPPED.labels(reason="too_large").inc()
            logger.info(
                "attachment %s ignoré (%d bytes > %d)",
                attachment_id,
                len(blob),
                MAX_BYTES,
            )
            return None

        mime = magic.from_buffer(blob, mime=True)
        result = _extract(blob, mime)

        if result is None:
            return None

        session.add(
            AttachmentText(
                attachment_id=attachment_id,
                text=result.text,
                language=",".join(result.languages_detected) or "und",
                pages=result.pages,
                truncated=result.truncated,
                source=result.kind,
            )
        )
        # Le trigger SQL `attachment_text_fts_au` met à jour FTS5/tsvector.
        return result


# ---------------------------------------------------------------------------
# Dispatch interne
# ---------------------------------------------------------------------------


def _extract(blob: bytes, mime: str) -> ExtractionResult | None:
    start = time.perf_counter()

    if mime in SUPPORTED_IMAGE_MIMES:
        try:
            text = _ocr_image(blob)
        except pytesseract.TesseractError as exc:
            OCR_FAILURES.labels(reason="tesseract_image").inc()
            logger.exception("tesseract échec sur image: %s", exc)
            return None
        duration = time.perf_counter() - start
        OCR_DURATION.labels(kind="image").observe(duration)
        return ExtractionResult(
            text=text,
            kind="image",
            pages=1,
            duration_seconds=duration,
            languages_detected=_detect_langs(text),
        )

    if mime in SUPPORTED_PDF_MIMES:
        # Étape 1 : tentative couche texte native (rapide).
        native = _try_pdf_text_layer(blob)
        if native is not None:
            duration = time.perf_counter() - start
            OCR_DURATION.labels(kind="pdf_text_layer").observe(duration)
            return ExtractionResult(
                text=native.text,
                kind="pdf_text_layer",
                pages=native.pages,
                truncated=native.truncated,
                duration_seconds=duration,
                languages_detected=_detect_langs(native.text),
            )

        # Étape 2 : rasterisation + Tesseract.
        try:
            text, pages, truncated = _ocr_pdf_raster(blob)
        except Exception as exc:  # pdf2image relance des subprocess errors
            OCR_FAILURES.labels(reason="pdf_raster").inc()
            logger.exception("rasterisation PDF échouée: %s", exc)
            return None
        duration = time.perf_counter() - start
        OCR_DURATION.labels(kind="pdf_raster").observe(duration)
        return ExtractionResult(
            text=text,
            kind="pdf_raster",
            pages=pages,
            truncated=truncated,
            duration_seconds=duration,
            languages_detected=_detect_langs(text),
        )

    OCR_SKIPPED.labels(reason="unsupported_mime").inc()
    logger.info("MIME non supporté pour OCR: %s", mime)
    return None


# ---------------------------------------------------------------------------
# Implémentations spécifiques
# ---------------------------------------------------------------------------


def _ocr_image(blob: bytes) -> str:
    img = Image.open(io.BytesIO(blob))
    # `--psm 6` = bloc uniforme de texte (meilleur pour scans de mails).
    return pytesseract.image_to_string(img, lang=TESSERACT_LANGS, config="--psm 6 --oem 1").strip()


@dataclass
class _NativeText:
    text: str
    pages: int
    truncated: bool


def _try_pdf_text_layer(blob: bytes) -> _NativeText | None:
    """Tente d'extraire la couche texte native d'un PDF.

    Renvoie None si le PDF n'a pas de couche texte exploitable (typique
    d'un scan).
    """
    try:
        text = pdf_extract_text(io.BytesIO(blob), maxpages=MAX_PAGES)
    except Exception as exc:
        logger.debug("pdfminer ne peut lire ce PDF (%s) → fallback raster", exc)
        return None

    pages = text.count("\f") + 1 if text else 0
    if pages == 0:
        return None

    # Heuristique : si on a moins de 50 caractères par page en moyenne,
    # c'est probablement un PDF scanné avec une fausse couche texte
    # (ex. signatures vides). On préfère rasteriser.
    avg_per_page = len(text.replace("\f", "")) / max(pages, 1)
    if avg_per_page < PDF_TEXT_LAYER_THRESHOLD:
        return None

    truncated = pages >= MAX_PAGES  # extract_text s'est arrêté à MAX_PAGES
    return _NativeText(text=text.strip(), pages=pages, truncated=truncated)


def _ocr_pdf_raster(blob: bytes) -> tuple[str, int, bool]:
    images = convert_from_bytes(
        blob,
        dpi=RASTER_DPI,
        fmt="png",
        thread_count=1,  # cgroup limite 512 Mo, on évite la concurrence
        first_page=1,
        last_page=MAX_PAGES,
    )
    truncated = len(images) >= MAX_PAGES

    parts: list[str] = []
    for img in images:
        parts.append(
            pytesseract.image_to_string(img, lang=TESSERACT_LANGS, config="--psm 6 --oem 1")
        )
    return "\f".join(p.strip() for p in parts), len(images), truncated


def _detect_langs(text: str) -> list[str]:
    """Renvoie ["fr", "en"] si on détecte les deux, sinon le dominant.

    Implémentation volontairement naïve (heuristique stop-words) pour
    éviter d'embarquer langdetect/fasttext qui pèsent 100+ Mo. En pratique
    suffisant pour étiqueter les PJ FR vs EN.
    """
    if not text:
        return []

    sample = text.lower()[:5000]
    fr_hits = sum(1 for w in (" le ", " la ", " et ", " est ", " pour ") if w in sample)
    en_hits = sum(1 for w in (" the ", " and ", " of ", " to ", " is ") if w in sample)

    detected: list[str] = []
    if fr_hits >= 2:
        detected.append("fr")
    if en_hits >= 2:
        detected.append("en")
    return detected or ["und"]


# ---------------------------------------------------------------------------
# Helper pour purge / réindexation (ops)
# ---------------------------------------------------------------------------


def reindex_account(account_id: str) -> int:
    """Re-OCRise toutes les PJ d'un compte (utile après mise à jour modèle).

    Renvoie le nombre de PJ ré-enqueuées. À déclencher manuellement via
    `pli ops ocr-reindex --account=<id>` (cf. CLI ops dans Sprint 9).
    """
    from pli.tasks import queue  # import local : casse cycle Celery <-> models

    with session_scope() as session:
        ids: Iterable[str] = (
            session.query(Attachment.id).filter(Attachment.account_id == account_id).all()
        )
        count = 0
        for (att_id,) in ids:
            queue.enqueue("pli.ocr.worker.extract_text", att_id)
            count += 1
    logger.info("re-OCR enqueued %d attachments for account %s", count, account_id)
    return count
