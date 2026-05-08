"""PLI backend — client mail conversationnel.

Architecture :
- `main` : entrypoint FastAPI
- `config` : settings (mode Local vs Cloud)
- `db` : connexion SQLite + chargement FTS5
- `models` : modèles de domaine Pydantic
- `providers/*` : adapters Gmail / Microsoft Graph (pattern Strategy)
- `sync/*` : orchestration sync incrémentale
- `api/*` : routers REST
"""

__version__ = "0.1.0-m1"
