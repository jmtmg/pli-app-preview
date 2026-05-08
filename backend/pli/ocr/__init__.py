"""
Module OCR serveur PLI (Sprint 8 — US-8.8).

Pourquoi serveur (et pas client) :
- Tesseract en WASM côté navigateur explose le bundle (+8 Mo) et bloque
  l'UI sur mobiles bas de gamme.
- L'OCR doit alimenter l'index FTS *immédiatement* après réception d'un
  message, pour que la PJ soit recherchable même si l'utilisateur n'a
  jamais ouvert le mail.
- Conformité RGPD : la donnée brute (PJ scannée) est traitée dans un
  worker isolé et n'est jamais persistée hors du chiffrement AES-256-GCM
  déjà en place pour les pièces jointes.

Architecture :
    Reception PJ → enqueue(ocr.extract_text) → Worker Celery
                                                    ↓
                                Tesseract (FRA + ENG) → texte brut
                                                    ↓
                              Stockage chiffré + index FTS (table attachment_text)

Limites (cf. SPRINT-8-BACKLOG.md US-8.8) :
- Taille max d'entrée : 20 Mo (refus au-delà, log warning).
- Pages PDF max : 50 (au-delà : seules les 50 premières sont OCRisées,
  flag `truncated=true` dans le résultat).
- PDF avec couche texte natif : on l'extrait via pdfminer plutôt que
  d'OCRiser à nouveau (SLO < 200 ms vs 3 s).
- Cible : 5 pages PDF en < 3 s sur worker 2 vCPU.
"""

from pli.ocr.api import router as ocr_router
from pli.ocr.worker import ExtractionResult, extract_text

__all__ = ["ocr_router", "extract_text", "ExtractionResult"]
