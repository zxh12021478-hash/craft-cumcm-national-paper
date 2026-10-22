"""Small corrected prediction/feasibility interfaces; no training or SDK call."""
import json
from pathlib import Path


def predict_ovo(features, pair_models, classes):
    """All pair models vote on every feature row; ties choose smaller class."""
    predictions = []
    for row in features:
        votes = {c: 0 for c in classes}
        for c0, c1, weights, bias in pair_models:
            score = sum(w * x for w, x in zip(weights, row)) + bias
            votes[c1 if score > 0 else c0] += 1
        predictions.append(min(classes, key=lambda c: (-votes[c], c)))
    return predictions


def shared_grid_equality(digits, signed_training_labels):
    """With alpha_i=Delta*d_i, Delta!=0, equality is this exact integer sum."""
    if any(type(d) is not int or d < 0 for d in digits):
        raise ValueError("Require nonnegative decoded integers")
    if len(digits) != len(signed_training_labels):
        raise ValueError("Length mismatch")
    if any(y not in (-1, 1) for y in signed_training_labels):
        raise ValueError("Binary training labels must be -1/+1")
    residual = sum(d * y for d, y in zip(digits, signed_training_labels))
    return residual == 0, residual


def main():
    features = [[0., 0.], [1., -1.], [-1., 1.]]
    # Same fixed cycle of pair winners as the original-label-leak counterexample.
    models = [(0, 1, [0., 0.], 1.), (0, 2, [0., 0.], -1.), (1, 2, [0., 0.], 1.)]
    first = predict_ovo(features, models, [0, 1, 2])
    evaluations = []
    for evaluation_labels in ([0, 1, 2], [0, 0, 0], [2, 0, 1]):
        repeated = predict_ovo(features, models, [0, 1, 2])
        assert repeated == first == [0, 0, 0]
        evaluations.append({"evaluation_labels": evaluation_labels, "predictions": repeated})
    # This fixture needs the third classifier: two votes tie at class0,
    # the third breaks the tie in favor of class1. Invariance alone would
    # not detect a predictor silently dropping the third classifier.
    decisive_models = models[:2] + [(1, 2, [0., 0.], -1.)]
    two_only = predict_ovo(features, decisive_models[:2], [0, 1, 2])
    all_three = predict_ovo(features, decisive_models, [0, 1, 2])
    assert two_only == [0, 0, 0] and all_three == [1, 1, 1]
    assert shared_grid_equality([1, 1], [-1, 1]) == (True, 0)
    assert shared_grid_equality([1, 2], [-1, 1]) == (False, 1)
    result = {
        "scope": "Root independently implemented corrected interfaces on frozen toy models; not a repaired Iris training pipeline or measured accuracy",
        "label_invariance": evaluations,
        "third_classifier_decisive": {"two_only":two_only, "all_three":all_three},
        "integer_grid": {"balanced": list(shared_grid_equality([1, 1], [-1, 1])), "one_LSB_violation": list(shared_grid_equality([1, 2], [-1, 1]))},
        "training_runs": 0, "SDK_runs": 0,
    }
    (Path(__file__).parent / "minimal-contract-results.json").write_text(json.dumps(result, indent=2) + "\n")
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
