# Network, path, spatial, and trajectory kit

## Applicability and baseline

Use when nodes, edges, locations, geometry, fields, maps, or trajectories define the problem. Start
with shortest path, minimum spanning structure, simple flow, nearest-neighbor, or direct geometry as appropriate.

## Construction contract

- Define coordinate reference, distance metric, node/edge semantics, direction, capacity, time dependence, and disconnected cases.
- Audit graph or spatial construction separately from the solver.
- Test key-edge/location perturbations, ties, disconnected components, capacity and flow conservation, and scaling.
- For trajectories, state sampling, interpolation, speed/curvature limits, collision semantics, and boundary handling.

## Independent verifier

Rebuild a small graph or spatial instance from raw coordinates/edges; recompute path length, capacity,
flow balance, geometric invariants, and trajectory feasibility independently. Compare selected small
cases with enumeration or a trusted basic algorithm.

## Outputs and failure boundary

Deliver maps, bottleneck and path/flow decompositions, resilience scenarios, coordinate metadata,
and operational recommendations. Reject conclusions that depend on an unstated distance convention,
silent disconnection handling, or visually plausible but infeasible trajectories.
