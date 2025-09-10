"""
Unified data processing module for AI Auditor.
Handles file ingestion, analysis, and data transformation.
"""

import io
import logging
import re
from pathlib import Path
from typing import Any, Dict, List, Optional

import chardet
import numpy as np
import pandas as pd
from unidecode import unidecode

from .exceptions import FileProcessingError

logger = logging.getLogger(__name__)


class DataProcessor:
    """Handles data processing operations."""

    def __init__(self):
        self.supported_formats = {".xlsx", ".xls", ".csv", ".tsv", ".txt"}

    def normalize_column_name(self, name: str) -> str:
        """Normalize column name to standard format."""
        if not name:
            return "col"

        # Convert to ASCII and lowercase
        normalized = unidecode(str(name)).strip().lower()

        # Replace spaces and special characters with underscores
        normalized = re.sub(r"\s+", "_", normalized)
        normalized = re.sub(r"[^a-z0-9_]+", "_", normalized)
        normalized = re.sub(r"_+", "_", normalized)
        normalized = normalized.strip("_")

        return normalized or "col"

    def deduplicate_column_names(self, names: List[str]) -> List[str]:
        """Deduplicate column names by adding suffixes."""
        seen = {}
        result = []

        for name in names:
            normalized = self.normalize_column_name(name)

            if normalized in seen:
                seen[normalized] += 1
                normalized = f"{normalized}__{seen[normalized]}"
            else:
                seen[normalized] = 0

            result.append(normalized)

        return result

    def flatten_multiindex_columns(self, columns) -> List[str]:
        """Flatten pandas MultiIndex columns."""
        if isinstance(columns, pd.MultiIndex):
            flattened = []
            for tup in columns.tolist():
                parts = [
                    str(x) for x in tup if x is not None and str(x).lower() != "nan"
                ]
                flattened.append("_".join(parts).strip("_"))
            return self.deduplicate_column_names(flattened)

        return self.deduplicate_column_names(list(columns))

    def find_header_row(self, df: pd.DataFrame, scan_rows: int = 10) -> int:
        """Find the best header row in a DataFrame."""
        best_row = 0
        best_score = -1.0

        for i in range(min(scan_rows, len(df))):
            row = df.iloc[i]
            non_null_count = row.notna().sum()
            unique_count = row.dropna().astype(str).nunique()
            score = float(non_null_count) + 0.5 * float(unique_count)

            if score > best_score:
                best_score = score
                best_row = i

        return best_row

    def extract_prompts_from_header(
        self, df: pd.DataFrame, header_row: int
    ) -> List[str]:
        """Extract prompts from rows above the header."""
        prompts = []

        # Get rows above header
        header_data = df.iloc[: max(header_row, 0)].fillna("")

        for _, row in header_data.iterrows():
            # Join all non-empty values in the row
            line_parts = [str(x).strip() for x in row.tolist() if str(x).strip()]
            line = " ".join(line_parts)

            # Clean up whitespace
            line = re.sub(r"\s{2,}", " ", line)

            if line:
                prompts.append(line)

        # Remove duplicates while preserving order
        unique_prompts = []
        for prompt in prompts:
            if prompt not in unique_prompts:
                unique_prompts.append(prompt)

        return unique_prompts

    def parse_amount_series(self, series: pd.Series) -> pd.Series:
        """Parse amount series with locale-aware handling."""

        def parse_amount(amount_str):
            if pd.isna(amount_str):
                return float("nan")

            # Convert to string and clean
            s = str(amount_str).strip()
            if not s:
                return float("nan")

            # Remove currency symbols and spaces
            s = re.sub(r"[^\d,.\-]", "", s)

            # Handle different formats
            if "," in s and "." in s:
                # Format like "1,234.56" or "1.234,56"
                if s.rfind(".") > s.rfind(","):
                    # "1,234.56" - comma is thousands separator
                    s = s.replace(",", "")
                else:
                    # "1.234,56" - dot is thousands separator, comma is decimal
                    s = s.replace(".", "").replace(",", ".")
            elif "," in s:
                # Only comma - could be decimal or thousands separator
                parts = s.split(",")
                if len(parts) == 2 and len(parts[1]) <= 2:
                    # Likely decimal separator
                    s = s.replace(",", ".")
                else:
                    # Likely thousands separator
                    s = s.replace(",", "")
            elif "." in s:
                # Only dot - could be decimal or thousands separator
                parts = s.split(".")
                if len(parts) == 2 and len(parts[1]) <= 2:
                    # Likely decimal separator
                    pass  # Keep as is
                else:
                    # Likely thousands separator
                    s = s.replace(".", "")

            try:
                return float(s)
            except ValueError:
                return float("nan")

        return series.apply(parse_amount)

    def find_column_by_candidates(
        self, candidates: List[str], columns: List[str]
    ) -> Optional[str]:
        """Find first matching column from candidates list."""
        for candidate in candidates:
            if candidate in columns:
                return candidate
        return None


