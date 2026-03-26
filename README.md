# FinAgent - 금융 벤치마크 특화 에이전트

간단 버전의 LLM Agent 구현입니다. OpenRouter를 통해 LLM을 호출하며, 아래 3가지 툴을 포함합니다.

1. **PII 제거(가드레일)**: 패턴 기반 민감정보 마스킹
2. **QA 벤치마크 데이터 자동 생성**: CSV 형태 QA 데이터셋 생성
3. **RAG 기반 벤치마크 검색**: 웹 검색 + 크롤링 + 간단 검색 기반 요약

---

## 빠른 시작

### 1) 의존성 설치

```bash
pip install -r requirements.txt
```

### 2) 환경변수 설정

`.env_example`를 참고해 `.env` 파일을 생성하세요.

```env
OPENROUTER_API_KEY=...
OPENROUTER_MODEL=openai/gpt-4o-mini
OPENROUTER_SITE_URL=https://localhost
OPENROUTER_SITE_NAME=BenchmarkAgent
# 사내 프록시/자체 서명 인증서가 있으면 CA 번들 경로를 지정
OPENROUTER_CA_BUNDLE=/path/to/ca.pem
# 임시 확인용. 운영/공유 환경에서는 권장하지 않음
OPENROUTER_DISABLE_SSL_VERIFY=false
```

### 3) 실행 예시

#### Streamlit UI (로컬)

```bash
streamlit run app.py
```

브라우저에서 3개 탭(PII 제거 / QA 자동 생성 / RAG 검색)을 사용할 수 있습니다.

#### PII 마스킹

```bash
python main.py pii --text "홍길동 이메일은 test@example.com, 전화번호는 010-1234-5678"
```

#### QA 벤치마크 생성

```bash
python main.py generate-qa --dataset-name "국내주식 기본" --topic "한국 주식시장 기초" --count 20 --output data/qa_benchmark.csv
```

```bash
python -m finagent.tools.qa_generator
```

#### RAG 기반 벤치마크 검색

```bash
python main.py rag-search --query "financial QA benchmark dataset" --top-k 5 --output data/rag_results.md
```

---

## 프로젝트 구조

```text
FinAgent/
├─ main.py
├─ app.py
├─ requirements.txt
├─ .env
├─ README.md
└─ finagent/
   ├─ __init__.py
   ├─ config.py
   ├─ agent.py
   ├─ llm/
   │  └─ openrouter_client.py
   └─ tools/
      ├─ pii_guardrail.py
      ├─ qa_generator.py
      └─ rag_search.py
```
