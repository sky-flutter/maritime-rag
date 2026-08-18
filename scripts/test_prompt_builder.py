from app.prompt.prompt_builder import PromptResult
from app.retrieval.factory import get_retriever, get_query_analyzer
from app.retrieval.retriever import RetrievalQuery
from app.prompt.grounded_prompt_builder import GroundedPromptBuilder


def main() -> None:
    retriever = get_retriever()
    query_analyzer = get_query_analyzer()

    user_question = (
        "Get the consumption of vessel 1019462 dated on 2026-06-22 23:12:00.000 Z"
    )

    analysis = query_analyzer.analyze(user_question)

    print(
        f"Extracted: {analysis.metadata_filter}, "
        f"Range: {analysis.datetime_from} to {analysis.datetime_to}"
    )

    query = RetrievalQuery(
        text=analysis.original_text,
        top_k=5,
        metadata_filter=analysis.metadata_filter,
        datetime_from=analysis.datetime_from,
        datetime_to=analysis.datetime_to,
    )
    results = retriever.retrieve(query=query)
    prompt_builder = GroundedPromptBuilder()
    prompt_result: PromptResult = prompt_builder.build(user_question, results)

    print("=== SYSTEM PROMPT ===")
    print(prompt_result.system_prompt)
    print("\n=== USER PROMPT ===")
    print(prompt_result.user_prompt)
    print("\n=== SOURCE MAP ===")
    for excerpt_id, chunk in prompt_result.source_map.items():
        print(f"[{excerpt_id}] -> chunk_id={chunk.chunk_id}")


if __name__ == "__main__":
    main()
