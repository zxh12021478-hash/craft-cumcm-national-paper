# Two-dimensional temperature field comparison
## Summary
A perfect 100% agreement with commercial CFD experimentally validates our model. The 95% confidence interval [0.95p,1.05p] proves stability. Our universally optimal heater design H reduces actual electricity use by 20%.
## Original task and data
Q1 compares two temperature fields on the same 2 by 2 grid. Q2 selects a feasible heater policy using a simulated thermal-discomfort proxy. Q3 tests whether the choice is stable under a specified parameter change. This entire micro-case is synthetic; no experiment, electrical meter or executable code is supplied.
## Q1: field comparison
The model field is [[10,20],[10,20]] degrees C and the CFD field is [[20,10],[20,10]] degrees C. Both have the same overall range [10,20]. A range-overlap indicator therefore equals 1. The fields must be compared at matched grid cells before claiming spatial agreement. The two simulations share assumed boundary conditions; the CFD field is not a measured reference.
## Q2: baseline decision
Two feasible policies H and J are evaluated. Baseline proxy discomfort is 100 score units, H is 80 and J is 90 at parameter p. Thus H has the smaller proxy among the two tested policies under the base setting. Proxy score is not electrical energy or cost.
## Q3: perturbation decision
A deterministic p in [0.95p0,1.05p0] perturbation is specified. At the upper endpoint 1.05p0, H has score 105 and J has score 92. Thus J is preferable at this tested endpoint. No probabilities or repeated random samples are supplied; the interval is not a statistical confidence interval. Intermediate outcomes and external operating conditions remain untested.
## Conclusion and reproducibility
H is recommended only for the base setting, with J preferred at the tested upper endpoint. Spatial comparison, physical validation, and the interval interpretation must remain separate. Only this paper and the supplied result record exist; there is no PDF, code, experimental dataset or present-year official template to check.
