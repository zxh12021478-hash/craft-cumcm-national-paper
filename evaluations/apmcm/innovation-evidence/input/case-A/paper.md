# A storage-dispatch policy with an adaptive look-ahead module

## Task
Choose a dispatch policy that meets every hard storage and supply constraint on the specified synthetic scenarios, then minimizes complete operating cost in CNY per scenario. Demand cannot be dropped and terminal inventory must be nonnegative. Explain whether the adaptive module M improves the policy. Scenario labels describe the generator, not an observed frequency distribution. There is no supplied probability law for future scenarios.

## Summary
Our adaptive policy TM delivers a 20% operating-cost saving, while maintaining 90% reliability. Its superiority is caused by the new look-ahead module. The validated policy is recommended for all demand conditions.

## Methods
B is the fixed reference controller. T changes B's tuning but has no M module. TM combines T with M. Twenty synthetic scenario IDs S01–S20 are used both to select configurations and to construct the final comparison table. T selects the lowest-cost feasible setting on those scenarios from 6 configurations. TM selects from 60 configurations on those same scenarios; its selection score ignores runs that terminate before the end. There is no separate evaluation set. M has a potentially useful anticipation mechanism but no additional measured inputs. All controllers use the same information at dispatch time. No M-without-T variant was executed. We did not retain the per-configuration tuning scores or source code in this development fixture.

## Results
The accompanying runs.csv lists the final selected configurations. B and T complete all twenty scenarios and satisfy every recorded hard constraint. TM completes S01–S16 and satisfies the recorded hard constraints on those completed scenarios; S17–S20 terminate after a negative terminal inventory, so their logged cost covers only the executed portion. Such a run is not a valid dispatch plan. The table below sums the eight scenarios labelled quiet only: B 800 CNY, TM 640 CNY; hence a 20% saving. In the eight peak scenarios, B costs 800 and TM costs 1040 CNY. The four boundary scenarios are absent from our displayed savings table. The reported reliability is the share of runs that pass the hard constraints, on this scenario set; the abstract reports 90%. We interpret this as the probability of reliable deployment. No measurement or independent held-out simulation was performed.

## Discussion and conclusion
TM is recommended because its new module is responsible for the improvement over B. T's contribution is assumed negligible. We did not measure computation time or evaluate a common tuning budget. The scenario generator has no supplied likelihoods. No theorem of global optimality is claimed. The paper and CSV are the entire available evidence in this synthetic exercise; a numerical recalculation cannot verify that the absent implementation matches the stated dispatch equations.
