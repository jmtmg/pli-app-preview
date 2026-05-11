# PLI — Étude open-source email/inbox

Date: 2026-05-11 14:51 CEST

Objectif: regarder ce qui existe en open-source autour des clients email, webmails, inbox AI, shared inbox/CRM et infrastructure mail, puis extraire ce qui est utile pour la v1/v2 de PLI.

Sources consultées:

- GitHub Repository API, avant rate-limit non authentifié, pour métriques publiques.
- README/configs publics via `raw.githubusercontent.com`; les extraits bruts temporaires ont été supprimés après synthèse pour éviter de conserver inutilement du contenu tiers ou secret-like.
- Aucun secret utilisateur consulté, copié ou nécessaire.

## Résumé exécutif

Ce qui ressort nettement:

1. Le marché open-source récent part vers des **inbox AI-first**: Inbox Zero, Mail-0/Zero, Cloudflare Agentic Inbox, Alle.
2. Les webmails matures restent très forts sur les fondamentaux: IMAP/SMTP, multi-comptes, search, tags, pièces jointes, plugins, mobile léger.
3. Les meilleurs patterns produit ne viennent pas seulement des clients mail: Chatwoot et Twenty montrent que la valeur se joue dans la **fiche contact**, la **timeline**, les **actions rapides**, les **règles/automations**, et la **priorisation**.
4. Pour PLI, il ne faut pas construire un serveur mail maintenant. Il faut un **client orchestrateur** avec providers officiels Gmail/Microsoft d’abord, puis abstraction IMAP/JMAP/EWS plus tard.
5. La priorité v1 devrait être: OAuth sécurisé, ingestion/sync minimale, index local, actions de tri, règles simples, puis AI opt-in avec garde-fous.

## Projets AI-first à étudier en priorité

### 1. `elie222/inbox-zero`

- URL: https://github.com/elie222/inbox-zero
- Stars observées: 10 655
- Langage principal: TypeScript
- Licence API GitHub: `NOASSERTION`
- État: actif, poussé le 2026-05-11
- Stack README: Next.js, Prisma, turborepo, Docker/Postgres.
- Fonctionnalités README:
  - assistant AI 24/7 pour email;
  - pré-rédaction de réponses dans le ton de l’utilisateur;
  - règles AI en langage naturel;
  - `Reply Zero`: suivi des emails auxquels répondre / en attente de réponse;
  - meeting briefs à partir d’emails + calendrier;
  - classement intelligent de pièces jointes vers Google Drive / OneDrive;
  - intégrations Slack et Telegram.

Leçons pour PLI:

- `Reply Zero` est une excellente tranche PLI: une vue “À répondre / En attente / Relances”.
- Les règles en langage naturel sont séduisantes, mais pour v1 il faut d’abord une base déterministe: règles locales simples + journal d’action.
- L’intégration Telegram est cohérente avec l’écosystème Jm/Hermes: PLI peut produire des briefings et demandes de confirmation dans Telegram.
- Les meeting briefs sont v2, mais l’idée de “brief contact/conversation” est v1 utile.

À éviter/copier avec prudence:

- Ne pas laisser l’AI agir sur les vrais emails sans mode preview/confirmation.
- Ne pas lier calendrier/drive tant que l’OAuth mail n’est pas fiable.

### 2. `Mail-0/Zero`

- URL: https://github.com/Mail-0/Zero
- Stars observées: 10 544
- Langage principal: TypeScript
- Licence: MIT
- État: actif non archivé, dernier push observé 2025-09-04
- README:
  - “Open-Source Gmail Alternative”;
  - self-host;
  - intégration Gmail et autres providers;
  - unified inbox Gmail/Outlook;
  - AI agents / LLMs;
  - privacy-first;
  - stack: Next.js, React, TypeScript, TailwindCSS, shadcn/ui;
  - auth: Better Auth, Google OAuth.

Leçons pour PLI:

