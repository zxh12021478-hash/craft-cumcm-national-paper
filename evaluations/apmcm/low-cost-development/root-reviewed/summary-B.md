## Summary

We evaluate constraint-first selection between policies L and R on batches of 100 synthetic requests, with a mandatory 85% service floor. At the base setting, L costs 88 CNY per batch and serves 92% of requests, compared with the baseline’s 100 CNY and 86%: a 12% cost reduction and a service gain of 6 percentage points. R costs 96 CNY and serves 97%, so both candidates are feasible and L is cheaper.

Under the specified stress setting, L costs 91 CNY but serves only 78%, violating the service floor; R costs 103 CNY and serves 88%, making it the only feasible tested candidate. We therefore recommend L at the tested base setting and R under the specified stress. These supplied simulation results establish a conditional choice rather than a new optimizer or a universal switching threshold. Intermediate conditions and field performance remain unvalidated.
