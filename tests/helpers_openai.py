# tests/helpers_openai.py
import json

def make_openai_responses_json(payload_dict: dict) -> dict:
    """
    Baut ein minimales /v1/responses-JSON wie in deiner Kassette:
    output -> content -> type=output_text, text=<JSON als String>.
    """
    return {
        "id": "resp_test",
        "object": "response",
        "model": "gpt-5-mini-2025-08-07",
        "status": "completed",
        "output": [
            {
                "id": "msg_1",
                "type": "message",
                "status": "completed",
                "role": "assistant",
                "content": [
                    {
                        "type": "output_text",
                        "text": json.dumps(payload_dict),
                        "annotations": [],
                        "logprobs": [],
                    }
                ],
            }
        ],
        "usage": {"input_tokens": 100, "output_tokens": 200},
    }
