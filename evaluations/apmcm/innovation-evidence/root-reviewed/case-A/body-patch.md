## Results

B and T complete all twenty specified scenarios and satisfy every recorded hard constraint. Their complete operating costs are CNY 2,000 and 1,900, respectively, so T costs 5% less on this set. TM completes sixteen scenarios, but terminates with negative terminal inventory on the four boundary scenarios. Its logged cost of CNY 10 on each terminated run is partial and cannot establish a valid complete operating cost.

| Scenario group | Cases | B complete cost (CNY) | T complete cost (CNY) | TM complete cost (CNY) |
|---|---:|---:|---:|---:|
| quiet | 8 | 800 | 760 | 640 |
| peak | 8 | 800 | 760 | 1,040 |
| boundary | 4 | 400 | 380 | No valid plan |
| full specified set | 20 | 2,000 | 1,900 | No valid complete total |

Over the sixteen scenarios completed by all three policies, TM costs CNY 1,680 versus 1,600 for B and 1,520 for T. TM therefore costs 5% more than B on this common subset; this comparison does not remove the four failed scenarios from the feasibility assessment. TM's recorded hard-constraint pass share is 16/20, or 80%. It is a descriptive share of the supplied scenario set, not a probability of reliable deployment.

## Discussion and conclusion

Among the three compared selected policies, T is the least-cost policy satisfying the recorded constraints on all twenty specified scenarios. We recommend T for this set; TM is not admissible under the stated hard constraints. The quiet-subset saving does not support a recommendation of TM over the full set.

The observations do not isolate M's contribution. The compared T and TM configurations used different parameter searches and budgets, and configurations were selected on the same scenarios used in the comparison. Their differences describe the selected policies, not the conditional effect of switching M at a fixed configuration. A controlled M-on/M-off comparison at one fixed backbone and configuration could address that narrower effect if the implementation and configuration become available; a full factorial study is not required merely to answer it.

These conclusions are arithmetic and decision checks on the supplied fixture. The absent implementation, configuration-selection records, performance beyond the specified cases and real deployment remain unverified. No change to the original constraints is justified by TM's failures.