class FileIngester:
    """Handles file ingestion operations."""

    def __init__(self):
        self.processor = DataProcessor()

    def read_excel_file(self, file_bytes: bytes) -> Dict[str, Any]:
        """Read Excel file and return processed data."""
        try:
            # Read without header first to find the best header row
            df_sniff = pd.read_excel(
                io.BytesIO(file_bytes), header=None, dtype=str, engine="openpyxl"
            )
            header_row = self.processor.find_header_row(df_sniff)
            prompts = self.processor.extract_prompts_from_header(df_sniff, header_row)

            # Read with proper header
            df = pd.read_excel(
                io.BytesIO(file_bytes), header=header_row, dtype=str, engine="openpyxl"
            )
            df.columns = self.processor.flatten_multiindex_columns(df.columns)

            return {"df": df, "prompts": prompts}

        except Exception as e:
            raise FileProcessingError(f"Failed to read Excel file: {e}")

    def read_csv_file(self, file_bytes: bytes) -> Dict[str, Any]:
        """Read CSV file and return processed data."""
        try:
            # Detect encoding
            encoding = chardet.detect(file_bytes).get("encoding", "utf-8")
            text_content = file_bytes.decode(encoding, errors="replace")

            # Read without header first to find the best header row
            df_sniff = pd.read_csv(
                io.StringIO(text_content),
                header=None,
                dtype=str,
                sep=None,
                engine="python",
            )
            header_row = self.processor.find_header_row(df_sniff)
            prompts = self.processor.extract_prompts_from_header(df_sniff, header_row)

            # Read with proper header
            df = pd.read_csv(
                io.StringIO(text_content),
                header=header_row,
                dtype=str,
                sep=None,
                engine="python",
            )
            df.columns = self.processor.flatten_multiindex_columns(df.columns)

            return {"df": df, "prompts": prompts}

        except Exception as e:
            raise FileProcessingError(f"Failed to read CSV file: {e}")

    def read_table(self, file_bytes: bytes, filename: str) -> Dict[str, Any]:
        """Read table file and return processed data."""
        file_path = Path(filename.lower())

        if file_path.suffix in {".xlsx", ".xls"}:
            result = self.read_excel_file(file_bytes)
        elif file_path.suffix in {".csv", ".tsv", ".txt"}:
            result = self.read_csv_file(file_bytes)
        else:
            raise FileProcessingError(
                f"Unsupported file format: {filename}", filename, file_path.suffix
            )

        df = result["df"]

        # Process date columns
        date_columns = [col for col in df.columns if col.startswith("data")]
        for col in date_columns:
            df[col] = pd.to_datetime(df[col], errors="coerce", dayfirst=True)

        return {
            "df": df,
            "columns": list(df.columns),
            "shape": list(df.shape),
            "prompts": result.get("prompts", []),
        }


