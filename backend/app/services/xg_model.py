import numpy as np
import pandas as pd
from typing import Dict, List, Any, Tuple
from sklearn.ensemble import RandomForestClassifier


class XGModel:
    """
    Model Expected Goals (xG) do oceny jakości sytuacji strzeleckich.
    """

    def __init__(self):
        """Inicjalizuje model xG."""
        self.model = RandomForestClassifier(n_estimators=100, random_state=42)
        self.is_trained = False

    def _extract_features(self, shot_data: Dict[str, Any]) -> List[float]:
        """
        Wyodrębnia cechy ze zdarzenia strzeleckiego.

        Args:
            shot_data: Dane o strzale

        Returns:
            Lista cech do modelu
        """
        # Przykładowe cechy - w rzeczywistości można użyć więcej
        features = [
            shot_data.get('distance', 0),  # Odległość od bramki
            shot_data.get('angle', 0),  # Kąt do bramki
            shot_data.get('is_big_chance', 0),  # Czy duża szansa
            shot_data.get('is_header', 0),  # Czy strzał głową
            shot_data.get('is_foot', 0),  # Czy strzał nogą
            shot_data.get('defenders_between', 0),  # Liczba obrońców między strzelcem a bramką
            shot_data.get('is_fast_break', 0),  # Czy kontratak
            shot_data.get('goalkeeper_distance', 0),  # Odległość bramkarza
        ]
        return features

    def train(self, shots_data: List[Dict[str, Any]]):
        """
        Trenuje model xG na podstawie historycznych danych o strzałach.

        Args:
            shots_data: Lista słowników z danymi o strzałach
                Każdy słownik powinien zawierać cechy strzału i informację czy był gol
        """
        X = []
        y = []

        for shot in shots_data:
            features = self._extract_features(shot)
            is_goal = shot.get('is_goal', 0)

            X.append(features)
            y.append(is_goal)

        if len(X) > 0:
            self.model.fit(X, y)
            self.is_trained = True

    def predict_xg(self, shot_data: Dict[str, Any]) -> float:
        """
        Przewiduje wartość xG dla pojedynczego strzału.

        Args:
            shot_data: Słownik z danymi o strzale

        Returns:
            Wartość xG (0-1)
        """
        if not self.is_trained:
            # Fallback jeśli model nie jest wytrenowany
            return self._simple_xg_estimation(shot_data)

        features = [self._extract_features(shot_data)]
        return float(self.model.predict_proba(features)[0][1])

    def _simple_xg_estimation(self, shot_data: Dict[str, Any]) -> float:
        """
        Prosta estymacja xG oparta na heurystyce.
        Używana jako fallback gdy model nie jest wytrenowany.

        Args:
            shot_data: Słownik z danymi o strzale

        Returns:
            Wartość xG (0-1)
        """
        # Podstawowe wartości
        distance = shot_data.get('distance', 18)  # W metrach
        angle = shot_data.get('angle', 45)  # W stopniach
        is_big_chance = shot_data.get('is_big_chance', 0)
        is_header = shot_data.get('is_header', 0)

        # Zależność xG od odległości (uproszczona formuła)
        distance_factor = max(0, 1 - (distance / 30))

        # Zależność xG od kąta
        max_angle = 90
        angle_factor = 1 - abs(angle) / max_angle

        # Bonus za "dużą szansę"
        big_chance_bonus = 0.3 if is_big_chance else 0

        # Kara za strzał głową
        header_penalty = 0.2 if is_header else 0

        # Podstawowa wartość xG
        base_xg = distance_factor * angle_factor

        # Całkowita wartość xG
        xg = base_xg + big_chance_bonus - header_penalty

        # Ograniczenie do przedziału [0,1]
        return max(0, min(1, xg))

    def calculate_match_xg(self, home_shots: List[Dict[str, Any]],
                           away_shots: List[Dict[str, Any]]) -> Tuple[float, float]:
        """
        Oblicza łączne xG dla obu drużyn w meczu.

        Args:
            home_shots: Lista strzałów drużyny gospodarzy
            away_shots: Lista strzałów drużyny gości

        Returns:
            Tuple (xG gospodarzy, xG gości)
        """
        home_xg = sum(self.predict_xg(shot) for shot in home_shots)
        away_xg = sum(self.predict_xg(shot) for shot in away_shots)

        return home_xg, away_xg