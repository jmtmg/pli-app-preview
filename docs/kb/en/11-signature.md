# Email signature

## Create

Settings → **Signatures** → **New signature**. Plain text or minimal rich (same restrictions as composer). Variables: `{{firstname}}`, `{{job}}`, `{{company}}`, `{{phone}}`, `{{site}}`.

## Multiple

Unlimited. One **default per account**, plus a global default.

Example: `personal-gmail` → "— Alex" vs `pro-acme` → "Alex Morel · Product at Acme · +33 …".

## Image / logo

Supported (JPG/PNG ≤ 500 KB). Hosted on our CDN (EU). Inline referenced (Content-ID). Compatible with all major providers.

⚠️ Your recipient's client may block external images on first view. That's a fact of email, not a PLI limit.

## Auto-insert

On `Reply` / `Compose` / `Forward`: signature inserted at cursor. On `Reply All`: same.

Toggle: Preferences → **Auto-insert signature on reply**.

## HTML signatures (from another client)

You can **paste** an HTML signature — PLI cleans the dangerous tags (scripts, remote JS) and keeps the rest. For pixel-perfect corporate signatures, prefer the PLI editor (cleaner rendering across recipients).

## Per-thread

Right-click the signature block in composer → **Pick another signature** or **Remove from this message**.
