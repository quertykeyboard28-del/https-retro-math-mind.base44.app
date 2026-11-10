"""Deterministic KALKUL8 decision scoring for ME + VAR versus an answer.

This is a transparent numeric decision helper, not a trained AI model. Epsilon
is an absolute error tolerance in the same units as the inputs. Kappa is a
normalized uncertainty/spread penalty in [0, 1].
"""

from dataclasses import asdict, dataclass
import math


@dataclass(frozen=True)
class DecisionResult:
    me: float
    var: float
    answer: float
    candidate: float
    error: float
    epsilon: float
    kappa: float
    equals: bool
    output: int
    confidence: float


def kalkul8_decide(me, var, answer, *, epsilon=1e-9, kappa=0.0):
    """Evaluate candidate ``ME + VAR`` against ``answer``.

    Returns a Boolean equality decision and an integer score from 1 to 9.
    ``equals`` is true exactly when absolute error is within epsilon.
    ``output`` scores closeness on a 1..9 scale; kappa reduces confidence.

    The score is not a probability. It is a deterministic, explainable signal.
    """
    values = {"me": me, "var": var, "answer": answer, "epsilon": epsilon, "kappa": kappa}
    parsed = {}
    for name, value in values.items():
        try:
            number = float(value)
        except (TypeError, ValueError, OverflowError) as exc:
            raise ValueError(f"{name} must be a finite number") from exc
        if not math.isfinite(number):
            raise ValueError(f"{name} must be a finite number")
        parsed[name] = number

    me_value = parsed["me"]
    var_value = parsed["var"]
    answer_value = parsed["answer"]
    epsilon_value = parsed["epsilon"]
    kappa_value = parsed["kappa"]
    if epsilon_value <= 0:
        raise ValueError("epsilon must be greater than zero")
    if not 0 <= kappa_value <= 1:
        raise ValueError("kappa must be between 0 and 1")

    candidate = me_value + var_value
    error = abs(candidate - answer_value)
    equals = error <= epsilon_value

    # Map exact agreement to 9 and the epsilon boundary to about 5; values
    # outside the tolerance trend toward 1. Kappa attenuates this score.
    closeness = max(0.0, 1.0 - error / (2.0 * epsilon_value))
    confidence = closeness * (1.0 - kappa_value)
    output = 1 + math.floor(8.0 * confidence + 0.5)

    return DecisionResult(
        me=me_value,
        var=var_value,
        answer=answer_value,
        candidate=candidate,
        error=error,
        epsilon=epsilon_value,
        kappa=kappa_value,
        equals=equals,
        output=max(1, min(9, output)),
        confidence=confidence,
    )


def result_as_dict(result):
    """Return a JSON-serializable representation of a DecisionResult."""
    return asdict(result)


if __name__ == "__main__":
    # Example: python kalkul8_decision.py
    result = kalkul8_decide(me=8, var=-5, answer=3, epsilon=0.01, kappa=0.1)
    print(result_as_dict(result))
