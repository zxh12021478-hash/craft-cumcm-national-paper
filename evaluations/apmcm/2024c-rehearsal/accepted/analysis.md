# 2024C Pet Industry — Bounded Numerical Analysis (Q1–Q4), v2

Sources: the official attachment tables (visually checked), the National Bureau of Statistics verified 2019 annual exchange rate 6.8985 CNY/USD, and explicitly labeled analyst scenarios. Not all numbers come from the attachments. Pet counts are in 10,000 animals; monetary values are in 100 millions (100m CNY or 100m USD as labeled). The three candidate models (last-value, level-linear, log-linear) are compared at two strictly forward one-step origins (train through 2021 → 2022; through 2022 → 2023), selected by two-origin MAE with ties going to the simpler model. v2 changes only the Q4 coupling and adds fixed-intensity bounds; the 10 series, selections and validation MAEs are unchanged from v1 and independently confirmed.

## Q1. China by pet type, 2024–26 forecast

- **Cats:** 4,412 (2019) → 6,980 (2023), +58.2%; level-linear wins (origin MAE 184.2 vs 276.8/587.0) and forecasts 7,762 / 8,443 / 9,124.
- **Dogs:** 5,503 → 5,175, down 6.0% overall; log-linear wins narrowly (MAE 141.2 vs 142.3/183.0) and forecasts 5,066 / 4,994 / 4,923.
- Drivers (urban income, housing scale, licensing/time costs) are hypotheses consistent with the observed cat–dog divergence, not causal effects identifiable from five annual points.

## Q2. Overseas markets, fixed-intensity bounds and conditional global demand

- Per-type forecasts: America cat (log-linear) 7,118 / 6,866 / 6,622; America dog flat 8,010; France cat flat 1,660; France dog 945 / 999 / 1,057; Germany cat flat 1,570; Germany dog 1,065 / 1,072 / 1,079.
- Three-market aggregate (six series): 20,660 (2023) → 20,368 / 20,177 / 19,998; index 100 → 98.6 / 97.7 / 96.8. Three named countries, not world demand.
- **New convex-combination bounds (machine-computed):** with fixed nonnegative per-animal food coefficients, the 2026/2023 food-demand ratio lies between 0.897318 and 1.067906 (2024: 0.954265–1.014286; 2025: 0.930317–1.020952). The sign of growth is not determined by these data. Scope: three markets, fixed intensity, point forecasts; not global, not a confidence interval.
- **Conditional global demand scenarios:** CONAFAB’s 2024 industry yearbook (physical p.12, printed p.10), crediting the 2024 Alltech survey, reports preliminary 2023 global pet-food production of 34.96 million tonnes. This is production, not measured consumption. With an assumed 2% loss fraction and unchanged net inventories, a zero-production-growth baseline gives consumption of 34.2608 million tonnes annually in 2024–2026; an analyst 5% annual production-growth scenario gives 35.97384 / 37.772532 / 39.6611586 million tonnes. Neither growth nor loss is estimated from the five pet-count observations. Global demand validation and its drivers remain incomplete. No three-country growth bound is transferred to the world.

## Q3. China production and exports (unchanged policy)

- **Production, 100m CNY:** 440.7 (2019) → 2,793 (2023), 6.3-fold; level-linear wins and forecasts 3,050 / 3,599 / 4,147 (100m CNY).
- **Exports, 100m USD:** 2019 entry 154.1 (100m CNY) converts to 22.34 (100m USD) at 6.8985; 2020–23 entries are already USD (9.8 → 39.6); last-value wins and forecasts a flat 39.6 (100m USD) per year.
- No mixed-currency arithmetic; monetary values are never tonnes. Linking value forecasts to physical global demand still lacks a calibrated global consumption series, per-animal quantities, uptake, prices and future FX assumptions. The production anchor alone does not identify that link.

## Q4. Unified tariff chain (v2 repair), profit and restoration cost

- Coupled chain (analyst scenario): g = (1+t1)/(1+t0); producer price mp = 1 − κ(1 − 1/g); buyer price mb = mp·g; quantity mq = mb^(−η); revenue multiplier 1 − s + s·mp·mq. This removes the v1 error where the exporter cut price but quantity still responded to the pure tariff ratio.
- With unit cost a = 0.8 of baseline producer price (analyst assumption), profit per baseline export revenue is (1−s)(1−a) + s(mp−a)·mq; tolerable mitigation cost for restoration fraction r is Cmax = max(0, r·R0·((1−a) − profit/R0)), R0 = 39.6 (100m USD). Full restoration requires r = 1; costs are never unconditional.
- All checks pass: κ = 1 gives buyer price and quantity exactly 1; η = 1 gives affected revenue mp·mq = 1/g for every κ (0.7333 at t1 = 0.5); unchanged tariff gives all multipliers 1; s = 0 and r = 0 give zero cost; η = 0 gives mq = 1; quantities are monotone in the tariff.
- Example: at t1 = 0.5, η = 1, κ = 0.5, s = 1, Cmax is 2.84 (100m USD) at r = 0.5 and 5.69 at r = 1. Mitigation is adopted only if its cost is below the restored margin; diversification is not recommended regardless of cost. Tariff, elasticity, absorption, share and cost parameters are analyst scenarios, not measured policy or causal estimates.


## Source and reproducibility limits

The global anchor is preliminary production from https://norel.com.mx/AnuarioCONAFAB2024.pdf, physical page 12. The downloaded document’s creation/modification metadata predates the historical contest, but public availability at that date was not independently archived. Later 2025/2026 revisions were excluded. The 2019 annual exchange rate is from https://www.stats.gov.cn/xxgk/sjfb/tjgb2020/202006/t20200617_1768655.html .

The pet-count holdouts are chronological; actual annual observation publication dates were not audited, so this is not verified real-time forecasting. The policy calculation describes specified operating/mitigation scenarios, not an empirically calibrated optimal firm or government strategy. Run `solve.py` then `add_global_anchor.py` to reproduce the core outputs and the later source/accounting supplement respectively.


The symbolic base `Q0_consumption` means 2023 consumption. Under the supplement’s zero-inventory-change/2%-loss assumptions, it equals 0.98 × 34.96 = 34.2608 million tonnes; it must not be set directly to the production anchor. Currency harmonization changes the 2019–2020 export decline from the invalid mixed-currency 93.64% to a still substantial 56.13%; it does not remove the decline. No selected series has a tie at the declared MAE tolerance.
