import os

from dotenv import find_dotenv, load_dotenv
from openai import OpenAI


DEFAULT_BASE_URL = "http://localhost:1234/v1"
DEFAULT_MODEL = "google/gemma-3-4b"


load_dotenv(find_dotenv(usecwd=True), override=False)


def _env_value(name: str, default: str) -> str:
    value = os.getenv(name)
    return value.strip() if value and value.strip() else default


class LMStudioClient:
    def __init__(self, base_url: str | None = None, model: str | None = None) -> None:
        self.base_url = base_url.strip() if base_url and base_url.strip() else _env_value("LM_STUDIO_URL", DEFAULT_BASE_URL)
        self.model = model.strip() if model and model.strip() else _env_value("LM_STUDIO_MODEL", DEFAULT_MODEL)
        self.client = OpenAI(base_url=self.base_url, api_key="lm-studio")

    def chat(
        self,
        system_prompt: str,
        user_message: str,
        temperature: float = 0.1,
    ) -> str:
        response = self.client.chat.completions.create(
            model=self.model,
            temperature=temperature,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_message},
            ],
        )

        content = response.choices[0].message.content
        if isinstance(content, str) and content.strip():
            return content.strip()

        raise RuntimeError("LM Studio returned an empty chat completion.")

    def ping(self) -> bool:
        response = self.chat(
            system_prompt="You are a connectivity check. Reply with the word PONG only.",
            user_message="reply with the word PONG only",
            temperature=0,
        )
        return response.strip().upper() == "PONG"
