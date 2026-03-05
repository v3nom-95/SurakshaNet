from __future__ import annotations

from dataclasses import dataclass

import numpy as np
import pandas as pd
from sklearn.ensemble import IsolationForest
from sklearn.neighbors import LocalOutlierFactor
from sklearn.preprocessing import MinMaxScaler


@dataclass
class AnomalyResults:
    scores_iforest: np.ndarray
    labels_iforest: np.ndarray
    scores_lof: np.ndarray
    labels_lof: np.ndarray
    combined_score: np.ndarray


class AnomalyDetector:
    """
    Wrapper around Isolation Forest and Local Outlier Factor for unsupervised anomaly detection.
    """

    def __init__(
        self,
        contamination: float = 0.1,
        random_state: int | None = 42,
    ) -> None:
        self.contamination = contamination
        self.random_state = random_state
        self.iforest = IsolationForest(
            n_estimators=200,
            contamination=contamination,
            random_state=random_state,
            n_jobs=-1,
        )
        self.lof = LocalOutlierFactor(
            n_neighbors=20,
            contamination=contamination,
            novelty=False,
            n_jobs=-1,
        )
        self.scaler_scores = MinMaxScaler()

    def fit_predict(self, X: pd.DataFrame) -> AnomalyResults:
        """
        Fit both models and produce anomaly scores and labels.

        Returns higher scores for more anomalous points (0-1 scaled).
        """
        X_np = X.to_numpy(dtype=float)

        # Isolation Forest: decision_function gives higher values for normal points.
        self.iforest.fit(X_np)
        if_scores_raw = -self.iforest.decision_function(X_np)  # invert so higher = more anomalous
        if_labels = (self.iforest.predict(X_np) == -1).astype(int)

        # Local Outlier Factor: negative_outlier_factor_, more negative = more anomalous.
        lof_labels = self.lof.fit_predict(X_np)
        lof_scores_raw = -self.lof.negative_outlier_factor_
        lof_labels_bin = (lof_labels == -1).astype(int)

        # Scale each score type to [0, 1]
        stacked = np.vstack([if_scores_raw, lof_scores_raw]).T
        stacked_scaled = self.scaler_scores.fit_transform(stacked)
        if_scores_scaled = stacked_scaled[:, 0]
        lof_scores_scaled = stacked_scaled[:, 1]

        # Combined score as simple average
        combined_score = (if_scores_scaled + lof_scores_scaled) / 2.0

        return AnomalyResults(
            scores_iforest=if_scores_scaled,
            labels_iforest=if_labels,
            scores_lof=lof_scores_scaled,
            labels_lof=lof_labels_bin,
            combined_score=combined_score,
        )

