import json

from openai import OpenAI, OpenAIError

from app.llm.llm_service import LLMService
from app.llm.models import Answer
from app.prompt.prompt_builder import PromptResult


class LLMServiceError(Exception):
    """Raised when the LLM call failed or returns an unusable response"""

    pass


class OpenAILLMService(LLMService):
    def __init__(self, client: OpenAI, model: str = "gpt-4o-mini"):
        self._client = client
        self._model = model

    def _to_answer(self, parsed: dict, prompt_result: PromptResult) -> Answer:
        cited_id = parsed.get("source_ids", [])
        answered = parsed.get("answered", False)
        text = parsed.get("answer", "")
        source_ids = []
        for cid in cited_id:
            chunk = prompt_result.source_map.get(cid)
            if chunk is not None:
                source_ids.append(chunk)

        if answered and not source_ids:
            answered = (False,)
            text = (
                "The model claimed an answer but did not cite valid sources, "
                "so this response has been treated as unanswered. "
                f"Original response: {text}"
            )
        return Answer(
            answered=answered,
            text=text,
            sources=source_ids,
        )

    def generate_answer(self, prompt_result: PromptResult) -> Answer:
        try:
            response = self._client.chat.completions.create(
                model=self._model,
                messages=[
                    {"role": "system", "content": prompt_result.system_prompt},
                    {"role": "user", "content": prompt_result.user_prompt},
                ],
                response_format={
                    "type": "json_schema",
                    "json_schema": {
                        "name": "grounded_answer",
                        "schema": prompt_result.response_schema,
                        "strict": True,
                    },
                },
            )
        except OpenAIError as e:
            raise LLMServiceError(f"LLM call failed: {e}") from e

        raw = response.choices[0].message.content
        try:
            parsed = json.loads(raw)
        except json.JSONDecodeError as e:
            raise LLMServiceError(f"LLM return invalid json: {e}") from e

        return self._to_answer(parsed, prompt_result)
