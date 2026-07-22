"""Offline RAGAS evaluation of the RAG pipeline.

Runs the real retriever + prompt + Gemini answering model over a golden set,
then scores the results with RAGAS metrics using Gemini as the judge.

Usage:
    python -m app.evaluation.run_eval
    python -m app.evaluation.run_eval --dataset app/evaluation/golden_set.json --workers 2

This is an offline/batch job. It is intentionally separate from the API and
never runs inside a user request.
"""

import argparse
import asyncio
import json
import logging
from pathlib import Path

from ragas import EvaluationDataset, evaluate
from ragas.dataset_schema import SingleTurnSample
from ragas.metrics import (
    Faithfulness,
    LLMContextPrecisionWithReference,
    LLMContextRecall,
    ResponseRelevancy,
)
from ragas.run_config import RunConfig

from app.evaluation.ragas_config import get_ragas_embeddings, get_ragas_llm
from app.llm.client import get_model
from app.rag.prompt_builder import build_prompt
from app.rag.retriever import retrieve_documents

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

DEFAULT_DATASET = Path(__file__).parent / "golden_set.json"


async def build_sample(item: dict) -> SingleTurnSample:
    """Run the real pipeline for one question and package it for RAGAS."""
    contexts = await retrieve_documents(item["question"], item["collection_name"])
    prompt = await build_prompt(
        question=item["question"],
        context="\n\n".join(contexts),
        history=[],
        user_id=None,
        user_name=None,
    )
    response = await get_model().ainvoke(prompt)
    logger.info("Answered: %s", item["question"])
    return SingleTurnSample(
        user_input=item["question"],
        response=response.content,
        retrieved_contexts=contexts,
        reference=item["ground_truth"],
    )


async def build_dataset(items: list[dict]) -> EvaluationDataset:
    # Sequential on purpose: keeps us under Gemini free-tier rate limits.
    samples = [await build_sample(item) for item in items]
    return EvaluationDataset(samples=samples)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Run RAGAS evaluation.")
    parser.add_argument("--dataset", type=Path, default=DEFAULT_DATASET)
    parser.add_argument("--output", type=Path, default=Path("ragas_results.csv"))
    parser.add_argument(
        "--workers",
        type=int,
        default=2,
        help="Concurrent judge calls. Lower it if you hit rate limits (429).",
    )
    return parser.parse_args()


def main() -> None:
    args = parse_args()

    items = json.loads(args.dataset.read_text())
    dataset = asyncio.run(build_dataset(items))

    llm = get_ragas_llm()
    embeddings = get_ragas_embeddings()
    run_config = RunConfig(max_workers=args.workers)

    result = evaluate(
        dataset=dataset,
        metrics=[
            Faithfulness(llm=llm),
            ResponseRelevancy(llm=llm, embeddings=embeddings),
            LLMContextPrecisionWithReference(llm=llm),
            LLMContextRecall(llm=llm),
        ],
        run_config=run_config,
    )

    print("\n=== RAGAS scores ===")
    print(result)
    result.to_pandas().to_csv(args.output, index=False)
    print(f"\nPer-question breakdown saved to {args.output}")


if __name__ == "__main__":
    main()