- PLI doit se positionner comme “personal inbox productivité” plutôt que webmail générique.
- Le couple `unified inbox + OAuth provider officiel + privacy-first` est le cœur v1.
- shadcn/Radix/Tailwind est la direction UI dominante; PLI a déjà React/Vite et peut reprendre les patterns, pas forcément les dépendances.
- On doit documenter explicitement le modèle de confidentialité: ce qui reste local, ce qui va au provider, ce qui va éventuellement à un LLM.

### 3. `cloudflare/agentic-inbox`

- URL: https://github.com/cloudflare/agentic-inbox
- Stars observées: 2 906
- Langage principal: TypeScript
- Licence: Apache-2.0
- État: actif non archivé, dernier push observé 2026-04-23
- README:
  - email client self-hosted avec agent AI;
  - fonctionne entièrement sur Cloudflare Workers;
  - inbound via Cloudflare Email Routing;
  - mailbox isolée par adresse;
  - agent capable de lire inbox, chercher conversations et rédiger réponses;
  - Cloudflare Agents SDK + Workers AI;
  - setup: R2, Durable Objects, Email Routing, send_email binding, Cloudflare Access.

Leçons pour PLI:

- Très intéressant comme architecture “mailbox isolée + agent outillé”.
- Le modèle `agent peut chercher + rédiger, mais l’interface garde le contrôle` est à reproduire.
- Pour PLI v1, Cloudflare ne doit pas être une dépendance obligatoire, mais peut inspirer une future option “alias/domain catch-all”.
- La sécurité Cloudflare Access montre qu’il faut traiter l’auth comme une couche produit, pas juste un écran login.

### 4. `bestruirui/Alle`

- URL: https://github.com/bestruirui/Alle
- Stars observées: 420
- Langage principal: TypeScript
- Licence: GPL-3.0
- État: actif non archivé
- README:
  - agrégateur email AI;
  - support Gmail, Outlook, QQ Mail;
  - AI extraction d’informations clés;
  - emails temporaires via Cloudflare Workers;
  - stack Next.js, React Query, Drizzle, OpenAI, next-pwa, Cloudflare Workers.

Leçons pour PLI:

- L’extraction structurée depuis email vers actions est pertinente: dates, demandes, factures, PJ, décisions.
- Les emails temporaires/aliases sont plutôt v2.
- Le PWA/mobile est cohérent avec le test téléphone PLI.

## Clients/webmails matures à étudier

### 5. `roundcube/roundcubemail`

- URL: https://github.com/roundcube/roundcubemail
- Stars observées: 6 963
- Langage principal: PHP
- Licence API GitHub: non détectée; README/écosystème Roundcube orienté GPL.
- État: actif, dernier push observé 2026-05-11
- README:
  - client IMAP multilingue dans navigateur;
  - framework propre + librairie IMAP;
  - gros écosystème historique.

Leçons pour PLI:

- Le socle IMAP/folders/messages est incontournable pour provider générique.
- La compatibilité et la sobriété priment sur les effets UI.
- Le plugin model est intéressant plus tard: actions PLI, intégrations, règles.

### 6. `nextcloud/mail`

- URL: https://github.com/nextcloud/mail
- Stars observées: 974
- Langage principal: JavaScript/PHP
- Licence: AGPL-3.0
- État: actif, dernier push observé 2026-05-11
- README:
  - app mail pour Nextcloud;
  - multiples comptes;
  - unified inbox;
  - connecte tout compte IMAP;
  - intégrations Contacts, Calendar, Files, Tasks;
  - Priority Inbox;
  - thread summaries opt-in avec Ethical AI Rating.

Leçons pour PLI:

- Très bon modèle pour “mail + contacts + calendrier + fichiers + tâches”.
- L’AI doit être opt-in, explicable, et notée/qualifiée selon backend utilisé.
- La v1 PLI doit lier contact/conversation/tâches avant d’ajouter trop d’AI.

### 7. `the-djmaze/snappymail`

