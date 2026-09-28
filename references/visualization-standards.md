# Visualization standards

## Every figure must answer a question

Classify each figure as mechanism, data diagnostic, model comparison, validation, uncertainty, optimization, policy boundary, or final answer. Delete figures with no analytical role.

## Flowcharts must match the implementation

Every node must correspond to an actual input, transformation, model, decision, validation step, or
output that can be located in the paper, code, data, or result ledger. Show branches, feedback, and
subproblem dependencies only when they are implemented. Delete generic model-name inventories,
decorative boxes, and copied template paths. A flowchart is a navigation and dependency device, not
a substitute for definitions, derivation, or evidence.

## Required design

- descriptive title or caption stating the insight;
- labeled axes with units;
- readable font at final page size;
- colorblind-safe palette and redundant encodings when important;
- uncertainty bands or error bars when estimates are uncertain;
- baseline or reference line for comparisons;
- annotations for thresholds, optima, and infeasible regions;
- consistent terminology and precision with the paper.

Avoid perspective-distorting 3D bars, surfaces used only as decoration, and exploded or 3D pie
charts. Use radar charts only when all axes have a justified common direction and scale and the
polygon shape answers a real comparison question; otherwise use aligned dots, intervals, small
multiples, or a table. Do not use dual axes unless the visual relationship is essential and cannot
be stated more clearly with aligned panels.

## Tables

Use tables for exact values and comparisons. Include units, scenario, rounding rule, and the best/feasible solution marker. Avoid dumping raw outputs.

## Quality checks

- inspect in grayscale;
- inspect at 100% final-page zoom;
- ensure captions make sense without reading the plotting code;
- verify every figure and table is referenced in the text;
- verify numbers against the result ledger.
- verify every flowchart node and edge against the implemented artifact chain;
- verify chart geometry does not distort magnitude or imply unsupported comparability.
