import openai
class OpenAIClient:
    def __init__(self, client=None):
        self.client = client or openai.OpenAI()
    def respond(self, messages, *, model, max_tokens):
        r = self.client.responses.create(model=model, input=messages, max_output_tokens=max_tokens)
        return getattr(r, "output_text", "").strip()
