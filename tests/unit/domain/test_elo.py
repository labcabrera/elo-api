import pytest

from src.domain.services.elo import calculate_elo


def test_elo_equal_ratings_a_wins():
    a, b = 1500.0, 1500.0
    new_a, new_b = calculate_elo(a, b, k=32.0, result_a=1.0)
    assert new_a == 1516.0
    assert new_b == 1484.0


def test_elo_equal_ratings_b_wins():
    a, b = 1500.0, 1500.0
    new_a, new_b = calculate_elo(a, b, k=32.0, result_a=0.0)
    assert new_a == 1484.0
    assert new_b == 1516.0


def test_elo_draw_different_ratings():
    a, b = 1600.0, 1500.0
    new_a, new_b = calculate_elo(a, b, k=32.0, result_a=0.5)
    # Expected values computed via formula
    # E_A = 1 / (1 + 10^((1500-1600)/400)) ~= 0.359935
    # R'_A = 1600 + 32 * (0.5 - E_A) ~= 1600 + 32*(0.140065) ~= 1604.4819
    assert round(new_a, 4) == round(1604.4819, 4)
    assert round(new_b, 4) == round(1395.5181, 4)
