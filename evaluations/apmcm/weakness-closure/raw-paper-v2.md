# Development Analyses and Strategies for the Pet Industry and Related Industries

*Rehearsal draft based on the 2024 APMCM Problem C. This is a development exercise with answer feedback, not a blind test, a calibrated world-demand forecast, a statement of actual tariff policy, or a submission-ready paper. All scenario parameters are labeled as analyst assumptions.*

## Summary

From 2019 to 2023 the number of pet cats in China rose from 4,412 to 6,980 (10,000 animals), i.e. from 44.12 million to 69.80 million, a 58.2% increase; the number of pet dogs moved from 5,503 to 5,175 (10,000 animals), a 6.0% net decline after year-to-year fluctuations. A level-linear model selected by two strictly forward one-step validation origins forecasts 7,762, 8,443 and 9,124 cats for 2024–2026; a log-linear model, chosen on the same rule, forecasts 5,066, 4,994 and 4,923 dogs, a mild downward trend. Two one-step origins are diagnostic evidence, not a three-year accuracy claim, and the five annual points cannot identify causal drivers.

For the three observed overseas markets, the six cat/dog series together drift from an index of 100 in 2023 to 96.8 in 2026. Under fixed nonnegative per-animal food coefficients, the 2026/2023 three-market food-demand ratio is provably bracketed between 0.897318 and 1.067906, so the sign of growth is not determined. A sourced 2023 worldwide production anchor of 34.96 million tonnes is production, not measured consumption; under assumed 2% loss and unchanged inventories, consumption is 34.2608 million tonnes, and an analyst 5% growth scenario reaches 39.6611586 million tonnes of consumption by 2026.

The separate univariate production and export projections are diagnostic baselines, not simultaneous predictions under one economic model: production value is forecast at 3,050.19, 3,598.72 and 4,147.25 (100m CNY), and exports at a flat 39.6 (100m USD) per year. The linked quantity–value bridge, which uses different economic assumptions, places 2026 exports between 35.08 and 51.63 (100m USD) and factory production between 2,698.09 and 3,612.57 (100m CNY). Tariff scenarios use a coupled buyer/producer price chain with an analytically derived optimal producer price; under the robust worst-case domain (elasticity up to 6, cost fraction 0.8) the recommended price is 0.96 of baseline with 15% absorption. Of the 12 analyst diversification scenarios, 8 keep the no-move decision and 4 support a positive move; acting on any of them still requires measured cost, margin and capacity quotes.

## 1. Data, scope and modeling protocol

Three official attachment tables supply: (i) 2019–2023 China pet cats and dogs; (ii) 2019–2023 cats and dogs in America, France and Germany; (iii) 2019–2023 China pet-food production value (CNY) and export value (USD except the 2019 entry in CNY). Pet counts are in 10,000 animals; monetary values are in 100 millions of the stated currency.

Three candidate extrapolators are compared:

```
last value:   f(x) = y_last
level linear: f(x) = a + b x, a,b from ordinary least squares
log linear:   f(x) = exp(a + b x), a,b from OLS on log y
```

The log-linear candidate is fitted on log-transformed y, but every candidate is scored on the original units: validation errors and MAEs are always computed between original-scale forecasts and original-scale observations. Validation is strictly forward: train on 2019–2021 and predict 2022, then train on 2019–2022 and predict 2023. The two absolute errors are averaged into an origin MAE, the lowest-MAE candidate is selected, and ties go to the simpler model. No 2024–2026 realized value enters any choice. After selection, each candidate is refit on all five points and extrapolated to 2024–2026.

[[FIG:china]]

## 2. Question 1 — China's pet industry by pet type

### 2.1 Observed development

| Year | Cats | Dogs |
|---|---|---|
| 2019 | 4,412 | 5,503 |
| 2020 | 4,862 | 5,222 |
| 2021 | 5,806 | 5,429 |
| 2022 | 6,536 | 5,119 |
| 2023 | 6,980 | 5,175 |

Cat ownership grew monotonically by 58.2% over five years; dog ownership fluctuated between 5,119 and 5,503 and ended 6.0% below its 2019 level. Cats were 44.5% of the 2019 total and 57.4% in 2023.

### 2.2 Validation and forecasts

