---
type: email
audience: Liste d'attente beta privée + inscrits newsletter pli.app
subject_fr: "PLI est ouvert en beta publique — essayez 14 jours"
subject_en: "PLI public beta is open — try it for 14 days"
send_target_date: TBD (Sprint 11 J6 cible = 2026-09-16, sous réserve FV direction)
status: draft
---

> **🚫 NE PAS ENVOYER.**
> Cet email est un draft. Aucun envoi externe avant :
> 1. Bascule effective `public_signup_enabled=true` (Sprint 11 J6, 08h00 CET)
> 2. Validation Checkpoint 11a Go/No-Go ouverture (Sprint 11 J5)
> 3. `statut=approved` dans `../publications-log.md` ligne `E-01`, signé direction.
> Toute ligne contenant `{placeholder}` reste à remplir avec une valeur **mesurée sur binaire intégré**.

---

## Version FR (principale)

**Objet** : PLI est ouvert en beta publique — essayez 14 jours

---

Bonjour,

Vous êtes inscrit·e à la liste de PLI — soit parce que vous avez demandé à tester avant tout le monde, soit parce que vous suivez le projet de loin. Merci d'avoir patienté.

Ce matin, j'ouvre PLI en **beta publique**. Vous pouvez créer un compte sans invitation, connecter Gmail ou Microsoft 365, et essayer 14 jours gratuitement sans carte bancaire.

**Lien direct** : https://pli.app/signup

Ce que PLI fait aujourd'hui :

- Regroupe vos emails par contact, pas par thread
- Propose un mode **Local** (vos emails restent chez vous, chiffrés) ou **Cloud** (hébergé en France)
- Recherche plein texte rapide, filtres Humains / Notifs, swipe bilatéral sur mobile
- Export et suppression de compte en 1 clic (RGPD conforme)

Ce que PLI **ne fait pas encore** :

- Pas d'IA assistant
- Pas d'app native iOS/Android (PWA seulement)
- Pas de calendrier ni de boîte partagée

Pendant 14 jours vous pouvez tout tester. Dites-moi ce qui ne va pas — widget in-app, Discord, ou en réponse à cet email.

Si PLI ne résout pas votre problème, vous pouvez vous désabonner en 1 clic tout en bas. Pas de rancune.

— Jean-Marie
Founder PLI

*PS : article long format "Pourquoi PLI — et pourquoi maintenant" disponible ici → {url_blog_fr}*

---

## Version EN (miroir)

**Subject** : PLI public beta is open — try it for 14 days

---

Hi,

You're on the PLI mailing list — either because you asked for early access or because you've been following along. Thanks for being patient.

This morning I'm opening PLI in **public beta**. You can create an account without invitation, connect Gmail or Microsoft 365, and try it for 14 days, no credit card required.

**Direct link**: https://pli.app/signup

What PLI does today:

- Groups your emails by contact, not by thread
- Offers a **Local** mode (your emails stay on your device, encrypted) or **Cloud** (hosted in France)
- Fast full-text search, Humans / Notifications filters, two-way swipe on mobile
- 1-click export and account deletion (GDPR-compliant)

What PLI **doesn't do yet**:

- No AI assistant
- No native iOS/Android app (PWA only)
- No calendar, no shared inbox

For 14 days you can test everything. Tell me what's broken — in-app widget, Discord, or by replying to this email.

If PLI doesn't solve your problem, unsubscribe in 1 click at the bottom. No hard feelings.

— Jean-Marie
Founder, PLI

*PS: long-form article "Why PLI — and why now" here → {url_blog_en}*

---

## Meta-draft — à retirer avant envoi

**Checklist envoi (CONT + direction)** :

- [ ] Feu vert direction écrit dans `../publications-log.md` ligne E-01
- [ ] Flag `public_signup_enabled=true` bien actif depuis 08h00 CET
- [ ] Smoke tests US-11.9 verts depuis 48 h
- [ ] URL blog FR/EN finalisées, publiées avant envoi (ordre : blog puis email, jamais l'inverse)
- [ ] Lien désabonnement en pied vérifié (conformité RGPD)
- [ ] Headers anti-spam SPF/DKIM/DMARC validés sur le domaine d'envoi
- [ ] Test d'envoi à 10 boîtes internes (Gmail, Outlook, iCloud, ProtonMail) : inbox primary, pas spam
- [ ] Rate d'envoi limité (< 100/min) pour éviter blacklist
- [ ] Version EN envoyée en parallèle sur segment EN uniquement
- [ ] Retirer ce bloc "Meta-draft" avant envoi

**Historique** :

- 2026-04-22 : création du draft (session M5, T5.2). Pas d'envoi autorisé.
