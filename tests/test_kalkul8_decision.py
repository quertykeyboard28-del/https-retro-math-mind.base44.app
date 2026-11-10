import pytest

from kalkul8_decision import kalkul8_decide


def test_exact_sum_is_equal_and_high_score():
    result = kalkul8_decide(8, -5, 3, epsilon=0.01, kappa=0)
    assert result.candidate == 3
    assert result.equals is True
    assert result.output == 9


def test_epsilon_controls_boolean_equality():
    assert kalkul8_decide(2, 2, 4.05, epsilon=0.1).equals is True
    assert kalkul8_decide(2, 2, 4.2, epsilon=0.1).equals is False


def test_kappa_reduces_score_not_boolean_result():
    confident = kalkul8_decide(4, 5, 9, epsilon=1, kappa=0)
    uncertain = kalkul8_decide(4, 5, 9, epsilon=1, kappa=1)
    assert confident.equals == uncertain.equals
    assert confident.output > uncertain.output
    assert uncertain.output == 1


@pytest.mark.parametrize("kwargs", [
    {"epsilon": 0},
    {"epsilon": -1},
    {"kappa": -0.1},
    {"kappa": 1.1},
    {"me": float("nan")},
    {"answer": float("inf")},
])
def test_invalid_inputs_are_rejected(kwargs):
    values = {"me": 1, "var": 2, "answer": 3, "epsilon": 0.01, "kappa": 0}
    values.update(kwargs)
    with pytest.raises(ValueError):
        kalkul8_decide(**values)