```
origin MAE, cats: last value 587.0 | level linear 184.2 | log linear 276.8  -> level linear
origin MAE, dogs: last value 183.0 | level linear 142.3 | log linear 141.2  -> log linear
```

The level-linear cat forecast is 7,762 / 8,443 / 9,124 and the log-linear dog forecast is 5,066 / 4,994 / 4,923 (10,000 animals). The dog margin between the two linear candidates is one unit on the origin MAE, so the choice is data-driven but not decisive.

### 2.3 Factors and their evidentiary status

Five annual observations cannot identify a multivariate causal mechanism. We record hypotheses consistent with the observed divergence — rising urban disposable income and supply expansion favoring cats, smaller dwellings and licensing/time costs constraining dogs — as qualitative context, not fitted effects. No five-point multivariate regression is attempted, and no factor is presented as measured.

## 3. Question 2 — Overseas markets and global pet-food demand

### 3.1 Observed development by type

The overseas series show distinct 2019–2023 paths: America cats fell 21.7% with sharp year-to-year swings, America dogs fell 10.7%; France cats rose 27.7% and France dogs 33.8%; Germany cats rose 6.8% and Germany dogs 4.0%. These are descriptive changes, not causal effects.

### 3.2 Per-market forecasts for all three years

| Series | Model | 2024 | 2025 | 2026 |
|---|---|---|---|---|
| America cats | log linear | 7,118.23 | 6,865.74 | 6,622.20 |
| America dogs | last value | 8,010 | 8,010 | 8,010 |
| France cats | last value | 1,660 | 1,660 | 1,660 |
| France dogs | log linear | 944.72 | 999.39 | 1,057.23 |
| Germany cats | last value | 1,570 | 1,570 | 1,570 |
| Germany dogs | level linear | 1,065 | 1,072 | 1,079 |

The three-market aggregate is 20,660 in 2023 and 19,998 in 2026, with an index path of 100, 98.6, 97.7, 96.8. These are three named countries; their sum is not world demand.

[[FIG:global]]

### 3.3 Proof of the fixed-intensity food-demand bounds

Let N_i be the animal count of series i, with a positive baseline Q0 = sum_i a_i N_i0 > 0, and let food demand be Q = sum_i a_i N_i with fixed coefficients a_i >= 0. For a horizon h,

```
Q_h / Q_0 = sum_i (a_i N_i0 / Q_0) * (N_ih / N_i0)
```

The weights are nonnegative and sum to one, so the ratio is a convex combination of the per-series stock ratios r_i = N_ih/N_i0. A convex combination cannot fall below the minimum r_i or exceed the maximum r_i, and placing all weight on the extremal series attains either bound. On the machine forecasts this gives:

| Year | Lower bound | Upper bound |
|---|---|---|
| 2024 | 0.954265 | 1.014286 |
| 2025 | 0.930317 | 1.020952 |
| 2026 | 0.897318 | 1.067906 |

The bounds are conditional on three-market coverage, fixed per-animal intensity and point forecasts; they are neither a global result nor a confidence interval, and the sign of growth is not identified.

### 3.4 Sourced worldwide anchor and conditional global quantities

The CONAFAB 2024 industry yearbook, crediting the 2024 Alltech survey, reports preliminary 2023 worldwide commercial pet-food production of 34.96 million metric tonnes. This is production, not measured consumption. With an analyst loss fraction lambda = 0.02 and zero net inventory change,

```
consumption 2023 = 34.96 * (1 - 0.02) = 34.2608 million tonnes
```

A zero-production-growth baseline holds consumption at 34.2608 million tonnes through 2026; an analyst 5% annual production-growth scenario gives consumption of 35.97384, 37.772532 and 39.6611586 million tonnes. Growth, loss and inventory values are assumptions, not estimates from the pet counts, and the vintage of the public source is not independently archived. Absolute global demand is therefore delivered only as conditional scenarios, not a completed forecast.

## 4. Question 3 — China's production, exports and the quantity–value bridge

### 4.1 Baseline monetary forecasts

Production value rose from 440.7 to 2,793 (100m CNY), reaching 6.3 times the 2019 level; the level-linear model forecasts 3,050.19, 3,598.72 and 4,147.25 (100m CNY). The 2019 export entry of 154.1 (100m CNY) is converted at the verified 2019 annual rate:

```
154.1 / 6.8985 = 22.34 (100m USD)
```

The harmonized export series is 22.34, 9.8, 12.2, 24.7, 39.6 (100m USD); the last-value model, selected on origin MAE, forecasts a flat 39.6 (100m USD). Currencies are never mixed in a ratio or subtraction, and no monetary value is labeled as tonnage.

### 4.2 Conditional quantity–value bridge

Border exports in USD and factory production in CNY are not automatically comparable. With a border-to-factory valuation factor v, a 2023 baseline export X0 = 39.6 (100m USD), production V0 = 2,793 (100m CNY), and FX0 = 7.0467 CNY/USD,

```
e0 = v * FX0 * X0 / V0
export ratio:   X_h/X0 = (G_h/G0) * (m_h/m0) * (p_export_h/p_export0)
domestic ratio: D_h/D0 = (rho cats_h + dogs_h) / (rho cats0 + dogs0)
V_h/V0 = (1-e0) * D_h/D0 * (p_dom_h/p_dom0)
         + e0 * (X_h/X0) * (FX_h/FX0) * (v_h/v0)
```

The machine implementation holds v_h/v0 = 1 and varies v0, evaluating 128 endpoint combinations per year over declared ranges (world growth 0/5%, share and price growth +/-2%, intensity rho 0.25/2, FX 0.95/1.05, valuation 0.5/1). The resulting envelopes:

| Year | Exports, 100m USD | Production, 100m CNY |
|---|---|---|
| 2024 | 38.03 – 43.26 | 2,748.99 – 3,079.31 |
| 2025 | 36.53 – 47.26 | 2,723.35 – 3,340.42 |
| 2026 | 35.08 – 51.63 | 2,698.09 – 3,612.57 |

[[FIG:bridge]]

These are scenario envelopes, not confidence intervals or known physical bounds, and future share and capacity must exist for any endpoint to be feasible. The parameters still needed to connect value to physical global demand — an empirical export share, per-animal quantities, uptake, prices and future FX — are not identified by the available data.

## 5. Question 4 — Tariff scenarios, analytic price choice and capacity thresholds

### 5.1 Coupled price and demand chain, with profit scope stated

For a baseline tariff t0 and a scenario tariff t1, define the tariff ratio g and the producer price multiplier mp, with absorption fraction kappa:

```
g  = (1+t1)/(1+t0)
mp = 1 - kappa * (1 - 1/g),          mp in [1/g, 1]
mb = mp * g                           buyer price multiplier
mq = mb^(-eta)                        quantity multiplier
```

Two profit scopes must be kept distinct. The exposed component, per unit of exposed baseline revenue, is

```
p_exposed(mp) = (mp - a) * (mp g)^(-eta)
```

The total profit per unit of total baseline export revenue, where s is the exposed share, is

```
P_total(mp) = (1-s)(1-a) + s * (mp - a) * (mp g)^(-eta)
```

The (1-s)(1-a) term is the unexposed baseline margin; the derivative argument below applies only to the exposed component. With this chain, full absorption kappa = 1 gives mp = 1/g, hence mb = 1 and mq = 1, and unit elasticity gives affected revenue mp*mq = 1/g for any kappa.

### 5.2 Proof of the analytic optimal producer price

On the exposed component, differentiate p_exposed(mp) = (mp - a)(mp g)^(-eta):

```
p'(mp) has the sign of  eta*a - (eta - 1)*mp
```

- If eta <= 1, then eta - 1 <= 0 and the sign is positive throughout the interval, so the maximum is at mp = 1 (no absorption).
- If eta > 1, the stationary point mp* = eta*a/(eta - 1) is the unique maximum; it is clipped into the feasible interval [1/g, 1].

No game payoff is invented; the result follows from the derivative sign. Absorption is defined as (1 - mp)/(1 - 1/g), zero when g = 1.

### 5.3 Robust price decision

Fixing one action before uncertainty is evaluated over eta in [0.5, 6] and a in [0.2, 0.8], with a non-loss-making constraint mp >= 0.8, the worst-case choice is mp = 0.96, absorption 0.15, buyer multiplier 1.309 and worst-case exposed profit 0.0318 per unit of exposed baseline revenue. The domain is an assumed screening region, not a measured probability distribution.

