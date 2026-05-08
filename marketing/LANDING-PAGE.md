# Landing page pli.app — Plan de contenu M4

**Owner** : MKT
**Tech** : Next.js 14 statique, hosting Vercel EU, i18n FR/EN
**Version** : M4 (waitlist) → évolue en M5 (checkout actif)

## Objectif par page

- **/** (hero) : convertir visiteur → waitlist, ou visiteur → retour trial s'il a déjà un compte
- **/invited** : landing pour les batches invités (clé d'invitation pré-remplie)
- **/privacy** : politique de confidentialité (légal)
- **/security** : posture sécurité détaillée (pour l'admin Microsoft ou sceptiques)
- **/press** : kit presse (téléchargeable)
- **/blog/beta-ouverte** : post annonce (SEO + RP)

---

## Structure page `/` (home)

### Section Hero

**Above the fold** :

- H1 FR : **"L'email redevient humain."**
- H1 EN : **"Email becomes human again."**
- Sous-titre FR : *"Un client mail qui sépare ce qui mérite ta réponse de ce qui mérite d'attendre. Local ou cloud européen. Jamais vendu."*
- Sous-titre EN : *"An email client that separates what deserves your reply from what deserves to wait. Local or EU cloud. Never sold."*
- CTA primaire : **Rejoindre la waitlist** (ouvre modal `/waitlist`)
- CTA secondaire : **Voir la démo 45 s** (lightbox vidéo landing)
- Vidéo muette autoplay en arrière-plan droite (cf. STORYBOARD-LANDING.md)
- Trust badges sous CTA : "🇪🇺 Hébergé UE" · "🔒 Chiffré" · "🚫 Pas de pub"

### Section "Pourquoi PLI"

3 blocs côte à côte :

1. **Humains vs Notifs** — mockup UI en gros, 2-3 phrases explicatives
2. **Local ou Cloud** — schéma 2 colonnes (icône device vs icône serveur UE)
3. **Zéro surveillance** — bullet points : pas de pub, pas de tracking, RGPD natif, export 1 clic

### Section "Comment ça marche"

Timeline 4 étapes avec illustrations :

1. Rejoins la waitlist
2. Reçois ton code d'invitation
3. Connecte Gmail ou Microsoft (30 s)
4. Utilise 60 s après

### Section "Ce qu'ils disent" (social proof)

En M4, on n'a pas encore de testimonials utilisateurs. On met :

- 3 citations de beta users (placeholders jusqu'à J+14 de M4 puis rempli avec vrais verbatims)
- Logos "As featured in" : ProductHunt (à J-M5), Maddyness, Frenchweb

⚠️ **Règle** : pas de fake testimonials. Si pas de citation réelle, section cachée jusqu'à J+14 M4.

### Section pricing (preview)

Tableau 2 colonnes : Cloud / Plus. Prix mensuel prominent. Lien "Voir tous les plans" → `/pricing` (M5).

### Section FAQ

10 questions les plus courantes depuis la waitlist + fin de trial :

1. C'est qui JMJ Consulting ?
2. Pourquoi pas IMAP ?
3. Mes emails Gmail vont bouger ?
4. Vous entraînez une IA dessus ?
5. Ça marche sur mobile ?
6. Combien de temps pour basculer de Apple Mail ?
7. Vos tarifs incluent la TVA ?
8. Vous supportez les boîtes pro Microsoft ?
9. Open source ?
10. Que se passe-t-il si vous coulez ?

Chaque réponse 3-5 lignes max. Lien vers KB si plus de détail.

### Section "L'équipe"

Photo team + 2 lignes sur JM et JMJ Consulting. Objectif : humaniser et rassurer "on sait qui sont les gens derrière".

### Footer

- Mentions légales, CGU, Confidentialité, Sécurité
- Contact : hello@pli.app, press@pli.app, security@pli.app
- Statut : [status.pli.app](https://status.pli.app)
- Réseaux : LinkedIn, Mastodon, Bluesky (pas X/Twitter — decisions sécurité/valeurs)
- Logo + "© 2026 JMJ Consulting"

---

## Structure page `/invited`

Landing spéciale batch invités. URL : `pli.app/invited?code=XXXXX`.

- H1 : "{{firstname}}, tu as ta place dans la beta PLI."
- Sous-titre : "Voici ton code d'invitation (expire dans X jours)"
- Bloc code invitation pré-rempli + bouton **Activer mon compte**
- Rappel charte Discord ([DISCORD-CHARTER.md](../community/DISCORD-CHARTER.md))
- Lien "Qu'est-ce que la beta PLI" → section courte

---

## SEO

- Title : "PLI — Email client EU-hosted, privacy-first | JMJ Consulting"
- Meta description : 160 chars — EN par défaut, FR sur domaine.fr
- OG image : 1200×630, logo + baseline
- Canonical : https://pli.app (HTTPS only)
- robots.txt : allow all
- sitemap.xml : généré par Next.js
- Schema.org : Organization + SoftwareApplication

## Conversion tracking

- Plausible Analytics (pas Google — choix data)
- Événements : `waitlist_submit`, `trial_clicked`, `demo_play`, `pricing_scroll`
- Pas de pixel Facebook, pas de pixel LinkedIn, pas de TikTok pixel

## Performance

- Lighthouse score cible : Performance >90, Accessibility >95, SEO >95
- Images en WebP + AVIF
- Fonts self-hosted (pas Google Fonts, RGPD friendly)
- Pas de JS tiers bloquant

## A/B test post-launch

À exécuter en M5 quand volume suffisant (>1 000 visiteurs/jour) :

- Variant hero H1 : "L'email redevient humain." vs "Le mail, mais utile."
- Variant CTA primaire : "Rejoindre la waitlist" vs "Essai gratuit 14 j"
- Variant trust badges : texte vs icônes seules
