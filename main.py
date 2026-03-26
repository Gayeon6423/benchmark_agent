from __future__ import annotations

import argparse
import json

from finagent.agent import build_agent
from finagent.tools.pii_guardrail import mask_pii


def main() -> None:
    parser = argparse.ArgumentParser(description="금융 벤치마크 특화 에이전트")
    sub = parser.add_subparsers(dest="command", required=True)

    test_parser = sub.add_parser("test", help="간단한 로컬 스모크 테스트")
    test_parser.add_argument(
        "--text",
        default="홍길동 이메일은 test@example.com, 전화번호는 010-1234-5678",
        help="테스트할 원문",
    )

    pii_parser = sub.add_parser("pii", help="PII 마스킹")
    pii_parser.add_argument("--text", required=True, help="마스킹할 원문")

    qa_parser = sub.add_parser("generate-qa", help="QA 벤치마크 CSV 생성")
    qa_parser.add_argument("--dataset-name", required=True)
    qa_parser.add_argument("--topic", required=True)
    qa_parser.add_argument("--count", type=int, default=20)
    qa_parser.add_argument("--difficulty", default="mixed")
    qa_parser.add_argument("--output", default="data/qa_benchmark.csv")

    rag_parser = sub.add_parser("rag-search", help="RAG 기반 웹 벤치마크 검색")
    rag_parser.add_argument("--query", required=True)
    rag_parser.add_argument("--top-k", type=int, default=5)
    rag_parser.add_argument("--output", default="data/rag_report.md")

    args = parser.parse_args()

    if args.command == "test":
        result = mask_pii(args.text)
        print("입력:", result["original"])
        print("출력:", result["masked"])
        print("탐지 개수:", json.dumps(result["counts"], ensure_ascii=False))

        assert result["masked"] != result["original"], "PII 마스킹이 적용되지 않았습니다."
        assert "email" in result["counts"], "이메일이 탐지되지 않았습니다."
        assert "phone" in result["counts"], "전화번호가 탐지되지 않았습니다."
        print("테스트 통과")
        return

    agent = build_agent()

    if args.command == "pii":
        result = agent.run_pii_guardrail(args.text)
        print(result["masked"])
        if result["counts"]:
            print("\nDetected PII:", json.dumps(result["counts"], ensure_ascii=False))
        return

    if args.command == "generate-qa":
        path = agent.run_generate_qa(
            dataset_name=args.dataset_name,
            topic=args.topic,
            count=args.count,
            difficulty=args.difficulty,
            output_csv=args.output,
        )
        print(f"완료: QA CSV 생성 -> {path}")
        return

    if args.command == "rag-search":
        result = agent.run_rag_search(query=args.query, top_k=args.top_k, output_file=args.output)
        print(f"완료: 크롤링 문서 수={result['crawled_count']}, 선택 문서 수={result['selected_count']}")
        print(f"보고서 파일: {args.output}")
        return


if __name__ == "__main__":
    main()
