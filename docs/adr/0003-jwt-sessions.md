# ADR 0003 — JWT access + refresh tokens avec rotation

**Statut** : Accepté · **Date** : 2026-06-26 · **Auteurs** : SEC + BE

## Contexte

Sessions Cloud nécessaires (M2) : équilibrer sécurité (révocation rapide, détection vol de token) et UX (pas de re-login fréquent).

## Décision

**Access JWT court (15 min) + refresh opaque long (30 j) avec rotation.**

- Access : signé HS256, contient `sub`, `email`, `plan`, `jti`, `exp`, `nbf`. Stocké côté client (mémoire React, jamais localStorage).
- Refresh : 384 bits aléatoire, opaque, stocké hashé SHA-256 en DB (table `user_sessions`). Transit en cookie httpOnly + SameSite=Lax + Secure, scope `/auth`.
- Rotation : chaque `/auth/refresh` invalide l'ancien et émet un nouveau. Si un refresh déjà rotaté est réutilisé → vol détecté → toutes les sessions du user sont révoquées.
- Révocation access : table `revoked_access_jti` (TTL ≤ exp du token).

## Alternatives écartées

- Sessions opaques côté serveur uniquement (Redis) : ajoute une dépendance et un point de panne pour M2.
- JWT auto-suffisant sans rotation : impossible de révoquer rapidement.

## Conséquences

Logout = invalidation côté serveur immédiate.
Performances : `/auth/refresh` rare (toutes les 15 min max), pas de pression DB.

## Validation

Tests `test_auth_flow.py` couvrent : signup → login → access → refresh rotation → logout → reuse refresh → toutes sessions révoquées.
