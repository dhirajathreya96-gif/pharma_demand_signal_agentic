# agents/trend_detector.py
from __future__ import annotations

from dataclasses import dataclass
from typing import List

import numpy as np
import pandas as pd


@dataclass
class ProductTrend:
    product_name: str
    trend_label: str            # increasing, decreasing, stable, spiky, insufficient_data
    reason: str                 # human-readable explanation of why
    last_quantity: float
    average_quantity: float
    pct_change_vs_avg: float    # e.g. +0.25 for +25%
    volatility_index: float     # coefficient of variation in the window [0..]
    num_days_used: int


class TrendDetectorAgent:
    """
    Applies rule-based logic to detect demand trends per product.

    Rules (you can tweak thresholds):
      - If fewer than min_history days -> 'insufficient_data'
      - Compute:
          avg = mean(quantity over window except last day)
          last = quantity on most recent day
          pct_change = (last - avg) / avg   (if avg > 0 else 0)
          volatility = std(window) / mean(window)  (if mean > 0 else 0)
      - If volatility is high and pct_change not clearly directional -> 'spiky'
      - Else:
          if pct_change >= increasing_threshold and recent diffs mostly positive -> 'increasing'
          if pct_change <= decreasing_threshold and recent diffs mostly negative -> 'decreasing'
          else -> 'stable'
    """

    def __init__(
        self,
        trend_window: int = 7,
        min_history: int = 3,
        increasing_threshold: float = 0.20,  # +20% vs previous average
        decreasing_threshold: float = -0.20, # -20% vs previous average
        volatility_threshold: float = 0.50,  # coefficient of variation > 0.5 -> spiky
        spike_pct_change_threshold: float = 0.50, # 50% single-day jump/drop
    ) -> None:
        self.trend_window = trend_window
        self.min_history = min_history
        self.increasing_threshold = increasing_threshold
        self.decreasing_threshold = decreasing_threshold
        self.volatility_threshold = volatility_threshold
        self.spike_pct_change_threshold = spike_pct_change_threshold

    def detect_trends(self, df: pd.DataFrame) -> List[ProductTrend]:
        trends: List[ProductTrend] = []

        for product_name, group in df.groupby("product_name"):
            qty_series = group.set_index("date")["quantity_sold"].sort_index()
            if qty_series.empty:
                continue

            window = qty_series.tail(self.trend_window)
            if len(window) < self.min_history:
                trends.append(
                    ProductTrend(
                        product_name=product_name,
                        trend_label="insufficient_data",
                        reason=(
                            f"Only {len(window)} days of data available; "
                            f"minimum required is {self.min_history}."
                        ),
                        last_quantity=float(window.iloc[-1]),
                        average_quantity=float(window.mean()),
                        pct_change_vs_avg=0.0,
                        volatility_index=0.0,
                        num_days_used=len(window),
                    )
                )
                continue

            last = float(window.iloc[-1])
            hist = window.iloc[:-1]  # previous days
            avg = float(hist.mean()) if len(hist) > 0 else 0.0

            if avg > 0:
                pct_change = (last - avg) / avg
            else:
                pct_change = 0.0

            mean_all = float(window.mean())
            if mean_all > 0:
                volatility = float(window.std(ddof=0) / mean_all)
            else:
                volatility = 0.0

            # Recent day-by-day direction info (last 3 deltas)
            diffs = np.diff(window.values)
            recent_diffs = diffs[-3:] if len(diffs) >= 3 else diffs
            num_positive = int((recent_diffs > 0).sum())
            num_negative = int((recent_diffs < 0).sum())

            # Check for single-day spikes
            spike_detected = False
            spike_dir = None
            for i in range(1, len(window)):
                prev = window.iloc[i - 1]
                cur = window.iloc[i]
                if prev > 0:
                    change = (cur - prev) / prev
                    if abs(change) >= self.spike_pct_change_threshold:
                        spike_detected = True
                        spike_dir = "up" if change > 0 else "down"
                        break

            # Core rule logic
            if volatility >= self.volatility_threshold and not (
                pct_change >= self.increasing_threshold
                or pct_change <= self.decreasing_threshold
            ):
                trend_label = "spiky"
                reason = (
                    f"Demand is volatile (volatility_index={volatility:.2f}); "
                    "no consistent upward or downward trend."
                )
            else:
                if pct_change >= self.increasing_threshold and num_positive >= 2:
                    trend_label = "increasing"
                    reason = (
                        f"Last day sales ({last:.1f}) are {pct_change*100:.1f}% above "
                        f"recent average ({avg:.1f}), and recent days show mostly increases "
                        f"({num_positive} increases vs {num_negative} decreases)."
                    )
                elif pct_change <= self.decreasing_threshold and num_negative >= 2:
                    trend_label = "decreasing"
                    reason = (
                        f"Last day sales ({last:.1f}) are {pct_change*100:.1f}% below "
                        f"recent average ({avg:.1f}), and recent days show mostly decreases "
                        f"({num_negative} decreases vs {num_positive} increases)."
                    )
                else:
                    if spike_detected and trend_label != "spiky":
                        trend_label = "spiky"
                        direction_word = "upward" if spike_dir == "up" else "downward"
                        reason = (
                            f"Detected a {direction_word} spike greater than "
                            f"{self.spike_pct_change_threshold*100:.0f}% in a single day; "
                            "overall trend is not clearly increasing or decreasing."
                        )
                    else:
                        trend_label = "stable"
                        reason = (
                            f"Last day sales ({last:.1f}) are within ±20% of recent average "
                            f"({avg:.1f}) with limited directional bias "
                            f"({num_positive} increases vs {num_negative} decreases)."
                        )

            trends.append(
                ProductTrend(
                    product_name=product_name,
                    trend_label=trend_label,
                    reason=reason,
                    last_quantity=last,
                    average_quantity=avg,
                    pct_change_vs_avg=pct_change,
                    volatility_index=volatility,
                    num_days_used=len(window),
                )
            )

        return trends
