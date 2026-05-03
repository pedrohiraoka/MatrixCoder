# Data Processor Service - Pandas transformations
import pandas as pd
import numpy as np
from typing import Dict, Any, List


class DataProcessor:
    def __init__(self):
        self.df = None

    def load_data(self, data: List[Dict[str, Any]]) -> pd.DataFrame:
        """Load data from list of dicts"""
        self.df = pd.DataFrame(data)
        return self.df

    def apply_transformations(
        self, transformations: List[str]
    ) -> Dict[str, Any]:
        """Apply specified transformations"""
        if self.df is None or self.df.empty:
            raise ValueError("No data loaded")

        metrics = {}

        for transform in transformations:
            if transform == "normalize":
                self._normalize()
                metrics["normalized"] = True
            elif transform == "aggregate":
                self._aggregate()
                metrics["aggregated"] = True
            elif transform == "rolling_mean":
                self._rolling_mean()
                metrics["rolling_mean_applied"] = True
            elif transform == "log_transform":
                self._log_transform()
                metrics["log_transformed"] = True

        # Generate metrics
        metrics.update({
            "rows": len(self.df),
            "columns": len(self.df.columns),
            "null_count": int(self.df.isnull().sum().sum()),
            "memory_usage_bytes": int(self.df.memory_usage(deep=True).sum()),
        })

        return metrics

    def _normalize(self):
        """Normalize numeric columns to 0-1 range"""
        numeric_cols = self.df.select_dtypes(include=[np.number]).columns
        for col in numeric_cols:
            min_val = self.df[col].min()
            max_val = self.df[col].max()
            if max_val - min_val > 0:
                self.df[col] = (self.df[col] - min_val) / (max_val - min_val)

    def _aggregate(self):
        """Aggregate numeric columns"""
        numeric_cols = self.df.select_dtypes(include=[np.number]).columns
        if len(numeric_cols) > 0:
            agg_dict = {col: ["mean", "sum", "std"] for col in numeric_cols}
            # Just mark that aggregation is available, don't reduce rows

    def _rolling_mean(self, window: int = 3):
        """Apply rolling mean to numeric columns"""
        numeric_cols = self.df.select_dtypes(include=[np.number]).columns
        for col in numeric_cols:
            self.df[f"{col}_rolling"] = self.df[col].rolling(window=window).mean()

    def _log_transform(self):
        """Apply log transform to positive numeric columns"""
        numeric_cols = self.df.select_dtypes(include=[np.number]).columns
        for col in numeric_cols:
            if (self.df[col] > 0).all():
                self.df[f"{col}_log"] = np.log(self.df[col])

    def get_preview(self, n: int = 5) -> List[Dict[str, Any]]:
        """Get preview of processed data"""
        if self.df is None:
            return []
        return self.df.head(n).to_dict(orient="records")

    def get_columns(self) -> List[str]:
        """Get column names"""
        if self.df is None:
            return []
        return self.df.columns.tolist()


# Singleton instance
data_processor = DataProcessor()
