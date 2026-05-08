"""DEPRECATED — ce module est shadow par le package `pli/crypto/`.

Le contenu (get_crypto, encrypt_str, decrypt_str) a migre dans
`pli/crypto/oauth.py` et est re-expose depuis `pli.crypto` via son
`__init__.py`. Ce fichier reste en place comme marqueur ; Python prefere
toujours un package a un module du meme nom, donc ce code n'est jamais
importe.

A supprimer lors du prochain nettoyage (ADR backlog "repo hygiene").
"""
