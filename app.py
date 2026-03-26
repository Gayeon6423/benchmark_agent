from __future__ import annotations

from pathlib import Path

import pandas as pd
import streamlit as st

from finagent.agent import FinancialBenchmarkAgent, build_agent as build_finagent_agent


@st.cache_resource
def _build_agent() -> FinancialBenchmarkAgent:
    return build_finagent_agent()


def _safe_init_agent() -> FinancialBenchmarkAgent | None:
    try:
        return _build_agent()
    except Exception as exc:
        st.error(f"에이전트 초기화 실패: {exc}")
        st.info(".env 파일에 OPENROUTER_API_KEY를 설정했는지 확인하세요.")
        return None


def ui_generate_qa(agent: FinancialBenchmarkAgent) -> None:
    st.subheader("Tool1) 벤치마크 QA 데이터 자동 생성")

    col1, col2 = st.columns(2)
    with col1:
        dataset_name = st.text_input("데이터셋 이름", value="국내주식")
        count = st.number_input("생성 개수", min_value=1, max_value=300, value=20, step=1)
    with col2:
        topic = st.text_input("주제", value="한국 주식시장 기초")
        difficulty = st.selectbox("난이도", options=["easy", "medium", "hard"], index=1)

    # output = st.text_input("출력 데이터 경로", value="data/qa_benchmark_v.csv")
    request = st.text_input("요청 사항", help="구체적인 요청 사항을 입력")

    if st.button("QA 벤치마크 생성", use_container_width=True):
        try:
            saved_path = agent.run_generate_qa(
                dataset_name=dataset_name,
                topic=topic,
                count=int(count),
                difficulty=difficulty,
                output_csv=f'data/{dataset_name}_{topic}_{difficulty}.csv',
            )
            st.success(f"생성 완료: {saved_path}")

            df = pd.read_csv(saved_path)
            st.dataframe(df, use_container_width=True)

            csv_bytes = Path(saved_path).read_bytes()
            st.download_button(
                label="CSV 다운로드",
                data=csv_bytes,
                file_name=Path(saved_path).name,
                mime="text/csv",
                use_container_width=True,
            )
        except Exception as exc:
            st.error(f"QA 생성 실패: {exc}")


def ui_rag_search(agent: FinancialBenchmarkAgent) -> None:
    st.subheader("Tool2) RAG 기반 벤치마크 검색")

    query = st.text_input("검색 질의", value="financial QA benchmark dataset")
    top_k = st.slider("Top-K", min_value=1, max_value=10, value=5)
    output = st.text_input("리포트 저장 경로", value="data/rag_results.md")

    if st.button("RAG 검색 실행", use_container_width=True):
        try:
            result = agent.run_rag_search(query=query, top_k=top_k, output_file=output)
            st.success(
                f"완료: 크롤링 {result['crawled_count']}건 / 선택 {result['selected_count']}건"
            )

            st.markdown("### 참고 URL")
            refs = result.get("references", [])
            if not refs:
                st.info("참고 URL이 없습니다.")
            else:
                for r in refs:
                    title = r.get("title") or "Untitled"
                    url = r.get("url") or ""
                    if url:
                        st.markdown(f"- [{title}]({url})")

            st.markdown("### 리포트")
            st.markdown(result.get("report_markdown", ""))

            report_text = result.get("report_markdown", "")
            st.download_button(
                label="리포트(.md) 다운로드",
                data=report_text.encode("utf-8"),
                file_name=Path(output).name,
                mime="text/markdown",
                use_container_width=True,
            )
        except Exception as exc:
            st.error(f"RAG 검색 실패: {exc}")


def main() -> None:
    st.set_page_config(page_title="FinAgent", page_icon="📊", layout="wide")
    # st.title("금융 벤치마크 특화 에이전트")
    st.caption("금융 벤치마크 서비스")

    agent = _safe_init_agent()
    if agent is None:
        return

    tab1, tab2 = st.tabs([
        "QA 자동 생성",
        "RAG 벤치마크 검색",
    ])

    with tab1:
        ui_generate_qa(agent)

    with tab2:
        ui_rag_search(agent)


if __name__ == "__main__":
    main()
