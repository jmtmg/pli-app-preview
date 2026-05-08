# The product tour

On first login, PLI runs a **5-step visual tour**. ~60 seconds. No extra text, no video, no skip required but available.

## The 5 steps

1. **Inbox** — "Your mail, zero-distraction."
2. **Filter Humans / Notifications** — the PLI principle: separate what needs attention from what can wait.
3. **Swipe** — archive / pin / snooze without moving your hand.
4. **Search** — finds in seconds (FTS5 index, see [Search](06-search.md))
5. **Compose** — no WYSIWYG bloat, `/` for commands, shortcuts visible ([Shortcuts](12-shortcuts.md))

## Replaying

Settings → Appearance → **Replay tour**. Good for a colleague or after a pause.

## Skip

Pressing Esc or the X on any bubble ends it. Nothing is stored besides the "seen" flag.

## Why we don't force it

Forcing a tour is pedagogically useless: you learn an app by using it, not by watching it. PLI's tour is **facultative by design**.

## Telemetry

If you opted into anonymous telemetry, we record "tour_started / tour_step_seen / tour_completed" events — no content, just UX events. See [Privacy](23-local-encryption.md).
