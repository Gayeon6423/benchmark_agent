from __future__ import annotations

__all__ = ["FinancialBenchmarkAgent"]


def __getattr__(name: str):
    if name == "FinancialBenchmarkAgent":
        from .agent import FinancialBenchmarkAgent

        return FinancialBenchmarkAgent
    raise AttributeError(f"module {__name__!r} has no attribute {name!r}")
