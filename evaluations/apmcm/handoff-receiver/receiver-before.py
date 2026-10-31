"""Evaluation-only extract from an actual development receiver. Not a trained model.
Source SHA256: 4ea3728e411db9a0b1cdc4b0bd22c23b05d631b86d3a6b460ffece2ef1af6ac4
"""

def least_squares_qubo(H, r, L, D):
    n = len(H)
    m = len(H[0])
    k = len(D[0])
    if not (len(r) == n and len(L) == m and (len(D) == m)):
        raise ValueError('shape mismatch: H n x m, r n, L m, D m x k')
    if any((len(row) != m for row in H)) or any((len(row) != k for row in D)):
        raise ValueError('ragged input')
    B = [[sum((H[i][p] * D[p][j] for p in range(m))) for j in range(k)] for i in range(n)]
    u = [sum((H[i][p] * L[p] for p in range(m))) for i in range(n)]
    e = [u[i] - r[i] for i in range(n)]
    Q = [[sum((B[i][a] * B[i][b] for i in range(n))) for b in range(k)] for a in range(k)]
    for j in range(k):
        Q[j][j] += 2.0 * sum((B[i][j] * e[i] for i in range(n)))
    offset = sum((v * v for v in e))
    return {'Q': Q, 'offset': offset, 'n_bits': k}

def _smaller(c0, c1, classes):
    return c0 if classes.index(c0) <= classes.index(c1) else c1

def predict_ovo(X, models, classes):
    predictions = []
    for x in X:
        votes = {c: 0 for c in classes}
        for model in models:
            c0, c1 = model['classes']
            score = sum((wj * xj for wj, xj in zip(model['w'], x))) + model['bias']
            if score > 0:
                votes[c1] += 1
            elif score < 0:
                votes[c0] += 1
            else:
                votes[_smaller(c0, c1, classes)] += 1
        best_votes = max(votes.values())
        winners = [c for c in classes if votes[c] == best_votes]
        predictions.append(winners[0])
    return predictions
