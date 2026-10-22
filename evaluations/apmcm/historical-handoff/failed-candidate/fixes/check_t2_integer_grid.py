"""
Regression fix check for Task 2 (candidate-skill task-families,
"specified representation / constrained solver" section):
a quantization step is NOT an equality-feasibility tolerance.
With alpha_i = Delta * d_i, d_i integer, the dual equality
  sum_i alpha_i y_i = 0
must be checked on the shared rational grid as
  sum_i d_i y_i = 0 (exact integer check),
not as |residual| <= Delta.

Two fixed, frozen instances (no parameter scans):
(A) Representation gate: n=8 Iris samples (4 setosa + 4 versicolor),
    K=3 -> 24 bits, EXACT enumeration; decode integers and assert the
    integer-weighted equality; also confirm encoded energy equals the
    decoded dual objective.
(B) Main route config: n=40 (20/class), K=4, C=1, P=10, linear kernel,
    fixed seed=1; the numpy SA is only a candidate generator;
    feasibility is again the exact integer check.
"""
import json
import sys
from pathlib import Path
import numpy as np
from sklearn.datasets import load_iris
from sklearn.preprocessing import StandardScaler

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "frozen-producer-output" / "probes"))
from qubo_sa import sa_minimize, exact_minimize, qubo_from_linear_quadratic  # noqa

data = load_iris()
X_all, y_all = data.data, data.target


def kernel(a, b):
    return a @ b.T


def svm_qubo(K, y, C, nbits, P):
    n = len(y)
    delta = C / (2 ** nbits - 1)
    D = np.zeros((n, n * nbits))
    for i in range(n):
        for k in range(nbits):
            D[i, i * nbits + k] = delta * 2 ** k
    M = (y[:, None] * y[None, :]) * K
    quad = 0.5 * (D.T @ M @ D) + P * (D.T @ np.outer(y, y) @ D)
    linear = -D.sum(axis=0)
    Q = qubo_from_linear_quadratic(linear, quad)
    return Q, D, delta


def decode_integers(bits, n, K):
    return (bits.reshape(n, K) @ (2.0 ** np.arange(K))).astype(int)


def instance(Xtr, ytr, kind_note, K, P, exact, sweeps, seed):
    Kmat = kernel(Xtr, Xtr)
    C = 1.0
    n = len(ytr)
    Q, D, delta = svm_qubo(Kmat, ytr, C, K, P)
    if exact:
        x, e = exact_minimize(Q)
    else:
        x, e, _, _ = sa_minimize(Q, sweeps=sweeps, runs=8, seed=seed)
    d = decode_integers(x, n, K)
    alpha = delta * d.astype(float)
    int_resid = int(np.sum(d * ytr.astype(int)))      # exact grid check
    float_resid = float(np.sum(alpha * ytr))
    # original dual objective (penalty-free), decoded directly
    obj = 0.5 * alpha @ ((ytr[:, None] * ytr[None, :]) * Kmat) @ alpha - alpha.sum()
    rec = {
        "instance": kind_note, "n": n, "K": K, "bits": n * K,
        "P": P, "delta": round(delta, 8),
        "integer_residual_sum(d_i*y_i)": int_resid,
        "integer_grid_feasible": bool(int_resid == 0),
        "float_residual": round(float_resid, 12),
        "old_lsb_check_abs_resid_le_delta": bool(abs(float_resid) <= delta),
        "decoded_dual_objective": round(float(obj), 6),
        "qubo_energy": round(float(x @ Q @ x), 6),
        "n_alpha_positive": int((d > 0).sum()),
        "solver": "exact enumeration" if exact else "numpy SA (not Kaiwu)",
    }
    return rec


out = {"check": "equality on rational integer grid, not LSB tolerance",
       "instances": []}

# (A) 24-bit exact representation gate: 4 setosa + 4 versicolor, by class
idx0 = np.where(y_all == 0)[0][:4]
idx1 = np.where(y_all == 1)[0][:4]
idx = np.r_[idx0, idx1]
Xp = X_all[idx]
yp = np.r_[-np.ones(4), np.ones(4)]
sc = StandardScaler().fit(Xp)
Xp = sc.transform(Xp)
out["instances"].append(instance(Xp, yp, "A: 8 samples, K=3, exact", 3, 10.0,
                                 True, None, 0))

# (B) frozen main config: same split as the frozen probe (seed=1, 40 train)
from sklearn.model_selection import train_test_split  # noqa
idxall = np.where((y_all == 0) | (y_all == 1))[0]
XpB = X_all[idxall]
ypB = np.where(y_all[idxall] == 0, -1.0, 1.0)
Xtr, _, ytr, _ = train_test_split(XpB, ypB, train_size=40,
                                  stratify=ypB, random_state=1)
sc2 = StandardScaler().fit(Xtr)
Xtr = sc2.transform(Xtr)
out["instances"].append(instance(Xtr, ytr, "B: 40 samples, K=4, P=10",
                                 4, 10.0, False, 1500, 1))

outp = Path(__file__).parent / "t2_integer_grid.json"
outp.write_text(json.dumps(out, indent=2, ensure_ascii=False))
for r in out["instances"]:
    print(json.dumps(r, ensure_ascii=False))
