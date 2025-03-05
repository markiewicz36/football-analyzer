from typing import Dict, List, Tuple


class EloRating:
    """
    System rankingowy Elo do oceny siły drużyn.
    """

    def __init__(self, default_rating: int = 1500, k_factor: int = 40):
        """
        Inicjalizuje system Elo.

        Args:
            default_rating: Domyślny rating początkowy dla nowych drużyn
            k_factor: Współczynnik K określający maksymalną zmianę ratingu po meczu
        """
        self.ratings = {}  # Słownik z ratingami drużyn
        self.default_rating = default_rating
        self.k_factor = k_factor
        self.home_advantage = 100  # Bonus punktowy za grę u siebie

    def get_rating(self, team: str) -> int:
        """
        Zwraca aktualny rating drużyny.

        Args:
            team: Nazwa drużyny

        Returns:
            Rating Elo drużyny
        """
        return self.ratings.get(team, self.default_rating)

    def calculate_expected_score(self, team_a: str, team_b: str, team_a_home: bool = False) -> float:
        """
        Oblicza oczekiwany wynik meczu dla team_a.

        Args:
            team_a: Pierwsza drużyna
            team_b: Druga drużyna
            team_a_home: Czy team_a gra u siebie

        Returns:
            Oczekiwana wartość (0-1) dla team_a
        """
        rating_a = self.get_rating(team_a)
        rating_b = self.get_rating(team_b)

        # Dodaj bonus za grę u siebie
        if team_a_home:
            rating_a += self.home_advantage

        # Wzór Elo na oczekiwany wynik
        expected = 1 / (1 + 10 ** ((rating_b - rating_a) / 400))
        return expected

    def update_ratings(self, home_team: str, away_team: str, result: str,
                       importance: float = 1.0) -> Tuple[int, int]:
        """
        Aktualizuje ratingi po meczu.

        Args:
            home_team: Drużyna gospodarzy
            away_team: Drużyna gości
            result: Wynik meczu ('home_win', 'away_win', 'draw')
            importance: Współczynnik ważności meczu (1.0 dla normalnego meczu)

        Returns:
            Tuple (nowy rating gospodarzy, nowy rating gości)
        """
        # Pobierz aktualne ratingi
        home_rating = self.get_rating(home_team)
        away_rating = self.get_rating(away_team)

        # Rzeczywisty wynik
        if result == 'home_win':
            actual_home = 1.0
            actual_away = 0.0
        elif result == 'away_win':
            actual_home = 0.0
            actual_away = 1.0
        else:  # draw
            actual_home = 0.5
            actual_away = 0.5

        # Oczekiwane wyniki
        expected_home = self.calculate_expected_score(home_team, away_team, True)
        expected_away = self.calculate_expected_score(away_team, home_team, False)

        # Oblicz nowe ratingi
        adjusted_k = self.k_factor * importance

        new_home_rating = round(home_rating + adjusted_k * (actual_home - expected_home))
        new_away_rating = round(away_rating + adjusted_k * (actual_away - expected_away))

        # Aktualizuj ratingi
        self.ratings[home_team] = new_home_rating
        self.ratings[away_team] = new_away_rating

        return new_home_rating, new_away_rating

    def predict_match(self, home_team: str, away_team: str) -> Dict:
        """
        Przewiduje wynik meczu na podstawie ratingów Elo.

        Args:
            home_team: Drużyna gospodarzy
            away_team: Drużyna gości

        Returns:
            Słownik z prawdopodobieństwami wyników
        """
        # Oczekiwany wynik dla gospodarzy
        expected_home = self.calculate_expected_score(home_team, away_team, True)

        # Prawdopodobieństwa 1X2
        # Uwaga: To jest uproszczenie. W rzeczywistości relacja między
        # oczekiwanym wynikiem Elo a prawdopodobieństwami 1X2 jest bardziej złożona.
        p_draw = 0.3  # Stałe prawdopodobieństwo remisu (można udoskonalić)
        p_home = expected_home * (1 - p_draw)
        p_away = (1 - expected_home) * (1 - p_draw)

        # Normalizacja
        total = p_home + p_draw + p_away
        p_home /= total
        p_draw /= total
        p_away /= total

        return {
            'home_win': float(p_home),
            'draw': float(p_draw),
            'away_win': float(p_away),
            'home_team_rating': self.get_rating(home_team),
            'away_team_rating': self.get_rating(away_team),
            'expected_score': float(expected_home)
        }

    def bulk_update(self, matches: List[Dict]):
        """
        Aktualizuje ratingi na podstawie listy meczów.

        Args:
            matches: Lista słowników z danymi o meczach
                {'home_team': str, 'away_team': str, 'result': str, 'importance': float}
        """
        for match in matches:
            home_team = match['home_team']
            away_team = match['away_team']
            result = match['result']
            importance = match.get('importance', 1.0)

            self.update_ratings(home_team, away_team, result, importance)