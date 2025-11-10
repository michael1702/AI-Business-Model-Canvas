from abc import ABC, abstractmethod
class LLMPort(ABC):
    @abstractmethod
    def respond(self, messages, *, model: str, max_tokens: int) -> str: ...
