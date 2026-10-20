# Preference and measurement conditions for a ranking decision

## Summary
We compare three options X, Y and Z under two already normalized benefit criteria, with values X=(9,3), Y=(6,8) and Z=(5,2), using scores w a+(1-w)b for w between zero and one. At w=0.4, X scores 5.4, Y scores 7.2 and Z scores 3.2, so Y is selected. Z is strictly dominated by X and is never a maximizer. The nominal score of X is 3+6w, that of Y is 8-2w, and that of Z is 2+3w. X and Y tie at w=5/8=0.625, with a score of 6.75; Y wins below this weight and X above it. When the first criterion of X independently varies between 8 and 10, and Y's between 5 and 7, the difference in their first criteria ranges between 1 and 5. The four corner differences are 1,3,3 and 5. The full score difference lies between 6w-5 and 10w-5. Hence Y is guaranteed no worse than X for w<=1/2, while X is guaranteed no worse for w>=5/6. In between these bounds, the winner depends on the actual criterion values, not just on the nominal weights. At either boundary an extreme perturbation can produce a tie, so the guarantee is weak rather than strict. X continues to strictly dominate Z throughout the interval inputs. These are exact analytic conditions over a bounded uncertainty set and specified weights; no score is a probability and no random perturbation frequency is interpreted as reliability.

## Model
The criteria are benefit values, already normalized by the task. No further scaling, fitted weights or stochastic model is introduced. A score is S_i(w)=w a_i+(1-w)b_i. We use dominance and linear score inequalities to derive complete weight regions rather than infer them from a sampled weight grid. These are synthetic choices, not measured investment, safety or field outcomes.

## Q1: fixed preference
At w=0.4, the scores of X,Y,Z are 5.4,7.2,3.2, respectively. Y is the unique winner, scoring 7.2. This answers the specified fixed preference, not all preferences.

## Q2: nominal weight regions
S_X=3+6w and S_Y=8-2w, so S_X-S_Y=8w-5. Y wins for 0<=w<5/8; X and Y tie at w=5/8; X wins for 5/8<w<=1. The nominal score at the tie is 6.75. Z is strictly dominated by X on both criteria and cannot win for any allowed w, including endpoints. No unique unconditional recommendation is supported when the weight is unknown.

## Q3: joint bounded perturbations
Let a_X in [8,10] and a_Y in [5,7], with these variations independent as a set constraint, not a probabilistic statement. Their difference d=a_X-a_Y ranges from 1 to 5. Then S_X-S_Y=w(d+5)-5, which lies in [6w-5,10w-5]. Y is guaranteed no worse for 0<=w<=1/2, because the upper bound is nonpositive. X is guaranteed no worse for 5/6<=w<=1, because the lower bound is nonnegative. If 1/2<w<5/6, permitted perturbations can reverse the ranking, so no uniformly best option is justified. At w=1/2 and w=5/6, equality is possible for an extreme perturbation; the guarantees mean weak optimality, not strict victory. Even under perturbation X has first criterion at least8>5 and second3>2, so Z remains strictly dominated.

## Conclusion and scope
Select Y at the specified weight0.4. With unknown nominal weights, report the threshold5/8 and tie rather than invent an unconditional winner. With bounded measurement perturbations, report the two robust weak-optimality regions and retain a conditional answer in between. Interval bounds here are not confidence intervals, and weight regions are not probabilities. The inequalities prove the stated finite-option, bounded-input result, without validating real measurements or preferences.
