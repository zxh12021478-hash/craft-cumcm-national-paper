"""
Shared QUBO utilities for the 2024 APMCM Problem D route probes.

Convention (verified against kaiwu-community 1.0.7):
  QuboModel.get_matrix() returns an UPPER-TRIANGULAR matrix U with
  energy = sum_i U_ii x_i + sum_{i<j} U_ij x_i x_j, x in {0,1}.
The local probe solver uses a SYMMETRIC matrix Q with energy x^T Q x,
i.e. Q_ii = linear_i, Q_ij = U_ij/2 for i!=j. The Kaiwu SA solver
(kw.classical.SimulatedAnnealingOptimizer.solve_qubo) consumes the
QuboModel directly, so Modex never needs these two representations
to be aligned by hand; to_kaiwu_matrix() emits the SDK upper-triangular
form for documentation/CSV checks.

The SA below is an independent numpy bit-flip annealer used ONLY to
decide whether each modeled route is viable. It is not the Kaiwu SDK
solver and must not be reported as such in the paper.
"""
import numpy as np


def qubo_from_linear_quadratic(linear, quad):
    """Build symmetric Q for energy x^T Q x from:
       linear: l^T x ; quad: symmetric quadratic matrix A with x^T A x.
    Returns symmetric Q (diag carries linear terms)."""
    A = np.asarray(quad, dtype=float)
    l = np.asarray(linear, dtype=float)
    Q = 0.5 * (A + A.T)
    Q = Q.copy()
    np.fill_diagonal(Q, 0.0)
    Q += np.diag(np.diag(0.5 * (A + A.T)) + l)
    return Q


def greedy_polish(Q, x):
    """Best-improvement single-flip descent to a local minimum."""
    n = Q.shape[0]
    x = x.copy()
    g = Q.diagonal().copy() + 2.0 * (Q @ x - Q.diagonal() * x)
    while True:
        dE = (1 - 2 * x) * g
        i = int(np.argmin(dE))
        if dE[i] >= -1e-12:
            return x
        g += 2.0 * (1 - 2 * x[i]) * Q[:, i]
        g[i] -= 2.0 * (1 - 2 * x[i]) * Q[i, i]
        x[i] = 1 - x[i]


def sa_minimize(Q, sweeps=1500, T0=None, T1=None, runs=6, seed=0,
                init=None, verbose=False, polish=True):
    """Bit-flip simulated annealing on symmetric Q (energy x^T Q x).
    T0=None: auto-scale from the positive single-flip delta-E distribution.
    Returns (best_x, best_energy, per_run_energies, accept_rate)."""
    rng = np.random.default_rng(seed)
    n = Q.shape[0]
    if T0 is None:
        probe = rng.integers(0, 2, n)
        gp = Q.diagonal().copy() + 2.0 * (Q @ probe - Q.diagonal() * probe)
        de = np.abs((1 - 2 * probe) * gp)
        T0 = max(float(np.quantile(de, 0.9)), 1e-9)
    if T1 is None:
        T1 = T0 * 1e-6
    best_x, best_e = None, np.inf
    run_es, acc_total, acc_steps = [], 0, 0
    for r in range(runs):
        x = rng.integers(0, 2, n) if init is None else init.copy()
        g = Q.diagonal().copy() + 2.0 * (Q @ x - Q.diagonal() * x)
        for s in range(sweeps):
            T = T0 * (T1 / T0) ** (s / max(1, sweeps - 1))
            for _ in range(n):
                i = rng.integers(n)
                dE = (1 - 2 * x[i]) * g[i]
                if dE <= 0 or rng.random() < np.exp(-dE / T):
                    g += 2.0 * (1 - 2 * x[i]) * Q[:, i]
                    g[i] -= 2.0 * (1 - 2 * x[i]) * Q[i, i]
                    x[i] = 1 - x[i]
                    acc_total += 1
                acc_steps += 1
        if polish:
            x = greedy_polish(Q, x)
        e = float(x @ Q @ x)
        run_es.append(e)
        if e < best_e:
            best_e, best_x = e, x.copy()
        if verbose:
            print(f"  run {r}: energy {e:.6f}")
    return best_x, best_e, run_es, acc_total / max(1, acc_steps)


def exact_minimize(Q, batch=1_000_000):
    """Enumerate all bit strings (only for n<=24). Returns (x, energy)."""
    n = Q.shape[0]
    assert n <= 24, "exact enumeration only for n<=24"
    best_x, best_e = None, np.inf
    for start in range(0, 2 ** n, batch):
        ids = np.arange(start, min(start + batch, 2 ** n), dtype=np.int64)
        B = ((ids[:, None] >> np.arange(n)) & 1).astype(float)
        E = np.einsum("bi,ij,bj->b", B, Q, B)
        i = int(np.argmin(E))
        if E[i] < best_e:
            best_e, best_x = float(E[i]), B[i]
    return best_x, best_e


def to_kaiwu_upper(Q):
    """Symmetric x^T Q x -> SDK upper-triangular U (diag linear;
    U_ij = 2 Q_ij for i<j)."""
    n = Q.shape[0]
    U = np.zeros_like(Q)
    for i in range(n):
        U[i, i] = Q[i, i]
        for j in range(i + 1, n):
            U[i, j] = 2.0 * Q[i, j]
    return U


def bits_of(values, nbits, lo, hi):
    """Encode each value in `values` (unsigned fixed-point over [lo,hi]).
    Returns bit indices (relative), decode(matrix_of_bits).
    Values map: v = lo + (hi-lo) * d / (2^nbits - 1), d=sum 2^k b_k."""
    idx = np.arange(nbits)
    scale = (hi - lo) / (2 ** nbits - 1)

    def decode(bit_rows):
        # bit_rows: (len(values), nbits)
        d = bit_rows @ (2.0 ** idx)
        return lo + scale * d
    return idx, scale, decode


def energy_ols_bits(X, y, ranges, nbits):
    """Least-squares min ||X theta - y||^2 with each theta_m encoded
    fixed-point over ranges[m]=(lo,hi) with nbits bits.
    Returns symmetric Q, block offsets, and a decoder theta(b)."""
    npar = X.shape[1]
    blocks = []
    L = np.zeros(npar)
    scales = np.zeros(npar)
    for m, (lo, hi) in enumerate(ranges):
        blocks.append((m, nbits))
        L[m] = lo
        scales[m] = (hi - lo) / (2 ** nbits - 1)
    # theta_m = L_m + scale_m * sum_k 2^k b_mk
    A = np.zeros((npar, npar * nbits))  # theta = L + A b
    for m in range(npar):
        for k in range(nbits):
            A[m, m * nbits + k] = scales[m] * 2 ** k
    XA = X @ A
    quad = XA.T @ XA
    linear = 2.0 * (X @ L - y) @ XA
    Q = qubo_from_linear_quadratic(linear, quad)
    const = float((X @ L - y) @ (X @ L - y))

    def decode(b):
        b = np.asarray(b).reshape(npar, nbits)
        d = b @ (2.0 ** np.arange(nbits))
        return L + scales * d
    return Q, decode, const