- URL: https://github.com/the-djmaze/snappymail
- Stars observées: 1 601
- Langage principal: PHP
- Licence: AGPL-3.0
- État: actif non archivé
- README:
  - webmail simple, moderne, léger et rapide;
  - privacy/GDPR friendly;
  - pas de Gravatar, Facebook, Google, Twitter, Dropbox, X-Mailer;
  - pas de user-agent detection, utilise la largeur d’écran;
  - beaucoup de RFC IMAP;
  - thèmes en mobile mode;
  - optimisation mobile et taille bundle.

Leçons pour PLI:

- PLI doit rester léger sur téléphone: charger vite, éviter trackers, pas d’appels externes inutiles.
- Responsive par largeur d’écran, pas par user-agent.
- Privacy/GDPR visible comme argument produit.

### 8. `cypht-org/cypht`

- URL: https://github.com/cypht-org/cypht
- Stars observées: 1 496
- Langage principal: PHP
- Licence: LGPL-2.1
- État: actif, dernier push observé 2026-05-10
- README:
  - “all your email, from all your accounts, in one place”;
  - supports IMAP/SMTP, JMAP, EWS;
  - gère folders IMAP et envoi SMTP;
  - Docker disponible.

Leçons pour PLI:

- Abstraction provider à prévoir dès maintenant: Gmail/Microsoft OAuth d’abord, mais modèle interne compatible IMAP/JMAP/EWS.
- JMAP est probablement la meilleure cible protocole long terme, mais Gmail/Microsoft gagnent v1.

### 9. `Foundry376/Mailspring`

- URL: https://github.com/Foundry376/Mailspring
- Stars observées: 17 463
- Langage principal: JavaScript/Electron
- Licence: GPL-3.0
- État: actif, dernier push observé 2026-05-11
- README:
  - client mail desktop Mac/Windows/Linux;
  - version moderne de Nylas Mail;
  - remplace la sync JS par un moteur local C++ basé sur Mailcore2;
  - sync engine lancé localement par l’app Electron;
  - fonctionnalités: link tracking, read receipts, mailbox analytics, contact/company profiles.

Leçons pour PLI:

- Séparer clairement UI et sync engine est une bonne architecture future.
- Les contact/company profiles confirment la direction fiche contact PLI.
- Link tracking/read receipts sont sensibles: PLI doit les éviter par défaut ou les rendre très explicites.

### 10. `mailpile/Mailpile`

- URL: https://github.com/mailpile/Mailpile
- Stars observées: 8 842
- Langage principal: Python
- Licence: AGPL-3.0+ selon `COPYING.md`
- État: dépôt non archivé mais dernier push observé 2023-11-01
- README:
  - webmail rapide avec chiffrement et privacy;
  - moteur de recherche local conçu pour gros volumes email;
  - tags type Gmail labels;
  - auto-tag incoming mail.

Leçons pour PLI:

- Le vrai avantage durable est l’index local + tags + règles.
- La recherche locale doit rester une priorité backend.
- Chiffrement local et stockage sécurisé sont v1.5/v2, pas premier blocage de v1 démo OAuth.

### 11. `deltachat/deltachat-desktop`

- URL: https://github.com/deltachat/deltachat-desktop
- Stars observées: 1 487
- Langage principal: TypeScript
- Licence: GPL-3.0
- État: actif, dernier push observé 2026-05-11
- README:
  - messagerie privée décentralisée basée sur email;
  - Electron/Tauri;
  - IMAP/SMTP;
  - chaque compte correspond à une DB SQLite distincte.

Leçons pour PLI:

- La vue conversationnelle est naturelle pour certains usages email.
- Séparer les bases par compte est une option forte pour réduire les fuites inter-comptes; PLI utilise déjà `account_id`, mais pourrait isoler davantage les stores réels plus tard.

## Shared inbox, CRM, automation

### 12. `chatwoot/chatwoot`

