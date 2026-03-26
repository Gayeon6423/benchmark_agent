from __future__ import annotations

from pathlib import Path
from typing import Any
import pandas as pd
import requests
import os
import json
from dotenv import load_dotenv

load_dotenv()
API_KEY = os.getenv("OPENROUTER_API_KEY")
MODEL = os.getenv("OPENROUTER_MODEL", "openai/gpt-5-mini")
SYSTEM_PROMPT = """
고품질의 금융 벤치마크 QA 데이터셋을 생성합니다.
반드시 여러 개의 질문-답변 쌍을 생성해야 하며, 사용자가 지정한 행 수와 정확히 일치해야 합니다.
각 항목은 '질문', '답변' 두 필드만 가져야 합니다.
중복 없이, 금융 도메인에 적합한 실용적인 QA를 생성하세요.
""".strip()


def llm(
    system_prompt: str,
    user_prompt: str,
    temperature: float = 0.2,
    max_tokens: int = 1200,
) -> str:
    url = "https://openrouter.ai/api/v1/chat/completions"
    headers = {
        "Authorization": f"Bearer {API_KEY}",
        "Content-Type": "application/json",
    }
    payload: dict[str, Any] = {
        "model": MODEL,
        "messages": [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt},
        ],
        "temperature": temperature,
        "max_tokens": max_tokens,
        "response_format": {
            "type": "json_schema",
            "json_schema": {
                "name": "qa_generator",
                "strict": True,
                "schema": {
                    "type": "object",
                    "properties": {
                        "items": {
                            "type": "array",
                            "description": "생성된 QA 목록",
                            "items": {
                                "type": "object",
                                "properties": {
                                    "질문": {
                                        "type": "string",
                                        "description": "주제에 특화된 벤치마크 질문"
                                    },
                                    "답변": {
                                        "type": "string",
                                        "description": "주제에 특화된 벤치마크 질문에 대한 답변"
                                    }
                                },
                                "required": ["질문", "답변"],
                                "additionalProperties": False
                            }
                        }
                    },
                    "required": ["items"],
                    "additionalProperties": False
                }
            },
        }
    }
    response = requests.post(
        url,
        headers=headers,
        json=payload,
        timeout=30,
        verify=True,
    )
    data = response.json()
    result = data["choices"][0]["message"]["content"].strip()
    if result.startswith("```") and result.endswith("```"):
        result = result[3:-3].strip()
    return result


def generate_qa_csv(
    dataset_name: str,
    topic: str,
    count: int,
    difficulty: str,
    output_path: str,
) -> str:
    user_prompt = f"""
데이터 명: {dataset_name}
주제: {topic}
행 수: {count}
난이도: {difficulty}

필수:
- 금융 도메인에 특화된 질문-답변 쌍을 생성하세요.
- 질문은 실용적이고 평가 준비가 되어 있어야 합니다.
- 답변은 간결하지만 사실적으로 명확해야 합니다.
- 정확히 {count}개의 질문-답변 쌍을 생성하세요.
- 모든 질문과 답변은 서로 중복되지 않아야 합니다.
- 반드시 JSON 객체 형태로 반환하고, 최상위 키는 items여야 합니다.
- items 안에는 질문/답변 객체를 정확히 {count}개 넣으세요.
""".strip()

    response = llm(
        system_prompt=SYSTEM_PROMPT,
        user_prompt=user_prompt,
        temperature=0.4,
        max_tokens=2200,
    )
    print("response:", response)

    data = json.loads(response)
    df = pd.DataFrame(data["items"])

    output_path = Path(output_path)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    df.to_csv(output_path, index=False, encoding="utf-8-sig")

    return str(output_path)


if __name__ == "__main__":
    output_path = generate_qa_csv(
        dataset_name="test_dataset",
        topic="stock market basics",
        count=3,
        difficulty="easy",
        output_path="./data/test_output_v2.csv"
    )

    print("결과 생성 완료:", output_path)