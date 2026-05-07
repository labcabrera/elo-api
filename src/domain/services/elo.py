from typing import Tuple
import math


def expected_score(rating_a: float, rating_b: float) -> float:
    """Return expected score for player A against player B."""
    return 1.0 / (1.0 + math.pow(10.0, (rating_b - rating_a) / 400.0))


def calculate_elo(rating_a: float, rating_b: float, k: float = 32.0, result_a: float = 1.0) -> Tuple[float, float]:
    """
    Calculate new ELO ratings for two players.

    Args:
        rating_a: current rating of player A
        rating_b: current rating of player B
        k: k-factor to apply (per-league)
        result_a: actual score for A (1.0 = A win, 0.5 = draw, 0.0 = A loss)

    Returns:
        (new_rating_a, new_rating_b)

    Deterministic and follows standard ELO formula:
        R'_A = R_A + K * (S_A - E_A)
        R'_B = R_B + K * (S_B - E_B)
    where S_B = 1 - S_A for win/loss or equal to S_A when draw handled accordingly.
    """
    ea = expected_score(rating_a, rating_b)
    eb = expected_score(rating_b, rating_a)

    sa = float(result_a)
    sb = 1.0 - sa

    new_a = rating_a + k * (sa - ea)
    new_b = rating_b + k * (sb - eb)

    # Keep numeric stability: round to 4 decimal places
    return (round(new_a, 4), round(new_b, 4))
