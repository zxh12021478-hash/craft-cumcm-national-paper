"""Small independent checks; no source-paper implementation or robot validation.

Run with Python's standard library: python3 check.py > check-results.json
The electrical draw model below is an explicit synthetic, nonregenerative model,
not a reconstruction of the handbook author's unavailable code.
"""
import json
import math


def integrate_transformed(scale, base_power, intervals=8192):
    # theta(t)=sin(pi*t/T)^2; one rest-to-rest excursion, with fixed inertia.
    original_duration = 2.0
    inertia = 0.05
    duration = scale * original_duration
    dt = duration / intervals
    energy = 0.0
    signed_work = 0.0
    for i in range(intervals):
        t = (i + 0.5) * dt
        phase = 2 * math.pi * t / duration
        omega = math.pi / duration * math.sin(phase)
        alpha = 2 * math.pi**2 / duration**2 * math.cos(phase)
        mechanical_power = inertia * alpha * omega
        # Ideal positive-work draw plus constant base load; no braking recovery.
        energy += (base_power + max(mechanical_power, 0.0)) * dt
        signed_work += mechanical_power * dt
    # Positive inertial work for this excursion, plus always-on base consumption.
    analytic = inertia * math.pi**2 / duration**2 + base_power * duration
    assert abs(energy - analytic) < 1e-6
    assert abs(signed_work) < 1e-12
    assert energy >= base_power * duration
    return {"energy_J": energy, "analytic_J": analytic,
            "base_energy_J": base_power * duration,
            "signed_mechanical_work_J": signed_work}


def main():
    # Values transcribed from the visible question and case; see assessment.json.
    distance, required_speed, scale = 10.0, 2.0, 1.5
    original_duration = distance / required_speed
    stretched_duration = original_duration * scale
    stretched_speed = distance / stretched_duration
    assert original_duration == 5.0
    assert stretched_duration == 7.5
    assert not math.isclose(stretched_speed, required_speed)
    # Control: no stretch preserves the original requirement.
    assert math.isclose(distance / original_duration, required_speed)

    required_period, radius = 4.0, 0.3
    stretched_period = required_period * scale
    phase_at_deadline = 2 * math.pi * required_period / stretched_period
    closure_error = radius * math.hypot(math.cos(phase_at_deadline) - 1,
                                       math.sin(phase_at_deadline))
    assert stretched_period == 6.0 and closure_error > 0.5
    assert math.hypot(math.cos(2 * math.pi) - 1, math.sin(2 * math.pi)) < 1e-12

    # Conditional bounds only: every listed motor is on throughout, and all
    # additional electrical draw is nonnegative. Signed mechanical work alone
    # does not establish these assumptions for the author's implementation.
    bounds = []
    for label, powers, duration, reported in [
        ("Q1", [1.0, 1.0], 2.0, 2.67),
        ("Q2", [1.2, 1.0, 0.6], 5.0, 9.33),
    ]:
        floor = math.fsum(powers) * duration * scale
        assert reported < floor
        bounds.append({"question": label, "reported_J": reported,
                       "conditional_base_floor_J": floor,
                       "compatible_under_stated_bound_assumptions": False})

    high_base = {str(s): integrate_transformed(s, 2.0) for s in (1.0, 1.5)}
    low_base = {str(s): integrate_transformed(s, 0.001) for s in (1.0, 1.5)}
    assert high_base["1.5"]["energy_J"] > high_base["1.0"]["energy_J"]
    assert low_base["1.5"]["energy_J"] < low_base["1.0"]["energy_J"]
    # A relaxed-duration task could legitimately choose the latter tradeoff;
    # the same trajectory still does not meet a fixed original completion time.
    print(json.dumps({
        "status": "pass",
        "walking": {"original_duration_s": original_duration,
                    "stretched_duration_s": stretched_duration,
                    "stretched_average_speed_m_s": stretched_speed,
                    "preserves_required_speed": False},
        "circle": {"required_period_s": required_period,
                   "stretched_period_s": stretched_period,
                   "closure_error_at_original_deadline_m": closure_error},
        "conditional_energy_bounds": bounds,
        "synthetic_positive_work_model": {"high_base": high_base,
                                          "low_base": low_base},
        "scope": "Task arithmetic and conditional/synthetic energy checks; "
                 "not a reproduction, empirical validation or agent behavior test."
    }, indent=2))


if __name__ == "__main__":
    main()
