from app.prompt.prompt_builder import PromptBuilder, PromptResult
from app.vectorstore.models import RetrievedChunk


SYSTEM_PROMPT = """You are an assistant answering questions about maritime vessel voyage reports.

Rules you must follow strictly:
1. Answer ONLY using the numbered context excerpts provided below. Do not use any
   outside knowledge, even if you're confident it's correct.
2. If the provided context does not contain enough information to answer the
   question, you MUST set "answered" to false and explain what's missing in
   "answer" — do not guess or fill gaps from general knowledge.
3. Every claim in your answer must be traceable to specific excerpt numbers.
   List every excerpt number you actually used in "source_ids".
4. If you use no excerpts, "source_ids" must be an empty list.

Respond only in the structured JSON format requested — no extra commentary.
"""

RESPONSE_SCHEMA = {
    "type": "object",
    "properties": {
        "answered": {
            "type": "boolean",
            "description": "True if the context was sufficient to the question.",
        },
        "answer": {
            "type": "string",
            "description": (
                "The answer, grounded strictly in the provided excerpts. If"
                "answered if false, explain what information is missing instead"
            ),
        },
        "source_ids": {
            "type": "array",
            "items": {"type": "string"},
            "description": "Excerpts numbers (as strings) actually used to construct the answer",
        },
    },
    "required": ["answered", "answer", "source_ids"],
    "additionalProperties": False,
}


class GroundedPromptBuilder(PromptBuilder):
    def _format_excerpt(self, excerpt_id: str, chunk: RetrievedChunk) -> str:
        imo = chunk.metadata.get("imo", "unknown")
        voyage_nr = chunk.metadata.get("voyage_nr", "unknown")
        datetime_gmt = chunk.metadata.get("datetime_gmt", "unknown")
        section = chunk.metadata.get("section", "unknown")

        header = (
            f"[{excerpt_id}] Vessel IMO: {imo} | Voyage: {voyage_nr} | "
            f"Report datetime: {datetime_gmt} | Section: {section}"
        )

        return f"{header}\n{chunk.content}"

    def build(self, question: str, chunks: list[RetrievedChunk]) -> PromptResult:
        source_map: dict[str, RetrievedChunk] = {
            str(i + 1): chunk for i, chunk in enumerate(chunks)
        }

        if not chunks:
            context_block = "(No relevant excerpts were found for this question)"
        else:
            context_block = "\n\n".join(
                self._format_excerpt(excerpt_id, chunk)
                for excerpt_id, chunk in source_map.items()
            )

        user_prompt = f"""Context excerpts:
            {context_block}

            Question: {question}"""
        return PromptResult(
            system_prompt=SYSTEM_PROMPT,
            user_prompt=user_prompt,
            source_map=source_map,
            response_schema=RESPONSE_SCHEMA,
        )
