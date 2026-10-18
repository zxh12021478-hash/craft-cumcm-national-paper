## Summary

This study evaluates two policies, L and R, against the existing baseline on batches of 100 synthetic requests. All costs are in CNY per batch, and an 85% service floor is mandatory in every setting.

For the base setting (Q1), the existing baseline costs 100 CNY and serves 86 of 100 requests; policy L costs 88 CNY and serves 92; policy R costs 96 CNY and serves 97. Both L and R meet the service floor, and L is the lower-cost feasible policy. Relative to the baseline, L reduces total batch cost by 12% and raises the service rate from 86% to 92%, a gain of 6 percentage points.

For the specified stress setting (Q2), L costs 91 CNY with a service rate of 78%, and R costs 103 CNY with a service rate of 88%. Because the 85% service floor is mandatory, R is the only feasible policy among the two tested policies; lower cost cannot compensate for violating the floor.

The decision (Q3) is therefore conditional: recommend L for the tested base setting and R for the specified stress setting. The mechanism is constraint-first policy switching, not a new optimization algorithm. All results are supplied simulations on synthetic batches; intermediate and external settings, field performance, statistical confidence levels, and win probabilities are not established, and the reported numbers cannot be independently reproduced because the simulator is not supplied.
