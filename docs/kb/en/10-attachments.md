# Attachments

## Attach

- **Drag-drop** into the composer (anywhere in the window)
- **`/attach`** inside the body
- **Paperclip icon** at the bottom

## Hard limits

| Provider | Single attachment | Total message |
|---|---|---|
| Gmail | 25 MB | 25 MB |
| Microsoft | 20 MB (in body) or 150 MB (OneDrive link) | 20 MB |

Above: PLI offers a **secure link** (expires at 30 days, AES-256 stored on our EU servers).

## Blocked file types

Both Gmail and Microsoft block `.exe`, `.bat`, `.js`, `.vbs`, `.jar`, and some others. Zip those (but: Gmail also blocks zips that contain blocked extensions).

## OCR

In Cloud and Plus Local, PDFs and images are OCR'd at ingest (Tesseract, FR+EN). Their text is searchable like any email body.

## Virus scan

Cloud: ClamAV scan at ingest. Infected files are quarantined, not delivered to you, a banner tells you who sent it. Local: no scan (your system antivirus handles it).

## Preview

Images, PDFs, videos (up to 100 MB), .eml (emails forwarded as attachment), DOCX/XLSX/PPTX (rendered via LibreOffice in background).

## Download

Click the attachment → downloads to your OS downloads folder. On mobile (V1.2), opens with system share sheet.