- URL: https://github.com/chatwoot/chatwoot
- Stars observées: 29 133
- Langage principal: Ruby/Rails + frontend
- Licence API GitHub: `NOASSERTION`; licence hybride/enterprise d’après `LICENSE`.
- État: actif, dernier push observé 2026-05-11
- README:
  - alternative open-source à Intercom/Zendesk/Salesforce Service Cloud;
  - AI agent support “Captain”;
  - omnichannel support desk;
  - canned responses;
  - auto-assignment;
  - teams + automation tools;
  - agent capacity management;
  - contact management avec profils et historique;
  - segments, notes, traduction temps réel.

Leçons pour PLI:

- Pour usage personnel/pro, reprendre: notes contact, historique, snippets/réponses modèles, actions rapides, automatisations simples.
- Ne pas reprendre la complexité support multi-agent maintenant.
- Une future v2 pourrait avoir “delegation/assignment” vers agents Hermes.

### 13. `twentyhq/twenty`

- URL: https://github.com/twentyhq/twenty
- Stars observées: 45 685
- Langage principal: TypeScript
- Licence: principalement AGPL avec fichiers enterprise selon `LICENSE`.
- État: actif, dernier push observé 2026-05-11
- README:
  - alternative open-source à Salesforce, conçue pour AI;
  - stack visible: NestJS, BullMQ, PostgreSQL, React, monorepo/Nx;
  - objets CRM et champs personnalisables;
  - AI agents/chats.

Leçons pour PLI:

- PLI doit faire de la fiche contact un objet central: champs, notes, historique, PJ, statut relationnel.
- Les champs personnalisés sont v2, mais le schéma doit ne pas les rendre impossibles.
- BullMQ/queue pattern rappelle que la sync mail réelle doit être asynchrone, pas dans les requêtes UI.

### 14. `automatisch/automatisch`

- URL: https://github.com/automatisch/automatisch
- Stars observées: 13 837
- Langage principal: JavaScript
- Licence: AGPL-3.0 avec exception enterprise selon `LICENSE`.
- État: actif non archivé
- README:
  - alternative open-source à Zapier;
  - connecte des services pour automatiser des processus;
  - self-hosted, Postgres/Redis via Docker compose.

Leçons pour PLI:

- Les règles PLI doivent pouvoir devenir des workflows: “si email de X avec PJ facture → tag + rappel + export”.
- Mais il faut commencer très simple: règles déterministes internes, pas builder complet.

### 15. `postalserver/postal` et `stalwartlabs/stalwart`

Postal:

- URL: https://github.com/postalserver/postal
- Stars observées: 16 509
- Langage principal: Ruby
- Licence: MIT
- Fonction: plateforme delivery incoming/outgoing email.

Stalwart:

- URL: https://github.com/stalwartlabs/stalwart
- Stars observées: 12 723
- Langage principal: Rust
- Licence README: AGPL v3 badge; API GitHub non détectée dans l’appel initial.
- Fonction: serveur mail/collaboration all-in-one IMAP/JMAP/SMTP/CalDAV/CardDAV/WebDAV.

Leçons pour PLI:

- Ne pas construire ni héberger le serveur mail pour v1.
- JMAP est un protocole important à garder en tête.
- Si PLI devient appliance self-hosted plus tard, Stalwart peut être étudié comme backend mail, mais c’est hors v1.

## Patterns à intégrer dans PLI

### Priorité P0 — nécessaire pour vraie v1

1. OAuth Gmail/Microsoft sécurisé
   - Provider officiel.
   - Pas de secret en repo.
   - Tokens stockés chiffrés/keychain/1Password ou secret store serveur.
   - Refresh/revocation gérés explicitement.

2. Sync minimale asynchrone
   - Ne pas bloquer l’UI.
   - Ingestion messages par compte.
   - Journal de sync.
   - Retry/backoff.
   - Isolation stricte `account_id`.

3. Index local de recherche
   - FTS sur sujet/corps/contact/PJ metadata.
   - Compte obligatoire.
   - Préparer tags/labels.

