# M4 — Storyboard tour produit 5 étapes

**Propriétaire** : UX · **Copy validée** : PM · **Implémenté dans** : `features/onboarding/Tour.tsx`

---

## Principes

- **Non intrusif** : overlay semi-transparent, pas de blocage complet, Skip toujours accessible.
- **Contextuel** : chaque bulle pointe un élément réel de l'UI (pas des screenshots).
- **Une idée par écran** : pas de pavé, 1-2 phrases max.
- **Pronom "tu"** : cohérent avec le ton PLI (informel, direct, pas infantilisant).
- **Pas d'animation gratuite** : juste un scroll-into-view + focus visible.

---

## Étape 1 · Liste conversations

**Cible** : `[data-tour='conversation-list']`
**Placement bulle** : droite (desktop) / bas (mobile)

| Copy FR | Copy EN |
|---|---|
| **Tes conversations, regroupées par contact** | **Your conversations, grouped by contact** |
| Une entrée = une personne. Tu vois tous ses messages à un endroit, tous comptes confondus. | One entry = one person. See every message from them, across all accounts. |

**Wireframe** :
```
┌────────────────────────────────┐
│ ≡ Inbox                   🔍 ≡ │
├────────────────────────────────┤
│ ● Anne Durand        hier 14h │ ◄── pointed
│   Re: contrat signé          │
│ ● Thomas Ménard      lun 09h  │
│   Propale nov                 │
│ ┌──────────────────────────┐  │
│ │ Tes conversations,       │  │
│ │ regroupées par contact.  │  │
│ │ Une entrée = une personne│  │
│ │ … [Passer]   [Suivant]   │  │
│ └──────────────────────────┘  │
└────────────────────────────────┘
```

---

## Étape 2 · Filtres Humains / Notifs

**Cible** : `[data-tour='filters']`
**Placement** : bas

| Copy FR | Copy EN |
|---|---|
| **Humains ou notifs ?** | **Humans or noise?** |
| Filtre d'un geste les vraies conversations des newsletters et notifications automatiques. | One tap filters out real conversations from newsletters and automated notifications. |

**Wireframe** :
```
┌────────────────────────────────┐
│ [Humains] [Notifs] [Tous]  🔍 │ ◄── pointed
│ ┌──────────────────────────┐  │
│ │ Humains ou notifs ?      │  │
│ │ Filtre d'un geste…       │  │
│ │ [Passer]   [Suivant]   2/5│  │
│ └──────────────────────────┘  │
└────────────────────────────────┘
```

---

## Étape 3 · Swipe

**Cible** : `[data-tour='swipe-card']`
**Placement** : gauche

| Copy FR | Copy EN |
|---|---|
| **Glisse pour agir** | **Swipe to act** |
| Swipe à droite pour archiver, à gauche pour marquer non lu. Deux seuils selon la distance. | Swipe right to archive, left to mark unread. Two thresholds based on distance. |

**Wireframe** :
```
      ┌──────────────────────────┐
      │ Glisse pour agir         │
      │ Droite = archive         │
      │ Gauche = non lu          │
      │ [Passer]  [Suivant] 3/5  │
      └──────────────────────────┘
◄─[archive] ● Anne Durand ◄──┤ [non lu]─►
```

---

## Étape 4 · Composer

**Cible** : `[data-tour='composer-fab']`
**Placement** : haut

| Copy FR | Copy EN |
|---|---|
| **Écris, envoie** | **Write, send** |
| Le composer s'étend à mesure que tu tapes. Brouillon auto sauvegardé toutes les 2 s. | The composer expands as you type. Drafts auto-save every 2 s. |

---

## Étape 5 · Recherche

**Cible** : `[data-tour='search-fab']`
**Placement** : bas

| Copy FR | Copy EN |
|---|---|
| **Cherche partout, vite** | **Search anywhere, fast** |
| Recherche plein-texte sur tous tes comptes. Moins de 300 ms sur 10 000 messages. | Full-text search across all accounts. Under 300 ms on 10,000 messages. |

**CTA final** : bouton "C'est parti" / "Let's go" (au lieu de "Suivant").

---

## Variantes copy à tester (itération #1 si besoin)

Si rétention tour < 60 % en batch #1, tester ces variantes :

### Variante A — Plus courte

> **Tes conversations, par contact** · Une entrée par personne, multi-comptes.

### Variante B — Orientée bénéfice

> **Une boîte plus calme** · Tu vois d'abord les personnes, les machines ensuite.

---

## Accessibilité

- Chaque bulle : `role="dialog"` + `aria-labelledby`
- Navigation clavier : Tab / Enter / Esc (= Skip)
- Contraste bouton primaire : AA minimum (noir sur blanc, #000 / #FFF)
- Taille minimum touch target : 44 × 44 px

---

## Métriques de succès tour

| Métrique | Cible M4 | Seuil alerte |
|---|---|---|
| Tour start rate (affiché / activés) | > 95 % | < 85 % |
| Tour complete rate (finish / start) | > 60 % | < 40 % |
| Skip rate à l'étape 1 | < 15 % | > 30 % |
| Temps médian tour complet | 35-60 s | > 120 s |

---

*Storyboard validé par UX + PM + Founder le 10 août 2026.*
