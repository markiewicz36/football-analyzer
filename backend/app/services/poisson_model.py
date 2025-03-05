import numpy as np
import pandas as pd
from scipy import stats
from typing import Dict, List, Tuple


class PoissonModel:
    """
    Implementacja modelu Poissona do przewidywania wyników meczów piłkarskich.
    Model wykorzystuje rozkład Poissona do modelowania liczby goli strzelonych przez drużyny.
    """

    def __init__(self):
        self.team_attack = {}  # Siła ataku drużyn
        self.team_defense = {}  # Siła obrony drużyn
        self.home_advantage = 1.35  # Współczynnik przewagi gospodarzy

    def fit(self, historical_matches: List[Dict]):
        """
        Trenuje model na historycznych danych meczowych.

        Args:
            historical_matches: Lista słowników zawierających dane o meczach
                {'home_team': str, 'away_team': str, 'home_goals': int, 'away_goals': int}
        """
        df = pd.DataFrame(historical_matches)

        # Oblicz średnią liczbę goli na mecz
        avg_goals = (df['home_goals'].sum() + df['away_goals'].sum()) / (len(df) * 2)

        # Inicjalizuj wartości domyślne dla wszystkich drużyn
        all_teams = set(df['home_team']).union(set(df['away_team']))
        self.team_attack = {team: 1.0 for team in all_teams}
        self.team_defense = {team: 1.0 for team in all_teams}

        # Trenuj model - prosta implementacja
        # (można rozszerzyć o bardziej zaawansowane metody jak Dixon-Coles)
        for _ in range(5):  # Kilka iteracji dla lepszej zbieżności
            for team in all_teams:
                # Kiedy drużyna gra u siebie
                home_matches = df[df['home_team'] == team]
                if not home_matches.empty:
                    home_goals = home_matches['home_goals'].sum()
                    home_games = len(home_matches)

                    expected_goals = sum(
                        self.team_attack[team] * self.team_defense[away_team] * self.home_advantage * avg_goals
                        for away_team in home_matches['away_team']
                    )

                    if expected_goals > 0:
                        self.team_attack[team] *= home_goals / expected_goals

                # Kiedy drużyna gra na wyjeździe
                away_matches = df[df['away_team'] == team]
                if not away_matches.empty:
                    away_goals = away_matches['away_goals'].sum()
                    away_games = len(away_matches)

                    expected_goals = sum(
                        self.team_attack[team] * self.team_defense[home_team] * avg_goals
                        for home_team in away_matches['home_team']
                    )

                    if expected_goals > 0:
                        self.team_attack[team] *= away_goals / expected_goals

            # Normalizacja, aby średni atak i obrona były równe 1
            attack_mean = sum(self.team_attack.values()) / len(all_teams)
            for team in all_teams:
                self.team_attack[team] /= attack_mean

            defense_mean = sum(self.team_defense.values()) / len(all_teams)
            for team in all_teams:
                self.team_defense[team] /= defense_mean

    def predict_score(self, home_team: str, away_team: str) -> Tuple[float, float]:
        """
        Przewiduje średnią liczbę goli dla obu drużyn.

        Args:
            home_team: Nazwa drużyny gospodarzy
            away_team: Nazwa drużyny gości

        Returns:
            Tuple z przewidywaną średnią liczbą goli dla gospodarzy i gości
        """
        # Średnia liczba goli w lidze (można pobrać z danych)
        avg_goals = 2.75

        # Przewidywana liczba goli dla gospodarzy
        home_expect = (
                self.team_attack.get(home_team, 1.0) *
                self.team_defense.get(away_team, 1.0) *
                self.home_advantage *
                avg_goals / 2
        )

        # Przewidywana liczba goli dla gości
        away_expect = (
                self.team_attack.get(away_team, 1.0) *
                self.team_defense.get(home_team, 1.0) *
                avg_goals / 2
        )

        return home_expect, away_expect

    def predict_match_result(self, home_team: str, away_team: str, max_goals: int = 10) -> Dict:
        """
        Przewiduje rozkład prawdopodobieństw dla wszystkich możliwych wyników meczu.

        Args:
            home_team: Nazwa drużyny gospodarzy
            away_team: Nazwa drużyny gości
            max_goals: Maksymalna liczba goli uwzględniana w obliczeniach

        Returns:
            Słownik z prawdopodobieństwami dla 1X2 i dokładnych wyników
        """
        home_expect, away_expect = self.predict_score(home_team, away_team)

        # Macierz prawdopodobieństw dla wszystkich wyników
        result_probs = np.zeros((max_goals + 1, max_goals + 1))

        # Wypełnij macierz prawdopodobieństw
        for i in range(max_goals + 1):
            for j in range(max_goals + 1):
                result_probs[i, j] = (
                        stats.poisson.pmf(i, home_expect) *
                        stats.poisson.pmf(j, away_expect)
                )

        # Prawdopodobieństwa 1X2
        home_win_prob = np.sum(np.tril(result_probs, -1))  # Gospodarze wygrywają
        draw_prob = np.sum(np.diag(result_probs))  # Remis
        away_win_prob = np.sum(np.triu(result_probs, 1))  # Goście wygrywają

        # Najczęstsze wyniki
        most_likely_scores = []
        flat_indices = np.argsort(result_probs.flatten())[::-1][:5]  # Top 5 wyników
        rows, cols = np.unravel_index(flat_indices, result_probs.shape)

        for i, j in zip(rows, cols):
            most_likely_scores.append({
                'score': f"{i}:{j}",
                'probability': float(result_probs[i, j])
            })

        # Prawdopodobieństwo over/under dla różnych progów
        over_under_probs = {}
        for threshold in [0.5, 1.5, 2.5, 3.5, 4.5]:
            under_prob = 0
            for i in range(max_goals + 1):
                for j in range(max_goals + 1):
                    if i + j < threshold:
                        under_prob += result_probs[i, j]
            over_under_probs[f"over_{threshold}"] = 1 - under_prob
            over_under_probs[f"under_{threshold}"] = under_prob

        # Prawdopodobieństwo both teams to score (BTTS)
        btts_yes = 0
        for i in range(1, max_goals + 1):
            for j in range(1, max_goals + 1):
                btts_yes += result_probs[i, j]

        return {
            'home_win': float(home_win_prob),
            'draw': float(draw_prob),
            'away_win': float(away_win_prob),
            'expected_goals': {
                'home': float(home_expect),
                'away': float(away_expect)
            },
            'most_likely_scores': most_likely_scores,
            'over_under': over_under_probs,
            'btts': {
                'yes': float(btts_yes),
                'no': float(1 - btts_yes)
            }
        }