### 5.4 Diversification boundary and the 12 analyst scenarios

For a fraction d of baseline exposed business moved to replacement markets, with replacement operating margin b (including destination unit costs), old margin pi_old, quadratic execution cost c, fixed cost F, and attainable capacity D,

```
net gain/R0 = s (b - pi_old) d - c d^2 - F * I(d > 0)
unconstrained vertex: d* = s (b - pi_old) / (2c), clipped to [0, D]
```

The objective is concave in d, so the vertex is the only interior candidate; it is compared with no action after the fixed cost. The 12 analyst scenarios (s = 0.5, c = 0.02, pi_old = 0.1467) split into two groups:

- **8 no-move rows.** Every b = 0.10 row (b below pi_old) and the two zero-capacity b = 0.20 rows give d = 0.
- **4 positive-move rows, all b = 0.20.** At capacity 0.25 the move is d = 0.25 with gain 0.005417 before fixed cost and 0.000417 after F = 0.005. At capacity 0.75 the move is d = 2/3 with gain 0.008889 before fixed cost and 0.003889 after F = 0.005.

[[FIG:policy]]

These are analyst-table outcomes under assumed parameters, not measured business actions, and the positive moves remain conditional on the stated capacity and costs. Real diversification requires obtaining cost, margin and capacity quotes; none is measured here, and no unconditional relocation recommendation follows.

### 5.5 Checks and strategy discipline

The declared machine checks pass: unchanged tariffs reproduce all baseline multipliers; eta = 0 gives mq = 1; zero destination share and zero restoration fraction give zero tolerable cost; full absorption neutralizes buyer price and quantity; and quantities are monotone in the tariff for eta > 0. Strategy follows the break-even rule: a mitigation action is accepted only if its quoted cost is below the margin it preserves. No actual tariff rate, runtime or measured physical validation is claimed.

## 6. Strengths, limitations and evidence that would change the decision

**Strengths.** Every forecast is reproducible from the frozen data and selection rule; the validation protocol is strictly forward; currency harmonization and the price chain are internally consistent; and the convex-bound and derivative proofs give exact, non-empirical structural results rather than asserted claims.

**Limitations.** Ten series and five annual points identify parameters only within the chosen forms; a fitted form alone does not establish physical parameter identification; no confidence intervals, causal driver estimates or empirical policy elasticities exist; the worldwide anchor is preliminary production with unarchived vintage; and scenario envelopes are not confidence intervals.

**Evidence that would change the decision.** Independently sourced world consumption with measured loss and inventory data; quoted replacement-market margins, capacities and fixed costs; actual destination tariff schedules and observed pass-through; and a holdout evaluation of the frozen forecasts. Any one of these would replace a conditional parameter with an identified quantity and could alter the recommendation.

## References

1. 2024 APMCM Problem C official attachment tables (pet counts, production and export values), as transcribed in the receiver's `question.txt`.
2. CONAFAB 2024 industry yearbook (table crediting the 2024 Alltech survey), worldwide 2023 pet-food production, physical page 12: https://norel.com.mx/AnuarioCONAFAB2024.pdf
3. National Bureau of Statistics, verified 2019 annual exchange rate 6.8985 CNY/USD: https://www.stats.gov.cn/xxgk/sjfb/tjgb2020/202006/t20200617_1768655.html
4. National Bureau of Statistics, verified 2023 annual exchange rate 7.0467 CNY/USD: https://www.stats.gov.cn/sj/zxfb/202402/t20240228_1947915.html

## Appendix. Algorithm pseudocode

```
for each series:
    for origin in (2021, 2022):
        fit each candidate on the training window only
        record forecast, actual, absolute error in original units
    select candidate by mean origin error; ties -> simpler
    refit selected candidate on 2019-2023; record 2024-2026 forecasts
for each linked year:
    enumerate 128 endpoint combinations from declared scenario ranges
    record export and production values; take min/max envelopes
for each tariff scenario:
    compute g, mp, mb, mq; apply analytic price rule to exposed component
    compute diversification vertex; compare with no action after fixed cost
freeze all parameters and predictions; no refit after evaluation
```
