# agents/report_generator.py
from __future__ import annotations

from datetime import datetime
from typing import List

from .demand_insight import DemandSignal


class ReportGeneratorAgent:
    """
    Builds a human-readable daily demand summary report.
    """

    def __init__(self, report_date: datetime | None = None) -> None:
        self.report_date = report_date or datetime.today()

    def generate_text_report(self, signals: List[DemandSignal]) -> str:
        lines: list[str] = []

        header_date = self.report_date.strftime("%Y-%m-%d")
        lines.append(f"DAILY DEMAND SUMMARY REPORT - {header_date}")
        lines.append("=" * 60)
        lines.append("")

        # High-level summary counts
        inc = sum(1 for s in signals if s.action == "increase_stock")
        dec = sum(1 for s in signals if s.action == "reduce_stock")
        stable = sum(1 for s in signals if s.action == "maintain_stock")
        review = sum(1 for s in signals if s.action == "review_data")

        lines.append("Summary by Action:")
        lines.append(f"  - Products recommended to INCREASE stock : {inc}")
        lines.append(f"  - Products recommended to REDUCE stock   : {dec}")
        lines.append(f"  - Products to MAINTAIN stock            : {stable}")
        lines.append(f"  - Products flagged for REVIEW           : {review}")
        lines.append("")
        lines.append("-" * 60)
        lines.append("DETAILED PRODUCT-LEVEL INSIGHTS")
        lines.append("-" * 60)
        lines.append("")

        # Per-product details
        for s in sorted(signals, key=lambda x: x.product_name.lower()):
            pct = s.pct_change_vs_avg * 100
            lines.append(f"Product: {s.product_name}")
            lines.append(f"  Detected Trend       : {s.trend_label}")
            lines.append(
                "  Recent Sales         : "
                f"last_day={s.last_quantity:.1f}, "
                f"recent_avg={s.average_quantity:.1f}, "
                f"change_vs_avg={pct:+.1f}%"
            )
            lines.append(f"  Volatility Index     : {s.volatility_index:.2f}")
            lines.append(
                f"  Recommended Action   : {s.action.upper()} "
                f"(strength: {s.action_strength})"
            )
            lines.append(f"  Reasoning (Trend)    : {self._format_single_line(s.trend_label)}")
            lines.append(f"  Reasoning (Action)   : {self._format_single_line(s.explanation)}")
            lines.append("")

        return "\n".join(lines)

    @staticmethod
    def _format_single_line(text: str) -> str:
        # Replace newlines in reasoning with spaces to keep report tidy.
        return " ".join(str(text).split())
