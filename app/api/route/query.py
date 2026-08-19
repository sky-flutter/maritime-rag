from fastapi import APIRouter, Depends

from app.api.dependencies import (
    get_query_analyzer_dep,
    get_retriever_dep,
    get_llm_service_dep,
    get_prompt_builder_dep,
)
from app.api.schemas import QueryRequest, QueryResponse, SourceResponse
from app.llm.models import Answer
from app.llm.openai_llm_service import OpenAILLMService
from app.prompt.prompt_builder import PromptBuilder
from app.retrieval.query_analyzer import QueryAnalyzer
from app.retrieval.retriever import RetrievalQuery, Retriever


router = APIRouter()


@router.post("/query", response_model=QueryResponse)
def query(
    request: QueryRequest,
    analyzer: QueryAnalyzer = Depends(get_query_analyzer_dep),
    retriever: Retriever = Depends(get_retriever_dep),
    prompt_builder: PromptBuilder = Depends(get_prompt_builder_dep),
    llm_service: OpenAILLMService = Depends(get_llm_service_dep),
) -> QueryResponse:
    analysis = analyzer.analyze(request.question)
    retreival_query = RetrievalQuery(
        text=analysis.original_text,
        datetime_to=analysis.datetime_to,
        datetime_from=analysis.datetime_from,
        top_k=request.top_k,
        metadata_filter=analysis.metadata_filter,
    )
    retrieved_chunks = retriever.retrieve(retreival_query)
    prompt_result = prompt_builder.build(request.question, retrieved_chunks)

    answer: Answer = llm_service.generate_answer(prompt_result)

    sources = [
        SourceResponse(
            report_id=source.report_id,
            chunk_id=source.chunk_id,
            section=source.metadata.get("section", None),
            similarity_score=source.similarity_score,
        )
        for source in answer.sources
    ]
    return QueryResponse(
        answer=answer.text, answered=answer.answered, source_ids=sources
    )
