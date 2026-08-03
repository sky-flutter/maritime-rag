from abc import ABC, abstractmethod


class TokenCounter(ABC):
    @abstractmethod
    def count(self, text: str) -> int:
        raise NotImplementedError


class TiktokenCounter(TokenCounter):
    """Uses tiktoken for accurate token counts against OpenAI-style models.
    Swap this for a different TokenCounter implementation if you pick a
    different embedding provider later.
    """

    def __init__(self, encoding_name: str = 'cl100k_base') -> None:
        import tiktoken
        self._encoding = tiktoken.get_encoding(encoding_name)
   
    def count(self, text: str) -> int:
        return len(self._encoding.encode(text))
