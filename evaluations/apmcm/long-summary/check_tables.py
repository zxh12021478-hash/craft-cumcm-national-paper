"""Recheck transcribed table facts; this does not reconstruct image contours."""
import json
from decimal import Decimal as D
from pathlib import Path


def evaluate(facts):
    tables = []
    for table in facts["contour_tables"]:
        rows = table["rows"]
        ids = [row["id"] for row in rows]
        total = sum((D(row["length_px"]) for row in rows), D(0))
        gap = abs(total - D(table["reported_total_px"]))
        bound = (len(rows) + 1) * D(table["nearest_display_increment_px"]) / 2
        tables.append({
            "table": table["table"],
            "distinct_listed_ids": len(set(ids)),
            "duplicate_ids": len(ids) != len(set(ids)),
            "reported_count": table["reported_count"],
            "count_matches_listed_ids": table["reported_count"] == len(set(ids)),
            "summed_point_counts": sum(row["points"] for row in rows),
            "sum_displayed_lengths_px": str(total),
            "length_gap_px": str(gap),
            "nearest_rounding_bound_px": str(bound),
            "length_compatible_with_rounding": gap <= bound,
            "true_contour_count_status": "unresolved: original exported roster unavailable",
        })
    c = facts["calibration"]
    mean = sum(map(D, c["plate_spacings_px"])) / len(c["plate_spacings_px"])
    scale = D(c["spacing_mm"]) / mean
    total_mm = sum(map(D, c["contour_lengths_px"])) * scale
    displayed_sum = sum(map(D, c["reported_lengths_mm"]))
    reported = D(c["reported_total_mm"])
    increment = D(c["nearest_display_increment_mm"])
    bound = (len(c["reported_lengths_mm"]) + 1) * increment / 2
    calibration = {
        "mean_spacing_px": str(mean),
        "scale_mm_per_px": str(scale),
        "converted_total_mm": str(total_mm),
        "converted_total_rounds_to_reported": abs(total_mm - reported) <= increment / 2,
        "sum_displayed_parts_mm": str(displayed_sum),
        "sum_total_gap_mm": str(abs(displayed_sum - reported)),
        "nearest_rounding_bound_mm": str(bound),
        "sum_compatible_with_rounding": abs(displayed_sum - reported) <= bound,
        "ratio_to_conflicting_scale": str(scale / D(c["conflicting_scale_mm_per_px"])),
        "physical_accuracy_status": "not verified by table arithmetic",
    }
    return {"contour_tables": tables, "calibration": calibration,
            "scope": "Original table claims remain unresolved; no model reproduction or ready Summary"}


if __name__ == "__main__":
    facts = json.loads(Path(__file__).with_name("table-facts.json").read_text())
    report = evaluate(facts)
    assert [t["distinct_listed_ids"] for t in report["contour_tables"]] == [14, 33]
    assert [t["summed_point_counts"] for t in report["contour_tables"]] == [3623, 7995]
    assert all(t["length_compatible_with_rounding"] for t in report["contour_tables"])
    assert not any(t["count_matches_listed_ids"] for t in report["contour_tables"])
    assert report["calibration"]["converted_total_rounds_to_reported"]
    assert report["calibration"]["sum_compatible_with_rounding"]
    print(json.dumps(report, indent=2))
