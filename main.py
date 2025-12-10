# main.py
from __future__ import annotations

import argparse
from pathlib import Path

from agents.data_loader import DataLoaderAgent
from agents.store_aggregation import StoreAggregationAgent
from agents.trend_detector import TrendDetectorAgent
from agents.demand_insight import DemandInsightAgent
from agents.report_generator import ReportGeneratorAgent


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Daily Pharmacy Demand Signal Report Generator"
    )
    parser.add_argument(
        "--input",
        "-i",
        required=True,
        help="Path to daily sales CSV file (columns: product_name,date,quantity_sold)",
    )
    parser.add_argument(
        "--output",
        "-o",
        help="Optional path to save the text report. If omitted, only prints to console.",
    )
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    csv_path = Path(args.input)

    # 1. Data Loader Agent
    loader = DataLoaderAgent(csv_path)
    df, issues = loader.load_and_validate()

    if issues:
        print("Data validation issues:")
        for issue in issues:
            print(f"  [{issue.level.upper()}] {issue.message}")
        print("")

    # 2. Store Aggregation Agent ✅
    aggregation_agent = StoreAggregationAgent()
    aggregated_df, agg_summary = aggregation_agent.aggregate(df)

    print("\nSTORE AGGREGATION SUMMARY")
    print("--------------------------")
    print(f"Stores detected      : {agg_summary.num_stores}")
    print(f"Products detected    : {agg_summary.num_products}")
    print(f"Days covered         : {agg_summary.num_days}")
    print(f"Input rows           : {agg_summary.total_rows_input}")
    print(f"Output rows          : {agg_summary.total_rows_output}")
    print("")

    # 3. Trend Detector Agent
    trend_agent = TrendDetectorAgent(
        trend_window=7,
        min_history=3,
        increasing_threshold=0.20,
        decreasing_threshold=-0.20,
        volatility_threshold=0.50,
        spike_pct_change_threshold=0.50,
    )
    trends = trend_agent.detect_trends(df)

    # 4. Demand Insight Agent
    insight_agent = DemandInsightAgent(
        strong_increase_threshold=0.50,
        moderate_increase_threshold=0.20,
        strong_decrease_threshold=-0.50,
        moderate_decrease_threshold=-0.20,
    )
    signals = insight_agent.generate_signals(trends)

    # . Report Generator Agent
    report_agent = ReportGeneratorAgent()
    report_text = report_agent.generate_text_report(signals)

    print(report_text)

    if args.output:
        output_path = Path(args.output)
        output_path.write_text(report_text, encoding="utf-8")
        print(f"\nReport saved to: {output_path.resolve()}")


if __name__ == "__main__":
    main()
