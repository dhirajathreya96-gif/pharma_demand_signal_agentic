# agents/data_loader.py
from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import List

import pandas as pd


@dataclass
class DataValidationIssue:
    level: str   # "warning" or "error"
    message: str


class DataLoaderAgent:
    """
    Responsible for:
      - Loading the CSV file
      - Basic validation of required columns
      - Ensuring date is parsed and data is sorted
    """

    REQUIRED_COLUMNS = {"product_name", "date", "quantity_sold"}

    def __init__(self, filepath: str | Path):
        self.filepath = Path(filepath)

    def load_and_validate(self) -> tuple[pd.DataFrame, List[DataValidationIssue]]:
        issues: List[DataValidationIssue] = []

        if not self.filepath.exists():
            raise FileNotFoundError(f"CSV file not found at: {self.filepath}")

        df = pd.read_csv(self.filepath)

        # Check required columns
        missing = self.REQUIRED_COLUMNS - set(df.columns)
        if missing:
            raise ValueError(
                f"Missing required columns: {', '.join(missing)}. "
                f"Expected columns: {', '.join(self.REQUIRED_COLUMNS)}"
            )

        # Parse date
        try:
            df["date"] = pd.to_datetime(df["date"])
        except Exception as exc:  # noqa: BLE001
            raise ValueError(
                "Failed to parse 'date' column. Please ensure it is in a valid date format."
            ) from exc

        # Basic numeric validation
        if not pd.api.types.is_numeric_dtype(df["quantity_sold"]):
            issues.append(
                DataValidationIssue(
                    level="warning",
                    message="Column 'quantity_sold' is not numeric; attempting to coerce.",
                )
            )
            df["quantity_sold"] = pd.to_numeric(df["quantity_sold"], errors="coerce")

        # Check for NaNs in quantity
        num_nans = df["quantity_sold"].isna().sum()
        if num_nans > 0:
            issues.append(
                DataValidationIssue(
                    level="warning",
                    message=f"{num_nans} rows have invalid 'quantity_sold' and will be dropped.",
                )
            )
            df = df.dropna(subset=["quantity_sold"])

        # Ensure quantity is non-negative
        negative_rows = (df["quantity_sold"] < 0).sum()
        if negative_rows > 0:
            issues.append(
                DataValidationIssue(
                    level="warning",
                    message=f"{negative_rows} rows had negative 'quantity_sold' and were set to 0.",
                )
            )
            df.loc[df["quantity_sold"] < 0, "quantity_sold"] = 0

        # Sort by product and date
        df = df.sort_values(["product_name", "date"]).reset_index(drop=True)

        return df, issues
