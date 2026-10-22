"""Small independent identities/counterexamples, never a Kaiwu execution claim."""
import ast
import itertools
import json
from fractions import Fraction
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parent
RAW = ROOT / "frozen-producer-output" / "probes"


def functions(path, names, namespace):
    tree = ast.parse(path.read_text())
    selected = [n for n in tree.body if isinstance(n, ast.FunctionDef) and n.name in names]
    assert {n.name for n in selected} == set(names)
    exec(compile(ast.Module(body=selected, type_ignores=[]), str(path), "exec"), namespace)
    return namespace


def bitstrings(n):
    return np.array(list(itertools.product([0.0, 1.0], repeat=n)))


def main():
    util = functions(RAW / "qubo_sa.py", ["qubo_from_linear_quadratic", "energy_ols_bits", "to_kaiwu_upper"], {"np": np})
    X = np.array([[1., 0.], [1., 1.], [1., 2.]])
    target = np.array([0.2, 1.1, 1.9])
    Q, decode, offset = util["energy_ols_bits"](X, target, [(-1., 1.), (-1., 1.)], 3)
    ar_errors = []
    upper_errors = []
    U = util["to_kaiwu_upper"](Q)
    for bits in bitstrings(6):
        actual = float(np.sum((X @ decode(bits) - target) ** 2))
        ar_errors.append(abs(actual - float(bits @ Q @ bits + offset)))
        upper_errors.append(abs(float(bits @ Q @ bits - bits @ U @ bits)))

    svm = functions(RAW / "probe_task2_svm.py", ["kernel", "svm_qubo", "decode_alpha"], {"np": np, "qubo_from_linear_quadratic": util["qubo_from_linear_quadratic"]})
    points = np.array([[0., 1.], [1., 0.], [1., 1.]])
    labels = np.array([-1., 1., 1.])
    K = points @ points.T
    sq, D, delta = svm["svm_qubo"](K, labels, 1., 2, 2.)
    svm_errors = []
    for bits in bitstrings(6):
        alpha = D @ bits
        signed = alpha * labels
        direct = .5 * signed @ K @ signed - alpha.sum() + 2. * (alpha @ labels) ** 2
        svm_errors.append(abs(float(direct - bits @ sq @ bits)))

    bnn = functions(RAW / "probe_task3_bnn.py", ["head_qubo"], {"np": np, "BTH": 2, "TH_LO": -2., "TH_SCALE": 4. / 3., "qubo_from_linear_quadratic": util["qubo_from_linear_quadratic"]})
    Z = np.array([[.1, .4], [.5, -.3], [-.2, .6]])
    targets = np.array([1., -1., 1.])
    hq, A, g = bnn["head_qubo"](Z, targets)
    head_errors = []
    for bits in bitstrings(4):
        weights = 2. * bits[:2] - 1.
        threshold = -2. + 4. / 3. * (bits[2] + 2. * bits[3])
        actual = np.sum((Z @ weights - threshold - targets) ** 2)
        head_errors.append(abs(float(actual - bits @ hq @ bits - np.sum((targets - g) ** 2))))

    # Keep inputs and the three pair classifiers fixed. The original code's
    # voting gate depends on y_all; the logical counterexample needs no training.
    pairs_and_fixed_winners = [(0, 1, 1), (0, 2, 0), (1, 2, 2)]

    def gated_predictions(evaluation_labels):
        votes = np.zeros((len(evaluation_labels), 3), dtype=int)
        for c0, c1, winner in pairs_and_fixed_winners:
            idx = np.flatnonzero((evaluation_labels == c0) | (evaluation_labels == c1))
            votes[idx, winner] += 1
        return votes.argmax(axis=1).tolist()

    y_first = np.array([0, 1, 2])
    y_second = np.array([0, 0, 0])
    gated_first = gated_predictions(y_first)
    gated_second = gated_predictions(y_second)
    correct_votes = np.zeros((3, 3), dtype=int)
    for _, _, winner in pairs_and_fixed_winners:
        correct_votes[:, winner] += 1
    assert gated_first != gated_second
    one_lsb = Fraction(1, 15)
    raw2 = json.loads((RAW / "results/task2_probe.json").read_text())
    raw3 = json.loads((RAW / "results/task3_probe.json").read_text())
    suspect = [r for r in raw2["penalty_sweep"] if r["resid_in_lsb"] and abs(r["resid"]) > 1e-6]
    # Boolean multilinear coefficients, independently expanded by finite
    # differences; bit order is beta_low,beta_high,weight_1,weight_2.
    beta_loss = []
    for mask in range(16):
        bits = [(mask >> j) & 1 for j in range(4)]
        beta = 1 + bits[0] + 2 * bits[1]
        score = beta * ((2 * bits[2] - 1) + 2 * (2 * bits[3] - 1))
        beta_loss.append((score - 1) ** 2)
    coefficients = beta_loss[:]
    for j in range(4):
        for mask in range(16):
            if mask & (1 << j):
                coefficients[mask] -= coefficients[mask ^ (1 << j)]
    highest_degree = max(bin(mask).count("1") for mask, c in enumerate(coefficients) if c)
    assert highest_degree == 4 and coefficients[15] == 64
    and_table = []
    for x, y, z in itertools.product([0,1], repeat=3):
        old = x*y-x*z-y*z+z
        corrected = x*y-2*x*z-2*y*z+3*z
        valid = z == x*y
        assert (corrected == 0) if valid else (corrected > 0)
        and_table.append({"x":x,"y":y,"z":z,"valid":valid,"candidate_penalty":old,"corrected_penalty":corrected})
    original_demand = np.array([9000,9400,9594,9859,9958,10043,10309,10512,10588]) / 1000.
    common_window = {}
    for order in (1, 2, 3):
        design = np.array([[1.] + [original_demand[t-i] for i in range(1,order+1)] for t in range(3,9)])
        response = original_demand[3:]
        theta = np.linalg.lstsq(design, response, rcond=None)[0]
        sse = float(np.sum((design @ theta - response) ** 2))
        common_window[order] = {"n":6,"k":order+1,"SSE":sse,"conditional_BIC":float(6*np.log(sse/6)+(order+1)*np.log(6))}
    checks = {
        "scope": "Small exhaustive algebra checks against original objectives plus deterministic counterexamples; no full-data SA rerun or SDK execution",
        "algebra": {
            "AR_assignments": 64, "AR_max_error": max(ar_errors),
            "SVM_assignments": 64, "SVM_max_error": max(svm_errors),
            "binary_head_assignments": 16, "binary_head_max_error": max(head_errors),
            "upper_vs_symmetric_max_error": max(upper_errors),
        },
        "prediction_label_leak": {
            "source": "probe_task2_svm.py: Kall uses Xp selected by y_all; only votes[idx] updated",
            "frozen_pair_winners": pairs_and_fixed_winners,
            "labels_first": y_first.tolist(), "predictions_first": gated_first,
            "labels_changed_only": y_second.tolist(), "predictions_after_label_change": gated_second,
            "correct_all_pairs_predictions": correct_votes.argmax(axis=1).tolist(),
            "consequence": "Withdraw original full_corpus_vote_acc; even an in-sample label does not excuse label-dependent prediction. Original aggregate outputs cannot recover corrected accuracy without models/predictions.",
        },
        "equality_acceptance": {
            "one_LSB_exact": str(one_lsb), "one_LSB_is_zero": one_lsb == 0,
            "original_rows_marked_acceptable_despite_nonzero_residual": suspect,
            "consequence": "Discretization resolution is not equality-feasibility tolerance; integer signed bit-sums can be checked exactly on this shared grid.",
        },
        "failed_head_route": {
            "source_status": "Original producer numerical outputs read, not independently rerun",
            "binary_accuracy": raw3["acc_qubo_binary_head"],
            "random_median": raw3["acc_random_binary_median"],
            "random_max": raw3["acc_random_binary_max"],
            "continuous_head_accuracy": raw3["acc_continuous_ls_head"],
            "consequence": "Does not approach continuous head. Do not describe route as validated or improved; future fallback still needs a check.",
        },
        "learned_scale_quadratization": {
            "tiny_loss": "(beta*(w1+2*w2)-1)^2; beta=1+u+2v, wi=2bi-1",
            "Boolean_assignments":16,"highest_degree":highest_degree,"quartic_coefficient":coefficients[15],
            "consequence":"Adding jointly learned beta does not preserve QUBO. Count beta and any reduction variables; fixed scaling or a derived quadratic alternative is different.",
        },
        "AR_common_response_window": {
            "source_issue":"Original BIC rows use8/7/6responses for p1/2/3; raw ranks not same-response likelihood comparisons",
            "recomputed_same6responses":common_window,
            "boundary":"Conditional-model comparison only, tiny9pointseries; no predictive accuracy or unique correct order claim",
        },
        "candidate_regression_findings": {
            "AND_truth_table":and_table,
            "invalid_zero_penalty_rows":[r for r in and_table if not r["valid"] and r["candidate_penalty"]==0],
            "OVO":"All3pair classifiers must evaluate every3-class test sample; candidate's2voteprotocol still requires knowing its true class",
            "split_counts":"150Iris samples,30test/class leaves20train/class; a pair has40trainrows, not60or70. K4 gives160bits.",
            "causal_scope":"Candidate's0.9611 result changed classes10->2, features72->16, pooling/filtercount, thresholdrange, sampling and solver as well as normalization. It does not isolate normalization as cause.",
            "invariance_scope":"Candidate code repeats acc(Xte,ste) with identical inputs; its true boolean does not document a label permutation/hiding experiment",
        },
        "SDK": "Not executed; generic local NumPy SA is not Kaiwu SA, and neither alone establishes hardware advantage",
        "passed_algebra_only": all(max(x) < 1e-9 for x in (ar_errors, upper_errors, svm_errors, head_errors)),
    }
    assert checks["passed_algebra_only"]
    (ROOT / "root-checks.json").write_text(json.dumps(checks, indent=2, ensure_ascii=False) + "\n")
    print(json.dumps(checks, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()