4. Filtres boîte utiles
   - non lu;
   - avec PJ;
   - en attente de réponse;
   - à répondre;
   - archivé/silencieux;
   - priorité.

5. Composer réel en mode provider
   - Garde-fous autour de CC/CCI/PJ.
   - Preview avant envoi réel.
   - Journal local de l’action.
   - Gestion erreurs provider lisible.

### Priorité P1 — forte différenciation

1. Reply Zero / Follow-up
   - Détecter: “je dois répondre”, “j’attends une réponse”, “relancer”.
   - Vue dédiée simple.

2. Règles locales déterministes
   - `from`, `subject contains`, `has_attachment`, `account`, `label`.
   - Actions: tag, archive, silence, rappel, brouillon.
   - Journal et mode dry-run.

3. Notes contact + timeline
   - Inspiré Chatwoot/Twenty.
   - Notes manuelles.
   - Historique conversations/PJ.
   - Champs rôle/société déjà amorcés.

4. Brief conversation/contact
   - Résumé local/AI opt-in.
   - Affiche sources et confiance.
   - Aucun envoi automatique.

### Priorité P2 — après v1 stable

1. AI agent outillé
   - Recherche conversations.
   - Prépare réponses.
   - Propose actions.
   - Nécessite confirmation pour envoyer/archiver/supprimer.

2. Intégrations calendrier/fichiers
   - Meeting briefs.
   - Classement PJ Drive/OneDrive.
   - Tâches/rappels.

3. Alias/domain catch-all
   - Inspiration Cloudflare Agentic Inbox / Alle.
   - Utile pour privacy et tri automatique.

4. Protocoles étendus
   - IMAP/SMTP générique.
   - JMAP.
   - EWS si besoin entreprise.

## Recommandation de roadmap immédiate PLI

### Tranche 1 — durcissement composer local

- Rejeter/normaliser noms de pièces jointes avec `/` ou `\`.
- Test explicite max 20 PJ.
- Test migration DB existante sans `bcc_emails`.
- Polish erreurs UI/chips/i18n.

Pourquoi: sécurise ce qui vient d’être construit avant d’ajouter un provider réel.

### Tranche 2 — filtres boîte + Reply Zero local

- Filtres: non lu, avec PJ, silencieux, archivé, priorité.
- Vue “À répondre” / “En attente”.
- Données démo déterministes.
- Tests account-scoped.

Pourquoi: valeur produit visible immédiatement, inspirée Inbox Zero/Nextcloud/Chatwoot.

### Tranche 3 — architecture OAuth provider sans secrets

- Interfaces provider Gmail/Microsoft.
- Endpoints mock/local.
- Schéma tokens sans valeurs réelles.
- Journal sync/envoi.
- Erreurs et révocation.

Pourquoi: prépare vraie boîte sans manipuler de secrets tant que les accès officiels ne sont pas prêts.

### Tranche 4 — sync Gmail/Microsoft réelle

- Seulement avec OAuth/app officiel.
- Scope minimal.
- Lecture limitée d’abord.
- Puis envoi réel avec confirmation.

## Notes de prudence licence

- Plusieurs projets pertinents sont AGPL/GPL/hybrides. Pour PLI, il faut éviter de copier du code sans revue licence.
- Étude autorisée: architecture, UX, idées produit, patterns publics.
- Si on intègre du code tiers, il faudra une revue licence explicite avant import.

## Conclusion

PLI est déjà dans la bonne direction: mobile, contact-centric, account-scoped, composer solide, local-first. Les projets open-source confirment que la v1 utile doit maintenant se concentrer sur:

1. vrais providers OAuth;
2. sync/recherche/filtres robustes;
3. Reply Zero / follow-up;
4. règles locales simples;
5. AI opt-in seulement après base mail fiable.

Le meilleur angle différenciant pour PLI: **un client mail personnel/pro orienté décision, relation et action**, pas un webmail générique.
