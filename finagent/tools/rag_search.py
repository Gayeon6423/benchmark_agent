from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Any
from urllib.parse import quote_plus, unquote, urlparse
import json
import os

import requests
from bs4 import BeautifulSoup
from dotenv import load_dotenv

# .env 파일에서 OpenRouter 설정을 읽어온다.
load_dotenv()
API_KEY = os.getenv("OPENROUTER_API_KEY")
MODEL = os.getenv("OPENROUTER_MODEL", "openai/gpt-5-mini")
SITE_URL = os.getenv("OPENROUTER_SITE_URL", "https://localhost")
SITE_NAME = os.getenv("OPENROUTER_SITE_NAME", "FinAgent")


@dataclass
class WebDoc:
    # 검색 결과에서 실제로 읽어온 웹 문서 1개를 표현한다.
    title: str
    url: str
    content: str


def llm(
    system_prompt: str,
    user_prompt: str,
    temperature: float = 0.2,
    max_tokens: int = 1200,
) -> str:
    url = "https://openrouter.ai/api/v1/chat/completions"
    headers = {
        "Authorization": f"Bearer {API_KEY}",
        "HTTP-Referer": SITE_URL,
        "X-Title": SITE_NAME,
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
    }

    response = requests.post(
        url,
        headers=headers,
        json=payload,
        timeout=60,
        verify=True,
    )
    response.raise_for_status()

    data = response.json()
    return data["choices"][0]["message"]["content"].strip()


def _fetch_text(url: str, timeout: int = 12) -> str:
    # 웹페이지 HTML을 받아서 불필요한 태그를 제거한 뒤 텍스트만 추출한다.
    try:
        response = requests.get(url, timeout=timeout, headers={"User-Agent": "Mozilla/5.0"})
        response.raise_for_status()
        soup = BeautifulSoup(response.text, "html.parser")
        for tag in soup(["script", "style", "noscript"]):
            tag.decompose()
        text = " ".join(soup.get_text(separator=" ").split())
        return text[:12000]
    except Exception:
        return ""


def _search_web(query: str, max_results: int = 8) -> list[dict[str, str]]:
    # DuckDuckGo HTML 검색 페이지를 이용해 검색 결과를 수집한다.
    search_url = f"https://duckduckgo.com/html/?q={quote_plus(query)}"
    response = requests.get(search_url, timeout=12, headers={"User-Agent": "Mozilla/5.0"})
    response.raise_for_status()

    soup = BeautifulSoup(response.text, "html.parser")
    results: list[dict[str, str]] = []

    for item in soup.select(".result"):
        a_tag = item.select_one("a.result__a")
        snippet = item.select_one(".result__snippet")
        if not a_tag:
            continue

        raw_link = a_tag.get("href", "")
        title = a_tag.get_text(" ", strip=True)
        body = snippet.get_text(" ", strip=True) if snippet else ""

        parsed = urlparse(raw_link)
        href = raw_link
        if parsed.netloc.endswith("duckduckgo.com") and "uddg=" in parsed.query:
            for part in parsed.query.split("&"):
                if part.startswith("uddg="):
                    href = unquote(part.replace("uddg=", "", 1))
                    break

        if href and href.startswith("http"):
            results.append({"title": title, "href": href, "body": body})

        if len(results) >= max_results:
            break

    return results


def _rank_docs(query: str, docs: list[WebDoc], top_k: int) -> list[WebDoc]:
    # 쿼리 단어와 문서 본문이 얼마나 많이 겹치는지로 대략적인 관련도를 계산한다.
    if not docs:
        return []

    query_terms = {t.lower() for t in query.split() if len(t.strip()) > 1}
    scored: list[tuple[WebDoc, float]] = []
    for d in docs:
        text = f"{d.title} {d.content[:3000]}".lower()
        if not query_terms:
            score = 0.0
        else:
            hit = sum(1 for term in query_terms if term in text)
            score = hit / max(len(query_terms), 1)
        scored.append((d, score))

    scored.sort(key=lambda x: x[1], reverse=True)
    return [doc for doc, _ in scored[:top_k]]


def rag_benchmark_search(query: str, top_k: int = 5) -> dict[str, Any]:
    # 1) 웹 검색 결과를 넓게 수집한다.
    search_results = _search_web(query, max_results=max(8, top_k * 2))

    # 2) 각 검색 결과 페이지를 실제로 열어서 본문 텍스트를 가져온다.
    docs: list[WebDoc] = []
    for item in search_results:
        url = item.get("href", "")
        if not url:
            continue
        text = _fetch_text(url)
        if not text:
            continue
        docs.append(WebDoc(title=item.get("title", ""), url=url, content=text))

    # 3) 쿼리와 가장 관련 있는 문서만 남긴다.
    ranked = _rank_docs(query, docs, top_k=top_k)

    # 4) LLM에 넣을 컨텍스트 문자열을 만든다.
    context = "\n\n".join(
        [
            f"[문서 {i+1}]\n제목: {d.title}\nURL: {d.url}\n요약용 텍스트: {d.content[:1800]}"
            for i, d in enumerate(ranked)
        ]
    )

    # 5) LLM에게 어떤 보고서를 써야 하는지 한국어로 지시한다.
    system_prompt = (
        "당신은 금융 벤치마크 리서치 어시스턴트입니다. "
        "수집된 웹 문서를 바탕으로 평가에 유용한 벤치마크 데이터셋과 생성 전략을 정리하세요."
    )
    user_prompt = f"""
사용자 질의: {query}

수집된 문서:
{context}

다음 형식으로 마크다운 보고서를 작성하세요:
1) 후보 벤치마크 데이터셋 목록(이름 + 왜 유용한지)
2) 현재 문서 기준의 커버리지 부족 영역
3) 커스텀 QA 벤치마크 생성 전략
4) 참고 URL 목록
""".strip()

    # 6) 최종 보고서를 LLM으로 생성한다.
    report = llm(system_prompt=system_prompt, user_prompt=user_prompt, temperature=0.2, max_tokens=1400)

    return {
        # 검색 작업의 메타 정보와 최종 보고서를 함께 반환한다.
        "query": query,
        "crawled_count": len(docs),
        "selected_count": len(ranked),
        "references": [{"title": d.title, "url": d.url} for d in ranked],
        "report_markdown": report,
    }


if __name__ == "__main__":
    result = rag_benchmark_search(query="한국 증시 벤치마크 데이터셋")
    print(result["report_markdown"])
