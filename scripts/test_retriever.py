from app.retrieval.factory import get_retriever, get_query_analyzer
from app.retrieval.retriever import RetrievalQuery


def main() -> None:
    retriever = get_retriever()
    query_analyzer = get_query_analyzer()

    # "Get the consumption of vessel 1019462 dated on 2026-06-22 23:12:00.000 Z"
    # How rough was the sea for vessel 1019462 on 2026-06-22?
    # How much fuel is remaining on board for vessel 1019462 on 2026-03-19 04:00:00+00?
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

    print(f"Top {len(results)} results: \n")
    for r in results:
        print(f"[{r.similarity_score:.4f}] chunk id = {r.chunk_id}, report={r.report_id} | {r.content}")
        print(f"  metadata: {r.metadata}\n")


if __name__ == "__main__":
    main()
