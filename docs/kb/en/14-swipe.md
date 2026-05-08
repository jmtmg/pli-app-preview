# Swipe actions

## Thresholds

PLI uses **two thresholds** per direction:

- 15 % of screen width → light action
- 33 % → definitive action

Why two: to avoid destructive actions on a micro-swipe.

## Right (archive / read)

- 15 % → mark read
- 33 % → archive

## Left (unread / silence)

- 15 % → mark unread
- 33 % → silence 7 days (snooze)

## Undo

Each action shows a toast at bottom: "Archived · Undo". You have 5 seconds.

## Sensitivity

Too sensitive / too stiff? Ping `#feedback` — we have dedicated iteration batches. Thresholds were tuned after beta batch #1.

## Temporarily disable

Reading mode (conversation open fullscreen) → no swipe on the list.
