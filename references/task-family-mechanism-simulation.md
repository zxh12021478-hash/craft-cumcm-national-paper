# Mechanism, simulation, and differential-equation kit

## Applicability and baseline

Use when the task asks how a system evolves, why a phenomenon occurs, or how physical, biological,
or economic flows respond. Start from conservation, limiting cases, or a simplified analytical/coarse model.

## Construction contract

- Define states, flows, initial and boundary conditions, parameter units, observation equations, and numerical scheme.
- Separate measured, fitted, literature, inferred, and assumed parameters.
- Check structural and practical identifiability before interpreting individual parameters.
- Propagate parameter and observation uncertainty to the requested prediction or decision.

## Independent verifier

Check dimensions and conservation from primitive trajectories; reproduce a limiting or closed-form
case; run step/grid convergence and an alternate integrator or independently coded residual. Use
synthetic recovery to test identifiability when truth is unavailable.

## Outputs and failure boundary

Deliver a mechanism diagram, parameter-source table, residual and convergence evidence, uncertainty
bands, and a validity region. Visual agreement to one trajectory does not validate parameters or
extrapolation; narrow the claim when identifiability or conservation fails.
