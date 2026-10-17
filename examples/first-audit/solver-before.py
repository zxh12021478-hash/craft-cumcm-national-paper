"""Intentionally flawed heuristic for an audit demonstration."""
import json


def solve():
    # Bug: ignores A's capacity limit of 6.
    a, b = 8, 2
    return {"a": a, "b": b, "cost": 2 * a + 5 * b}


if __name__ == "__main__":
    print(json.dumps(solve()))
