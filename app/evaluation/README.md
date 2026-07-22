# Avaliação com RAGAS

Avaliação offline da qualidade do RAG usando [RAGAS](https://docs.ragas.io),
com o **Gemini** como juiz (mesmo provider da aplicação — não precisa de OpenAI).

## Métricas

| Métrica | O que mede |
|---|---|
| `faithfulness` | A resposta se baseia no contexto? (detecta alucinação) |
| `answer_relevancy` | A resposta responde de fato a pergunta? |
| `context_precision` | Os chunks recuperados são relevantes? |
| `context_recall` | O retriever trouxe tudo que a resposta correta precisava? |

## Como rodar

1. Instale as dependências **de avaliação** (separadas das de produção, pois o
   RAGAS puxa pacotes pesados que não devem ir pro deploy):
   ```bash
   pip install -r app/evaluation/requirements-eval.txt
   ```

   > **Compatibilidade:** o `ragas 0.4.3` tem um import morto de `ChatVertexAI`
   > (`langchain_community.chat_models.vertexai`), removido na langchain-community
   > 0.4.x. O `app/evaluation/__init__.py` injeta um shim mínimo que resolve isso
   > antes do ragas carregar — você não precisa fazer nada.

2. Garanta que as env vars estão carregadas (as mesmas da app):
   - `GOOGLE_API_KEY` — para o Gemini (LLM juiz + embeddings)
   - `DATABASE_URL` — para o pgvector (retriever)
   - `LANGSMITH_API_KEY` / `LANGCHAIN_API_KEY` — o prompt é puxado do LangSmith Hub

3. Preencha `golden_set.json` com perguntas reais, a resposta esperada
   (`ground_truth`) e o `collection_name` de um documento **já indexado**.
   > O `collection_name` é o mesmo resolvido em `DocumentRepository.resolve_collection`.

4. Rode:
   ```bash
   python -m app.evaluation.run_eval
   ```

   Opções:
   ```bash
   python -m app.evaluation.run_eval --dataset app/evaluation/golden_set.json --workers 2
   ```

## Saída

- Scores agregados no terminal.
- `ragas_results.csv` com o detalhamento por pergunta (útil para achar quais
  perguntas puxaram a média pra baixo).

## Dicas

- **Rate limit (429)**: no free tier do Gemini, comece com poucas perguntas e
  `--workers 1`. Cada amostra faz várias chamadas ao LLM juiz.
- Isto é um job batch/offline — não roda dentro do request do usuário.
