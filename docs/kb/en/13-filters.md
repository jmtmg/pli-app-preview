# Filters Humans / Notifs / All

The **Humans / Notifs** distinction is a PLI core principle.

## How PLI classifies

Algorithmically (no sensitive ML — a transparent heuristic):

- Generic sender name (`noreply@`, `notifications@`, `updates@`) → Notifs
- Bulk-send domain (Mailgun, SendGrid, etc.) + no personal greeting → Notifs
- `List-Unsubscribe` header present → Notifs
- Otherwise → Humans

You can **force a sender's category** via `⋯` on their contact card.

## The golden rule

Go through **Humans first**. Notifs are consultable when you have time, not for interrupting you.

## Complementary filters

- **Unread**: only things to read
- **With attachment**: messages with attachments
- **All**: everything, no filter

## Combining

Filters stack: "Humans + Unread + With attachment" is valid and useful for a Monday morning catch-up.

## Custom rules (V1.2)

Advanced rules ("anything from @client.com → pinned"): not in V1. Scheduled V1.2 based on user feedback.
