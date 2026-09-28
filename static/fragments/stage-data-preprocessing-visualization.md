# Stage: data preprocessing and exploratory visualization

Read `references/validation-playbook.md` and `references/visualization-standards.md`.

## Procedure

1. Preserve raw data unchanged; create a deterministic derived-data pipeline.
2. Build a data dictionary with field meaning, unit, type, range, source, missingness, and role.
3. Check duplicate entities, inconsistent identifiers, impossible values, time leakage, target leakage, censoring, repeated measures, and sample-selection bias.
4. Quantify missingness and outliers before choosing treatment. Report how many rows or values change.
5. Match preprocessing to mechanism: compositional data, circular variables, censored values, irregular time grids, spatial coordinates, and grouped observations require specialized treatment.
6. Create only decision-relevant exploratory plots. Each plot must test an assumption, motivate a model, reveal a pattern, or expose a defect.
7. Fit preprocessing inside resampling folds when prediction is evaluated out of sample.
8. Save processed data, transformation parameters, seeds, and a transformation log.

## Required evidence

- row/column counts before and after processing;
- missingness and anomaly summary;
- distribution and dependency diagnostics;
- justification for scaling, encoding, imputation, smoothing, or aggregation;
- leakage audit;
- sensitivity to at least one plausible alternative preprocessing choice when consequential.

## Prohibitions

Do not delete outliers solely because they worsen the model. Do not infer substitution, complementarity, or causality from a correlation heatmap alone.

