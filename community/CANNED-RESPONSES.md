# Canned responses — Discord & support PLI

**Usage** : réponses réutilisables pour l'équipe CONT pendant M4. Personnalise toujours par le prénom + adapte au ton. Ces templates évitent le copier-coller robotique mais garantissent la cohérence.

---

## #help — questions d'usage

### CR-01 — Connexion Gmail KO

Salut {{firstname}} 👋

Si tu as `invalid_grant` ou `token_expired`, ton OAuth est cassé côté Google. La réparation prend 30s :

1. Réglages → Comptes → ton Gmail → **Reconnecter**
2. Re-accepte les permissions Google
3. Sync redémarre toute seule

Si l'erreur est différente (`quota_exceeded`, `admin_policy_enforced`, etc.), jette un œil à https://pli.app/docs/fr/26-sync-gmail-ko — on y a listé les plus fréquentes.

Ça marche ? Si toujours KO, partage le code d'erreur et ton user-id (Réglages → About → Copier infos diag), je regarde.

### CR-02 — Recherche lente

Hello {{firstname}} !

Deux pistes rapides :

1. **Reconstruire l'index** (Réglages → Maintenance → Reconstruire index recherche) — 2-15 min, tes data restent intactes
2. **Requête trop large** : ajoute `from:` ou `after:2025-01-01` pour aider l'index

Plus de détails → https://pli.app/docs/fr/29-recherche-lente

Si ça persiste après reconstruction, dis-moi le volume de ta boîte (approx messages) et un exemple de requête, on regarde côté backend.

### CR-03 — Tour non lancé

Coucou {{firstname}},

Le tour produit se lance au premier login uniquement. Pour le relancer : **Réglages → Apparence → Rejouer le tour** 🎬

Dis-moi si tu ne vois pas l'option, il y a eu un bug chez une beta user la semaine dernière — un refresh F5 suffit en général.

### CR-04 — Swipe trop sensible

Salut {{firstname}},

Les seuils de swipe sont 15 % (léger) et 33 % (définitif) — détail : https://pli.app/docs/fr/14-swipe

Si c'est encore trop sensible sur ton device, dis-moi :

- Navigateur + OS
- Trackpad ou souris ou écran tactile

On a un batch d'ajustement prévu iteration #2 (sprint 10), ton retour est précieux.

---

## #feedback — bug

### CR-10 — Ack bug reçu

Merci {{firstname}} 🙏 — bien reçu. On tag ça en BUG-{{severity}} et on te revient sous 24 h avec un statut (reproductible / pas encore / priorisé).

Si tu as une capture ou le user-id de diagnostic, ajoute-les en commentaire, ça accélère.

### CR-11 — Bug fixé, release imminente

Hey {{firstname}}, **fix en route** 🎉

On a ajouté le correctif dans la release de vendredi (10h CET). Ping-nous après pour confirmer que ça marche chez toi. Merci d'avoir remonté — sans ton rapport on serait passé à côté.

### CR-12 — Bug pas reproduit

Salut {{firstname}},

On n'arrive pas à reproduire de notre côté 😕 Pour nous aider :

1. **Étapes exactes** depuis un état propre (refresh puis actions)
2. **Capture ou vidéo** si possible (OBS / QuickTime / intégré Windows)
3. **Infos système** : Réglages → About → Copier diag
4. **Est-ce que ça arrive à chaque fois** ou sporadique ?

Sans repro, difficile de fixer — on te remercie d'avance pour le temps passé à debugger avec nous.

### CR-13 — Bug hot-fixable

Urgent reçu {{firstname}}. On met un hot-fix en prod **aujourd'hui** (si possible, sinon demain matin max). Je te tag dès que c'est live.

---

## #feedback — feature request

### CR-20 — Ack feature idée

Top idée {{firstname}} ✨ On l'ajoute au board de priorisation. Triage en équipe tous les lundis, je reviens vers toi avec l'arbitrage (on ne promet pas que ça sort en M4 — on gèle le backlog pendant la beta, voir notre ADR-006 — mais ça peut partir pour V1.1 / V1.2).

### CR-21 — Feature déjà en backlog

Hey {{firstname}}, super qu'on partage la même priorité 🤝

C'est déjà sur notre board sous l'id **{{id}}**. Priorité actuelle **{{priorité}}**. Shipping estimé **{{date}}**.

Tu peux voter dans `#vote` quand on fait les tours de prio, plus y'a de votes plus ça remonte.

### CR-22 — Feature hors scope

