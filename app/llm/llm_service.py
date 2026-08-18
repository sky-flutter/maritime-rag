from abc import ABC, abstractmethod
from app.llm.models import Answer
from app.prompt.prompt_builder import PromptResult


class LLMService(ABC):
    @abstractmethod
    def generate_answer(self, prompt_result: PromptResult) -> Answer:
        raise NotImplementedError
