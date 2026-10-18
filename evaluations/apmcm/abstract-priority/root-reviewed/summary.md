# Summary

We link four-week-ahead demand forecasts to capacity-constrained inventory decisions in a synthetic planning study. On 20 common nonoverlapping out-of-sample targets, regression reduces RMSE from the seasonal-naive baseline’s 10 items to 8 items (20%), using only information available at each forecast origin.

Forecasts determine buffer requirements for inventory planning. Among 12 prespecified feasible strategies evaluated under equal service requirements on the same synthetic demand trajectory, strategy P has the lowest total cost: 120 CNY versus 150 CNY for seasonal-naive planning, a 20% reduction. The reported capacity and stock-balance checks satisfy a tolerance of 1e-8; the optimization claim is limited to the evaluated candidate set.

Across 20 prespecified demand perturbation scenarios spanning −10% to +10%, P remains the least-cost evaluated strategy in 18. Strategy R is preferable in the other two, both at +10% demand. We therefore recommend P for the tested base setting and R for those two high-demand cases. This scenario count carries no probability interpretation, and performance between or beyond the tested scenarios is unestablished. The simulated cost gains require external validation before deployment.
