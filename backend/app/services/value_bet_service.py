from typing import Dict, List, Any, Tuple
import math


class ValueBetAnalyzer:
    """
    Analizator value betów - wykrywa zakłady o dodatniej wartości oczekiwanej.
    """

    def __init__(self, min_value_threshold: float = 0.05):
        """
        Inicjalizuje analizator value betów.

        Args:
            min_value_threshold: Minimalny próg value (5% = 0.05)
        """
        self.min_value_threshold = min_value_threshold

    @staticmethod
    def implied_probability(odds: float) -> float:
        """
        Oblicza prawdopodobieństwo implikowane przez kurs bukmacherski.

        Args:
            odds: Kurs bukmacherski (np. 1.85)

        Returns:
            Prawdopodobieństwo implikowane (0-1)
        """
        return 1 / odds

    def calculate_value(self, model_probability: float, bookmaker_odds: float) -> float:
        """
        Oblicza value dla zakładu.

        Args:
            model_probability: Prawdopodobieństwo według modelu (0-1)
            bookmaker_odds: Kurs bukmacherski

        Returns:
            Wartość value (wartość oczekiwana - 1)
        """
        implied_prob = self.implied_probability(bookmaker_odds)

        # Value = (prawdopodobieństwo modelu * kurs) - 1
        return (model_probability * bookmaker_odds) - 1

    def analyze_1x2_market(self, match_prediction: Dict, bookmaker_odds: Dict) -> Dict:
        """
        Analizuje rynek 1X2 pod kątem value betów.

        Args:
            match_prediction: Słownik z prawdopodobieństwami według modelu
                {'home_win': float, 'draw': float, 'away_win': float}
            bookmaker_odds: Słownik z kursami bukmacherskimi
                {'home_win': float, 'draw': float, 'away_win': float}

        Returns:
            Słownik z analizą value betów
        """
        result = {}

        # Analiza zakładu na zwycięstwo gospodarzy
        home_value = self.calculate_value(
            match_prediction['home_win'],
            bookmaker_odds['home_win']
        )

        # Analiza zakładu na remis
        draw_value = self.calculate_value(
            match_prediction['draw'],
            bookmaker_odds['draw']
        )

        # Analiza zakładu na zwycięstwo gości
        away_value = self.calculate_value(
            match_prediction['away_win'],
            bookmaker_odds['away_win']
        )

        # Zapisz wyniki
        result['home_win'] = {
            'model_probability': match_prediction['home_win'],
            'implied_probability': self.implied_probability(bookmaker_odds['home_win']),
            'odds': bookmaker_odds['home_win'],
            'value': home_value,
            'is_value_bet': home_value > self.min_value_threshold
        }

        result['draw'] = {
            'model_probability': match_prediction['draw'],
            'implied_probability': self.implied_probability(bookmaker_odds['draw']),
            'odds': bookmaker_odds['draw'],
            'value': draw_value,
            'is_value_bet': draw_value > self.min_value_threshold
        }

        result['away_win'] = {
            'model_probability': match_prediction['away_win'],
            'implied_probability': self.implied_probability(bookmaker_odds['away_win']),
            'odds': bookmaker_odds['away_win'],
            'value': away_value,
            'is_value_bet': away_value > self.min_value_threshold
        }

        # Znalezienie najlepszego value beta
        best_value = max(home_value, draw_value, away_value)

        if best_value == home_value:
            result['best_value_bet'] = 'home_win'
        elif best_value == draw_value:
            result['best_value_bet'] = 'draw'
        else:
            result['best_value_bet'] = 'away_win'

        result['has_value_bet'] = best_value > self.min_value_threshold

        return result

    def analyze_over_under_market(self, match_prediction: Dict, bookmaker_odds: Dict) -> Dict:
        """
        Analizuje rynek over/under pod kątem value betów.

        Args:
            match_prediction: Słownik z prawdopodobieństwami według modelu
                {'over_2.5': float, 'under_2.5': float, ...}
            bookmaker_odds: Słownik z kursami bukmacherskimi
                {'over_2.5': float, 'under_2.5': float, ...}

        Returns:
            Słownik z analizą value betów
        """
        result = {}
        best_value = -1
        best_value_bet = None

        # Analizuj każdy rynek over/under
        for market in match_prediction:
            if market in bookmaker_odds:
                model_prob = match_prediction[market]
                odds = bookmaker_odds[market]

                value = self.calculate_value(model_prob, odds)

                result[market] = {
                    'model_probability': model_prob,
                    'implied_probability': self.implied_probability(odds),
                    'odds': odds,
                    'value': value,
                    'is_value_bet': value > self.min_value_threshold
                }

                # Sprawdź czy to najlepszy value bet
                if value > best_value:
                    best_value = value
                    best_value_bet = market

        result['best_value_bet'] = best_value_bet
        result['has_value_bet'] = best_value > self.min_value_threshold

        return result

    def find_value_bets(self, fixtures: List[Dict]) -> List[Dict]:
        """
        Znajduje value bety wśród listy meczów.

        Args:
            fixtures: Lista słowników z danymi o meczach
                Każdy mecz zawiera predykcje modelu i kursy bukmacherskie

        Returns:
            Lista meczów z value betami
        """
        value_bets = []

        for fixture in fixtures:
            value_analysis = {
                'fixture_id': fixture.get('id'),
                'home_team': fixture.get('home_team'),
                'away_team': fixture.get('away_team'),
                'league': fixture.get('league'),
                'match_date': fixture.get('match_date'),
                'markets': {}
            }

            # Analizuj rynek 1X2
            if 'model_1x2' in fixture and 'odds_1x2' in fixture:
                value_analysis['markets']['1x2'] = self.analyze_1x2_market(
                    fixture['model_1x2'],
                    fixture['odds_1x2']
                )

            # Analizuj rynek over/under
            if 'model_over_under' in fixture and 'odds_over_under' in fixture:
                value_analysis['markets']['over_under'] = self.analyze_over_under_market(
                    fixture['model_over_under'],
                    fixture['odds_over_under']
                )

            # Sprawdź czy jakikolwiek rynek ma value bet
            has_value_bet = any(
                market.get('has_value_bet', False)
                for market in value_analysis['markets'].values()
            )

            if has_value_bet:
                value_analysis['has_value_bet'] = True
                value_bets.append(value_analysis)

        return value_bets