Merci {{firstname}} pour la suggestion.

On l'a regardée et, franchement, elle sort du scope PLI pour V1 : {{raison — ex : "ajouter un calendar complet demanderait un trimestre de dev et ce n'est pas notre positionnement produit"}}.

On note ton retour, on regardera si la demande revient souvent. Pour l'instant on reste focus sur {{ce qui est prioritaire}}.

---

## Onboarding beta

### CR-30 — Bienvenue batch fraîchement arrivé

Bienvenue {{firstname}} 🎉

Tu fais partie du **batch {{batch_number}}** de la beta PLI. 25 personnes. Voilà ce que tu peux faire tout de suite :

1. Jette un œil à [la charte Discord](charter link) — 2 min, on en a besoin pour que ça roule
2. Ouvre PLI, connecte ton compte mail, le tour te guide
3. Post dans `#help` au premier pépin, dans `#feedback` dès que tu vois quelque chose à améliorer

La beta dure **4 semaines** (releases vendredi 10h CET). À J+14 et J+30 on te demandera un NPS (1 minute). Merci d'avance de jouer le jeu — ton feedback oriente ce que PLI devient.

### CR-31 — Rappel NPS J+7

Salut {{firstname}} 👋

Petite minute pour nous aider à calibrer la suite ? On pose UNE question :

**Sur 0 à 10, quelle probabilité que tu recommandes PLI à un ami ?**

Réponds directement dans PLI (un widget apparaît en haut à droite) ou en DM si tu préfères. Que tu mettes 3 ou 9, c'est utile. Les 3 nous pique plus, mais c'est comme ça qu'on s'améliore.

---

## Sortie / fin trial

### CR-40 — Fin beta + choix upgrade

Hey {{firstname}},

**La beta s'est terminée le 9 septembre**. Merci pour ton accompagnement — PLI n'existe pas sans vous.

Ce qui se passe maintenant :

- Ton compte passe en trial commercial 14 jours (pas de rupture).
- Si tu veux continuer ensuite, **-50 % à vie** sur Cloud ou Plus (promesse beta). Code dans ton mail de fin de beta.
- Si tu veux partir, Réglages → Confidentialité → Supprimer compte. Aucune data perdue côté Gmail/Microsoft.

On a aimé te rencontrer. À bientôt peut-être en tant que user commercial 💛

### CR-41 — Demande annulation

Pas de souci {{firstname}}, annuler est ton droit.

Trois options :

1. **Annuler l'abo** (accès jusqu'à fin de période payée) → Réglages → Abonnement → Annuler
2. **Exporter tes data avant** → Réglages → Confidentialité → Exporter (voir https://pli.app/docs/fr/24-export-rgpd)
3. **Supprimer complètement** → Réglages → Confidentialité → Supprimer compte (voir https://pli.app/docs/fr/25-supprimer-compte)

Tu peux revenir quand tu veux — ton email reste reconnu, les réglages aussi, juste la data purgée après 30 j. Tes mails Gmail/Microsoft sont intacts quoi qu'il arrive.

Si tu as 30 secondes pour me dire **pourquoi** tu arrêtes, je preneur — c'est ce qui nous fait avancer.

---

## Modération

### CR-90 — Rappel charte (soft)

Hey {{firstname}}, juste un petit rappel : la règle {{numero}} de la charte ({{rappel court}}). Pas grave du tout, juste pour que le serveur reste cool pour tout le monde 🙂

### CR-91 — Avertissement ferme

{{firstname}}, le message précédent enfreint la règle {{numero}} de la charte ({{règle}}). **1er avertissement** officiel.

Prochaine infraction = ban 7 j. Si tu penses que c'est une erreur, DM-moi, on en discute calmement.

### CR-92 — Ban notification

{{firstname}}, suite au rappel {{date}} et à la nouvelle infraction aujourd'hui, on applique un **ban de 7 jours** (règle {{numero}}).

Tu pourras revenir le {{date_retour}}. D'ici là, si tu veux discuter, c'est hello@pli.app.

---

## Sécurité

### CR-80 — Escalade sécurité

Merci {{firstname}} — c'est pris au sérieux 🔒

J'escalade à notre équipe sécurité (SEC). Si tu as identifié une faille exploitable, merci de :

1. Ne pas la publier publiquement le temps qu'on regarde
2. Envoyer les détails à security@pli.app (PGP dispo sur demande)
3. Attendre 14 j — on te revient avec statut + crédit public si tu le souhaites

Notre politique : https://pli.app/security/disclosure
