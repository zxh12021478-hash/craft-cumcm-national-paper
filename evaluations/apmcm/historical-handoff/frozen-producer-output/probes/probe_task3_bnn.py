"""
Task 3 route probe: frozen numpy CNN feature extractor + QUBO-trained
binary-weight classification head on the built-in 8x8 digits images
(offline stand-in for MNIST 8x8 downscaled, which Modex should use when
network access is available).

Route: conv (fixed random 3x3 filters) -> ReLU -> average pool ->
standardize, then per-class one-vs-rest binary neuron
score_c = sum_i w_i z_i - theta, w_i in {-1,+1}, trained by
minimizing squared loss over samples. With w=2b-1 the loss is exactly
quadratic in binary variables -> one QUBO per class.

Questions decided by this probe:
  1) Does the QUBO binary head give non-trivial held-out accuracy
     (beats random binary weights, approaches a continuous head)?
  2) Bit budget per class vs the 600-bit limit.
"""
import json
import numpy as np
from pathlib import Path
from sklearn.datasets import load_digits
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler
from sklearn.linear_model import LogisticRegression
from qubo_sa import sa_minimize, qubo_from_linear_quadratic

digits = load_digits()
imgs = digits.images.astype(float) / 16.0
labels = digits.target
rng = np.random.default_rng(0)


def cnn_features(imgs, n_filters=8, seed=0):
    """Fixed random conv 3x3 (valid) -> ReLU -> 2x2 average pool."""
    r = np.random.default_rng(seed)
    F = rng.normal(size=(n_filters, 3, 3))
    fstd = F.reshape(n_filters, -1).std(axis=1).reshape(n_filters, 1, 1)
    F = F / fstd
    n = imgs.shape[0]
    feats = []
    for img in imgs:
        blocks = []
        for k in range(n_filters):
            c = np.array([[np.sum(img[i:i + 3, j:j + 3] * F[k])
                           for j in range(6)] for i in range(6)])
            c = np.maximum(c, 0)
            p = c.reshape(3, 2, 3, 2).mean(axis=(1, 3))  # 3x3 pooled
            blocks.append(p.ravel())
        feats.append(np.concatenate(blocks))
    return np.array(feats), n_filters * 9


Z, d = cnn_features(imgs)
Xtr, Xte, ytr, yte = train_test_split(Z, labels, test_size=0.5,
                                      stratify=labels, random_state=0)
sc = StandardScaler().fit(Xtr)
Xtr, Xte = sc.transform(Xtr), sc.transform(Xte)

BTH = 8
TH_LO, TH_HI = -16.0, 16.0
TH_SCALE = (TH_HI - TH_LO) / (2 ** BTH - 1)


def head_qubo(Z, s):
    n, dim = Z.shape
    u = Z.sum(axis=1)
    A = np.zeros((n, dim + BTH))
    A[:, :dim] = 2.0 * Z
    for k in range(BTH):
        A[:, dim + k] = -TH_SCALE * 2 ** k
    g = -u - TH_LO
    quad = A.T @ A
    linear = -2.0 * (s - g) @ A
    Q = qubo_from_linear_quadratic(linear, quad)
    return Q, A, g


def train_head(Z, s, seed=0):
    Q, A, g = head_qubo(Z, s)
    x, e, _, _ = sa_minimize(Q, sweeps=1000, runs=5, seed=seed)
    w = 2.0 * x[:Z.shape[1]] - 1.0
    theta = TH_LO + TH_SCALE * np.sum(2.0 ** np.arange(BTH) * x[Z.shape[1]:])
    return w, theta, Q.shape[0]


def scores_for(W, TH, Z):
    return Z @ W.T - TH[None, :]


classes = np.unique(ytr)
W, TH = [], []
bits_each = None
for c in classes:
    s = np.where(ytr == c, 1.0, -1.0)
    # balance positives/negatives to stop the squared loss collapsing
    pos = np.where(s == 1)[0]
    neg = np.where(s == -1)[0]
    neg_s = rng.choice(neg, size=len(pos), replace=False)
    sel = np.sort(np.r_[pos, neg_s])
    w, th, nb = train_head(Xtr[sel], s[sel], seed=int(c))
    W.append(w)
    TH.append(th)
    bits_each = nb
W, TH = np.array(W), np.array(TH)
acc_qubo = float(np.mean(np.argmax(scores_for(W, TH, Xte), 1) == yte))

# baselines
clf = LogisticRegression(max_iter=2000).fit(Xtr, ytr)
acc_log = float(clf.score(Xte, yte))
rnd_acc = []
for seed in range(20):
    Wr = np.random.default_rng(seed).choice([-1.0, 1.0], size=(10, d))
    rnd_acc.append(float(np.mean(np.argmax(Xte @ Wr.T, 1) == yte)))
# continuous least-squares one-hot head
T = -np.ones((len(ytr), 10)); T[np.arange(len(ytr)), ytr] = 1.0
Wc = np.linalg.lstsq(Xtr, T, rcond=None)[0]
acc_ls = float(np.mean(np.argmax(Xte @ Wc, 1) == yte))

results = {
    "features": "fixed random conv3x3-ReLU-avgpool on 8x8 digits",
    "n_features": d, "threshold_bits": BTH,
    "bits_per_class_qubo": bits_each,
    "n_classes": 10, "n_train": len(ytr), "n_test": len(yte),
    "acc_qubo_binary_head": round(acc_qubo, 4),
    "acc_logistic_baseline": round(acc_log, 4),
    "acc_continuous_ls_head": round(acc_ls, 4),
    "acc_random_binary_median": round(float(np.median(rnd_acc)), 4),
    "acc_random_binary_max": round(float(np.max(rnd_acc)), 4),
}
out = Path(__file__).parent / "results" / "task3_probe.json"
out.parent.mkdir(exist_ok=True)
out.write_text(json.dumps(results, indent=2, ensure_ascii=False))
print("=== Task 3 CNN+binary-head QUBO probe ===")
print(json.dumps(results, indent=2))
