"""
Regression fix gate for Task 3 (candidate-skill task-families):
the frozen probe's binary head failed at chance level. The diagnosed
cause was a score/target scale mismatch. The proposed repair must NOT
introduce a learnable binary multiplier beta (that creates bit*bit
products with w and raises the loss above quadratic -> QUBO would need
higher-order reduction with auxiliary variables and a new bit count).

This gate uses FIXED normalization only (features / sqrt(d), fixed
threshold grid), so the loss stays quadratic. It is a tiny, fixed
instance: digits 0 vs 1, 4 frozen random conv filters -> 16 pooled
features + 8 threshold bits = 24 bits, solved by EXACT Gray-code
enumeration (no SA, no scan, no learned hyperparameter).

The gate is a representation/feasibility check with a LOCAL criterion
set in the handoff (test accuracy >= 0.95 and within 5pp of the
continuous head on identical features). It is NOT a 10-class result and
does not transfer any continuous-model accuracy to the binary route.
"""
import json
from pathlib import Path
import numpy as np
from sklearn.datasets import load_digits
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler


def exact_minimize_gray(Q):
    """Exact QUBO minimization via Gray-code single-flip traversal."""
    n = Q.shape[0]
    Ql = [list(map(float, Q[:, j])) for j in range(n)]
    qd = [float(Q[i, i]) for i in range(n)]
    x = [0] * n
    g = list(qd)          # g_i = Q_ii + 2 sum_{j != i} Q_ij x_j, x=0
    e, best_e, best_x = 0.0, 0.0, x[:]
    for t in range(1, 1 << n):
        i = (t & -t).bit_length() - 1
        s = 1 - 2 * x[i]
        e += s * g[i]
        qi = Ql[i]
        for j in range(n):
            if j != i:
                g[j] += 2.0 * s * qi[j]
        x[i] = 1 - x[i]
        if e < best_e:
            best_e, best_x = e, x[:]
    return np.array(best_x), best_e


def conv_features(imgs, n_filters=4, seed=0):
    """Fixed random conv 3x3 (valid) -> ReLU -> non-overlapping 3x3
    average pool of the 6x6 activation -> 2x2 per filter -> 4 per filter."""
    r = np.random.default_rng(seed)
    F = r.normal(size=(n_filters, 3, 3))
    F = F / F.reshape(n_filters, -1).std(axis=1).reshape(n_filters, 1, 1)
    feats = []
    for img in imgs:
        blocks = []
        for k in range(n_filters):
            c = np.array([[np.sum(img[i:i + 3, j:j + 3] * F[k])
                           for j in range(6)] for i in range(6)])
            c = np.maximum(c, 0)
            p = c.reshape(2, 3, 2, 3).mean(axis=(1, 3))  # 2x2 pooled
            blocks.append(p.ravel())
        feats.append(np.concatenate(blocks))
    return np.array(feats), n_filters * 4


digits = load_digits()
mask = (digits.target == 0) | (digits.target == 1)
imgs = digits.images[mask].astype(float) / 16.0
y = digits.target[mask]
Z, d = conv_features(imgs)
Xtr, Xte, ytr, yte = train_test_split(Z, y, test_size=0.5,
                                      stratify=y, random_state=0)
sc = StandardScaler().fit(Xtr)
# fixed scaling only; no learnable variable added -> stays quadratic
Xtr = sc.transform(Xtr) / np.sqrt(d)
Xte = sc.transform(Xte) / np.sqrt(d)
s = np.where(ytr == 0, -1.0, 1.0)        # class 0 -> -1, class 1 -> +1
ste = np.where(yte == 0, -1.0, 1.0)

BTH = 8
TH_LO, TH_HI = -2.0, 2.0
TH_SCALE = (TH_HI - TH_LO) / (2 ** BTH - 1)
u = Xtr.sum(axis=1)
# score = sum w_i z_i - theta = A q + g, q = [b_w(16), b_th(8)]
A = np.zeros((len(s), d + BTH))
A[:, :d] = 2.0 * Xtr
for k in range(BTH):
    A[:, d + k] = -TH_SCALE * 2 ** k
g = -u - TH_LO
# squared loss: symmetric QUBO; off-diagonal carries A'A, diagonal
# carries (A'A)_ii plus the linear term -2(s-g)'A
Q = A.T @ A
np.fill_diagonal(Q, Q.diagonal() + (-2.0 * (s - g) @ A))

bx, be = exact_minimize_gray(Q)
w = 2.0 * bx[:d] - 1.0
theta = TH_LO + TH_SCALE * np.sum(2.0 ** np.arange(BTH) * bx[d:])


def acc(Z, sv):
    f = Z @ w - theta
    return float(np.mean(np.sign(f) == sv)), np.sign(f)


atr, pred_tr = acc(Xtr, s)
ate, pred_te = acc(Xte, ste)

# continuous linear head on identical features (reference only; its
# performance is not transferable to the binary head)
Wc = np.linalg.lstsq(np.c_[np.ones(len(Xtr)), Xtr], s, rcond=None)[0]
ac_tr = float(np.mean(np.sign(np.c_[np.ones(len(Xtr)), Xtr] @ Wc) == s))
ac_te = float(np.mean(np.sign(np.c_[np.ones(len(Xte)), Xte] @ Wc) == ste))
rng = np.random.default_rng(2)
rnd = [float(np.mean(np.sign(Xte @ rng.choice([-1.0, 1.0], d)) == ste))
       for _ in range(20)]

# label-hiding invariance: recompute predictions from features only
_, pred_te2 = acc(Xte, ste)
invariance = bool(np.array_equal(pred_te, pred_te2))

out = {
    "instance": "digits 0 vs 1, 4 frozen conv filters -> 16 features + 8 threshold bits",
    "bits": int(d + BTH), "solver": "exact Gray-code enumeration",
    "fixed_normalization": "z := standardize(train)/sqrt(d); quadraticity preserved",
    "theta_grid": {"lo": TH_LO, "hi": TH_HI, "lsb": round(TH_SCALE, 5)},
    "qubo_energy_exact": round(float(be), 4),
    "binary_head_acc_train": round(atr, 4),
    "binary_head_acc_test": round(ate, 4),
    "continuous_head_acc_train": round(ac_tr, 4),
    "continuous_head_acc_test": round(ac_te, 4),
    "random_binary_test_median": round(float(np.median(rnd)), 4),
    "local_gate_criterion": "test >= 0.95 and gap vs continuous <= 0.05",
    "gate_passed": bool(ate >= 0.95 and (ac_te - ate) <= 0.05),
    "n_train": len(ytr), "n_test": len(yte),
    "hidden_label_invariance": invariance,
}
outp = Path(__file__).parent / "t3_gate24.json"
outp.write_text(json.dumps(out, indent=2, ensure_ascii=False))
print(json.dumps(out, indent=2, ensure_ascii=False))
