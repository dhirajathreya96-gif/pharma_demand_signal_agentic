# agents/demand_insight.py
from __future__ import annotations

from dataclasses import dataclass
from typing import List

from .trend_detector import ProductTrend


@dataclass
class DemandSignal:
    product_name: str
    trend_label: str
    action: str                # increase_stock, reduce_stock, maintain_stock, review_data
    action_strength: str       # strong / moderate / mild
    explanation: str           # human-readable reason based on rules
    last_quantity: float
    average_quantity: float
    pct_change_vs_avg: float
    volatility_index: float


class DemandInsightAgent:
    """
    Converts trend labels into stocking recommendations using simple rules.
    """

    def __init__(
        self,
        strong_increase_threshold: float = 0.50,   # +50% vs avg
        moderate_increase_threshold: float = 0.20, # +20% vs avg
        strong_decrease_threshold: float = -0.50,  # -50% vs avg
        moderate_decrease_threshold: float = -0.20,# -20% vs avg
    ) -> None:
        self.strong_increase_threshold = strong_increase_threshold
        self.moderate_increase_threshold = moderate_increase_threshold
        self.strong_decrease_threshold = strong_decrease_threshold
        self.moderate_decrease_threshold = moderate_decrease_threshold

    def generate_signals(self, trends: List[ProductTrend]) -> List[DemandSignal]:
        signals: List[DemandSignal] = []

        for t in trends:
            if t.trend_label == "insufficient_data":
                signals.append(
                    DemandSignal(
                        product_name=t.product_name,
                        trend_label=t.trend_label,
                        action="review_data",
                        action_strength="mild",
                        explanation=(
                            "Not enough recent data to make a confident stocking decision. "
                            "Review sales history or ensure data capture is complete."
                        ),
                        last_quantity=t.last_quantity,
                        average_quantity=t.average_quantity,
                        pct_change_vs_avg=t.pct_change_vs_avg,
                        volatility_index=t.volatility_index,
                    )
                )
                continue

            if t.trend_label == "spiky":
                signals.append(
                    DemandSignal(
                        product_name=t.product_name,
                        trend_label=t.trend_label,
                        action="review_data",
                        action_strength="moderate",
                        explanation=(
                            "Demand is highly volatile or driven by spikes. "
                            "Avoid drastic changes in stock; investigate possible causes "
                            "(promotions, one-off events, data errors)."
                        ),
                        last_quantity=t.last_quantity,
                        average_quantity=t.average_quantity,
                        pct_change_vs_avg=t.pct_change_vs_avg,
                        volatility_index=t.volatility_index,
                    )
                )
                continue

            pct_change = t.pct_change_vs_avg

            if t.trend_label == "increasing":
                if pct_change >= self.strong_increase_threshold:
                    action = "increase_stock"
                    strength = "strong"
                    expl = (
                        "Strong increase in demand (last day significantly above recent average). "
                        "Increase stock levels aggressively to avoid stock-outs."
                    )
                elif pct_change >= self.moderate_increase_threshold:
                    action = "increase_stock"
                    strength = "moderate"
                    expl = (
                        "Moderate but consistent increase in demand. "
                        "Increase stock levels gradually and continue monitoring."
                    )
                else:
                    action = "increase_stock"
                    strength = "mild"
                    expl = (
                        "Slight upward trend. Consider a mild stock increase and close monitoring."
                    )
            elif t.trend_label == "decreasing":
                if pct_change <= self.strong_decrease_threshold:
                    action = "reduce_stock"
                    strength = "strong"
                    expl = (
                        "Strong decrease in demand (last day far below recent average). "
                        "Reduce stock levels significantly to avoid overstocking."
                    )
                elif pct_change <= self.moderate_decrease_threshold:
                    action = "reduce_stock"
                    strength = "moderate"
                    expl = (
                        "Moderate downward trend. Reduce stock gradually and monitor."
                    )
                else:
                    action = "reduce_stock"
                    strength = "mild"
                    expl = (
                        "Demand is softening slightly. Consider small reductions in stock "
                        "or slower replenishment."
                    )
            else:  # stable
                action = "maintain_stock"
                strength = "mild"
                expl = (
                    "Demand appears stable around its recent average. "
                    "Maintain current stock levels with normal replenishment cycles."
                )

            signals.append(
                DemandSignal(
                    product_name=t.product_name,
                    trend_label=t.trend_label,
                    action=action,
                    action_strength=strength,
                    explanation=expl,
                    last_quantity=t.last_quantity,
                    average_quantity=t.average_quantity,
                    pct_change_vs_avg=t.pct_change_vs_avg,
                    volatility_index=t.volatility_index,
                )
            )

        return signals