class DataAnalyzer:
    """Handles data analysis operations."""

    def __init__(self):
        self.processor = DataProcessor()

    def analyze_table(self, df: pd.DataFrame) -> Dict[str, Any]:
        """Analyze table and extract key metrics."""
        columns = list(df.columns)

        # Find key columns
        date_col = self.processor.find_column_by_candidates(
            [col for col in columns if col.startswith("data")], columns
        )

        amount_candidates = [
            "wartosc_netto_dokumentu",
            "wartosc_brutto_dokumentu",
            "kwota_netto",
            "kwota_brutto",
            "kwota",
            "wartosc_netto",
            "wartosc_brutto",
        ]
        amount_col = self.processor.find_column_by_candidates(
            amount_candidates, columns
        )

        counterparty_candidates = [
            "kontrahent",
            "nabywca",
            "dostawca",
            "klient",
            "sprzedawca",
            "odbiorca",
        ]
        counterparty_col = self.processor.find_column_by_candidates(
            counterparty_candidates, columns
        )

        result = {
            "date_col": date_col,
            "amount_col": amount_col,
            "counterparty_col": counterparty_col,
        }

        # Analyze amounts
        if amount_col is not None:
            amounts = self.processor.parse_amount_series(df[amount_col])
            result["amount_sum"] = float(np.nansum(amounts))
            result["amount_mean"] = float(np.nanmean(amounts))
            result["amount_count"] = int(amounts.notna().sum())
            result["amount_std"] = float(np.nanstd(amounts))

        # Analyze monthly trends
        if date_col is not None and amount_col is not None:
            monthly_data = self._analyze_monthly_trends(df, date_col, amount_col)
            result.update(monthly_data)

        # Analyze counterparties
        if counterparty_col is not None and amount_col is not None:
            counterparty_data = self._analyze_counterparties(
                df, counterparty_col, amount_col
            )
            result.update(counterparty_data)

        return result

    def _analyze_monthly_trends(
        self, df: pd.DataFrame, date_col: str, amount_col: str
    ) -> Dict[str, Any]:
        """Analyze monthly trends in the data."""
        try:
            temp_df = df[[date_col, amount_col]].copy()
            temp_df[amount_col] = self.processor.parse_amount_series(
                temp_df[amount_col]
            )
            temp_df = temp_df.dropna()

            if temp_df.empty:
                return {}

            # Set date as index and resample monthly
            temp_df = temp_df.set_index(date_col)
            monthly_series = temp_df[amount_col].resample("MS").sum().sort_index()

            result = {
                "monthly": [
                    [d.strftime("%Y-%m"), float(v)] for d, v in monthly_series.items()
                ]
            }

            # Calculate month-over-month changes
            if len(monthly_series) >= 2:
                latest = monthly_series.iloc[-1]
                previous = monthly_series.iloc[-2]

                result["mom_abs"] = float(latest - previous)
                result["mom_pct"] = float(
                    (latest - previous) / (previous + 1e-9) * 100.0
                )

            return result

        except Exception as e:
            logger.warning(f"Failed to analyze monthly trends: {e}")
            return {}

    def _analyze_counterparties(
        self, df: pd.DataFrame, counterparty_col: str, amount_col: str
    ) -> Dict[str, Any]:
        """Analyze counterparty data."""
        try:
            temp_df = df.copy()
            temp_df[amount_col] = self.processor.parse_amount_series(
                temp_df[amount_col]
            )

            # Group by counterparty and sum amounts
            counterparty_totals = temp_df.groupby(counterparty_col, dropna=False)[
                amount_col
            ].sum()
            top_counterparties = counterparty_totals.sort_values(ascending=False).head(
                10
            )

            return {
                "top_counterparties": [
                    [str(k), float(v)] for k, v in top_counterparties.items()
                ],
                "counterparty_count": int(counterparty_totals.notna().sum()),
            }

        except Exception as e:
            logger.warning(f"Failed to analyze counterparties: {e}")
            return {}


# Global instances
_data_processor = DataProcessor()
_file_ingester = FileIngester()
_data_analyzer = DataAnalyzer()


def read_table(file_bytes: bytes, filename: str) -> Dict[str, Any]:
    """Convenience function to read table file."""
    return _file_ingester.read_table(file_bytes, filename)


def analyze_table(df: pd.DataFrame) -> Dict[str, Any]:
    """Convenience function to analyze table."""
    return _data_analyzer.analyze_table(df)
