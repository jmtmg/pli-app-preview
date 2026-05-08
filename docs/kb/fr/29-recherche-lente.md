# Recherche lente

## Ce qui est normal

- **1-30 k messages** : < 200 ms, instantané ressenti
- **30-200 k messages** : 200-600 ms, ressenti légèrement différé
- **> 200 k messages** : 600-1500 ms, "un peu long"

Si tu es au-delà de ces ordres de grandeur → problème, lire la suite.

## Causes fréquentes

### Index FTS5 corrompu (Local)

Ça peut arriver après un crash disque ou une mise à jour interrompue.

→ Réglages → **Maintenance** → **Reconstruire l'index de recherche**. 2-15 min selon volume. Pas d'impact sur tes données.

### Cache froid (Cloud)

Au premier hit après longtemps d'inactivité, le cache Postgres est froid. Attends 2-3 requêtes, ça accélère.

### Trop de filtres combinés

"Humains + Non lus + Avec PJ + date + terme" = cartesian product. PLI simplifie mais garde une recherche rapide en simplifiant. Essaie **un filtre à la fois** d'abord.

### Query trop large

`a` ou `de` → la base doit scanner beaucoup. PLI bloque les tokens < 3 caractères d'office, mais pense à affiner.

## Accélérateurs

- **Syntaxe avancée** : `from:alice@acme.com subject:contrat` → l'index adore les opérateurs
- **Scope** : restreindre à un compte si tu en as plusieurs
- **Période** : `after:2025-01-01` divise par N la zone de recherche

## Si tu tombes sur un truc vraiment lent

[Support](30-support.md) avec ta requête exacte + volume approximatif. Ça nous aide à prioriser l'optim' (on a des alertes pli_search_p95_seconds côté SRE — c'est suivi).
