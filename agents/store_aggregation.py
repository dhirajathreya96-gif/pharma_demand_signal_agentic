# agents/store_aggregation.py
from __future__ import annotations

from dataclasses import dataclass
from typing import List, Tuple

import pandas as pd


@dataclass
class StoreAggregationSummary:
    num_stores: int
    num_products: int
    num_days: int
    total_rows_input: int
    total_rows_output: int


class StoreAggregationAgent:
    """
    Aggregates store-level sales into product-level daily totals.

    Input Expected Columns:
        - store_name
        - product_name
        - date
        - quantity_sold

    Output Columns:
        - product_name
        - date
        - total_quantity_sold
        - contributing_stores
    """

    REQUIRED_COLUMNS = {
        "store_name",
        "product_name",
        "date",
        "quantity_sold",
    }

    def __init__(self, validate_input: bool = True) -> None:
        self.validate_input = validate_input

    def aggregate(
        self, df: pd.DataFrame
    ) -> Tuple[pd.DataFrame, StoreAggregationSummary]:
        """
        Aggregates all stores into product-level daily demand.

        Returns:
            aggregated_df: DataFrame with total demand per product per day
            summary: Metadata about the aggregation process
        """

        if self.validate_input:
            self._validate_columns(df)

        df = df.copy()
        df["date"] = pd.to_datetime(df["date"])

        # Core aggregation
        aggregated_df = (
            df.groupby(["product_name", "date"], as_index=False)
            .agg(
                total_quantity_sold=("quantity_sold", "sum"),
                contributing_stores=("store_name", "nunique"),
            )
            .sort_values(["product_name", "date"])
            .reset_index(drop=True)
        )

        summary = StoreAggregationSummary(
            num_stores=df["store_name"].nunique(),
            num_products=df["product_name"].nunique(),
            num_days=df["date"].nunique(),
            total_rows_input=len(df),
            total_rows_output=len(aggregated_df),
        )

        return aggregated_df, summary

    def aggregate_by_store(
        self, df: pd.DataFrame
    ) -> pd.DataFrame:
        """
        Optional helper:
        Returns per-store, per-product, per-day totals
        (useful for store-level reports later).
        """

        if self.validate_input:
            self._validate_columns(df)

        df = df.copy()
        df["date"] = pd.to_datetime(df["date"])

        store_df = (
            df.groupby(["store_name", "product_name", "date"], as_index=False)
            .agg(quantity_sold=("quantity_sold", "sum"))
            .sort_values(["store_name", "product_name", "date"])
            .reset_index(drop=True)
        )

        return store_df

    def _validate_columns(self, df: pd.DataFrame) -> None:
        missing = self.REQUIRED_COLUMNS - set(df.columns)
        if missing:
            raise ValueError(
                f"StoreAggregationAgent missing required columns: {missing}. "
                f"Expected: {self.REQUIRED_COLUMNS}"
            )
