from __future__ import annotations

from dataclasses import dataclass
from typing import Any
import requests
import os
from pathlib import Path
from dotenv import load_dotenv

load_dotenv() # .env load
api_key = os.getenv("OPENROUTER_API_KEY")
model = os.getenv("OPENROUTER_MODEL")

@dataclass
class OpenRouterClient:
    api_key: str
    model: str
    site_url: str = "https://localhost"
    site_name: str = "FinAgent"
    timeout: int = 60
    verify_ssl: bool | str = True

    def __post_init__(self) -> None:
        if isinstance(self.verify_ssl, str):
            verify_path = Path(self.verify_ssl).expanduser()
            if not verify_path.exists():
                raise FileNotFoundError(f"SSL CA 번들을 찾을 수 없습니다: {verify_path}")
            self.verify_ssl = str(verify_path)

    def chat(
        self,
        system_prompt: str,
        user_prompt: str,
        temperature: float = 0.2,
        max_tokens: int = 1200,
    ) -> str:
        url = "https://openrouter.ai/api/v1/chat/completions"
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "HTTP-Referer": self.site_url,
            "X-Title": self.site_name,
            "Content-Type": "application/json",
        }
        payload: dict[str, Any] = {
            "model": self.model,
            "messages": [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt},
            ],
            "temperature": temperature,
            "max_tokens": max_tokens,
        }

        try:
            response = requests.post(
                url,
                headers=headers,
                json=payload,
                timeout=self.timeout,
                verify=self.verify_ssl,
            )
            response.raise_for_status()
            data = response.json()
        except requests.exceptions.SSLError as exc:
            raise RuntimeError(
                "OpenRouter TLS 검증에 실패했습니다. "
                "사내 프록시/자체 서명 인증서를 사용하는 환경이라면 "
                "OPENROUTER_CA_BUNDLE, REQUESTS_CA_BUNDLE 또는 SSL_CERT_FILE로 "
                "신뢰할 CA 번들을 지정하세요. "
                "임시 확인용으로만 OPENROUTER_DISABLE_SSL_VERIFY=1을 사용하세요."
            ) from exc

        return data["choices"][0]["message"]["content"].strip()

if __name__ == "__main__":
    client = OpenRouterClient(
        api_key=api_key,
        model=model,  # 사용하는 모델로 변경
        verify_ssl=False 
    )

    system_prompt = "You are a helpful assistant."
    user_prompt = "what's your name?"

    try:
        response = client.chat(
            system_prompt=system_prompt,
            user_prompt=user_prompt
        )
        print("Response:\n", response)

    except Exception as e:
        print("Error:", e)
