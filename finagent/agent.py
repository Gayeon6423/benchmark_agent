from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Any

from .config import get_settings
from .llm.openrouter_client import OpenRouterClient
from .tools.pii_guardrail import mask_pii
from .tools.qa_generator import generate_qa_csv
from .tools.rag_search import rag_benchmark_search


@dataclass
class FinancialBenchmarkAgent:
    llm: OpenRouterClient | None = None

    def _client(self) -> OpenRouterClient:
        if self.llm is not None:
            return self.llm

        settings = get_settings()
        verify_ssl = (
            False
            if settings.openrouter_disable_ssl_verify
            else (settings.openrouter_ca_bundle or True)
        )
        self.llm = OpenRouterClient(
            api_key=settings.openrouter_api_key,
            model=settings.openrouter_model,
            site_url=settings.openrouter_site_url,
            site_name=settings.openrouter_site_name,
            verify_ssl=verify_ssl,
        )
        return self.llm

    def run_pii_guardrail(self, text: str) -> dict[str, Any]:
        return mask_pii(text)

    def run_generate_qa(
        self,
        dataset_name: str,
        topic: str,
        count: int,
        difficulty: str,
        output_csv: str,
    ) -> str:
        output_path = Path(output_csv)
        output_path.parent.mkdir(parents=True, exist_ok=True)

        return generate_qa_csv(
            dataset_name=dataset_name,
            topic=topic,
            count=count,
            difficulty=difficulty,
            output_path=str(output_path),
            llm_client=self._client(),
        )

    def run_rag_search(self, query: str, top_k: int = 5, output_file: str | None = None) -> dict[str, Any]:
        result = rag_benchmark_search(query=query, top_k=top_k, llm_client=self._client())

        if output_file:
            output_path = Path(output_file)
            output_path.parent.mkdir(parents=True, exist_ok=True)
            output_path.write_text(result["report_markdown"], encoding="utf-8")

        return result


def build_agent() -> FinancialBenchmarkAgent:
    return FinancialBenchmarkAgent()
