# ML Engine Service - Isolation Forest for Anomaly Detection
import numpy as np
import pandas as pd
from sklearn.ensemble import IsolationForest
from sklearn.preprocessing import StandardScaler
import time
from typing import Dict, Any, Tuple


class MLEngine:
    def __init__(self):
        self.model = None
        self.scaler = StandardScaler()

    def generate_synthetic_data(
        self, n_samples: int, n_features: int, contamination: float
    ) -> Tuple[pd.DataFrame, np.ndarray]:
        """Generate synthetic data with injected anomalies"""
        np.random.seed(42)  # Reproducibility for demo

        # Normal data
        n_normal = int(n_samples * (1 - contamination))
        normal_data = np.random.randn(n_normal, n_features)

        # Anomalous data
        n_anomalies = n_samples - n_normal
        anomaly_data = np.random.randn(n_anomalies, n_features) * 3 + 5

        # Combine
        X = np.vstack([normal_data, anomaly_data])
        true_labels = np.array([0] * n_normal + [1] * n_anomalies)

        # Shuffle
        indices = np.random.permutation(n_samples)
        X = X[indices]
        true_labels = true_labels[indices]

        # Create DataFrame
        columns = [f"feature_{i}" for i in range(n_features)]
        df = pd.DataFrame(X, columns=columns)

        return df, true_labels

    def detect_anomalies(
        self, df: pd.DataFrame, contamination: float = 0.1
    ) -> Dict[str, Any]:
        """Run Isolation Forest and return results"""
        start_time = time.time()

        # Scale data
        X_scaled = self.scaler.fit_transform(df)

        # Train model
        self.model = IsolationForest(
            contamination=contamination,
            random_state=42,
            n_estimators=100,
        )
        predictions = self.model.fit_predict(X_scaled)
        scores = self.model.score_samples(X_scaled)

        # Convert predictions: -1 = anomaly, 1 = normal
        anomaly_mask = predictions == -1
        n_anomalies = np.sum(anomaly_mask)

        processing_time = (time.time() - start_time) * 1000

        # Statistics
        summary_stats = {
            "mean": df.mean().to_dict(),
            "std": df.std().to_dict(),
            "min": df.min().to_dict(),
            "max": df.max().to_dict(),
        }

        return {
            "total_samples": len(df),
            "anomalies_detected": int(n_anomalies),
            "anomaly_percentage": float(n_anomalies / len(df) * 100),
            "model_score": float(np.mean(scores)),
            "processing_time_ms": round(processing_time, 2),
            "summary_stats": summary_stats,
            "anomaly_indices": np.where(anomaly_mask)[0].tolist()[:10],  # Top 10
        }


# Singleton instance
ml_engine = MLEngine()
