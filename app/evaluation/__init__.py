"""Evaluation package.

Compatibility shim: ragas 0.4.3 still imports `ChatVertexAI` from
`langchain_community.chat_models.vertexai` at module load time, but that
submodule was removed in langchain-community 0.4.x (the project runs on
LangChain 1.x). We inject a lightweight placeholder before ragas is imported
so `import ragas` succeeds. ragas only needs the symbol to exist for isinstance
checks against Vertex models, which we never use (our judge is Gemini).

This runs first because Python imports the parent package before executing
any submodule (e.g. `python -m app.evaluation.run_eval`).
"""

import sys
import types

from dotenv import load_dotenv

# Eval scripts are standalone entrypoints that don't go through app.main /
# app.core.config, so nothing loads the .env before app.db.session reads
# DATABASE_URL at import time. Load it here, before any app import runs.
load_dotenv()

_MISSING = "langchain_community.chat_models.vertexai"
if _MISSING not in sys.modules:
    _shim = types.ModuleType(_MISSING)

    class ChatVertexAI:  # placeholder; unused, only satisfies ragas' import
        pass

    _shim.ChatVertexAI = ChatVertexAI
    sys.modules[_MISSING] = _shim
