import pytest
from pydantic import ValidationError

from printdesk import materials
from printdesk.cli import build_part
from printdesk.parts import mounting_plate as mp


def test_default_plate_builds_and_validates():
    solid, report, _ = build_part("mounting_plate", {}, "PLA")
    assert report.ok, report.errors
    bb = solid.bounding_box()
    assert bb.size.X == pytest.approx(40, abs=0.01)
    assert bb.size.Z == pytest.approx(4, abs=0.01)


def test_hole_diameter_is_compensated_per_material():
    pla, tpu = materials.get("PLA"), materials.get("TPU")
    from printdesk import fasteners
    assert fasteners.hole_diameter("M3", pla) == pytest.approx(3.6)
    assert fasteners.hole_diameter("M3", tpu) == pytest.approx(3.5)


def test_hole_volume_removed_matches_cylinder():
    import math
    params = {"width": 40, "depth": 30, "thickness": 4, "corner_radius": 0,
              "holes": [{"x": 0, "y": 0, "screw": "M4", "style": "through"}]}
    solid, report, _ = build_part("mounting_plate", params, "PLA")
    assert report.ok, report.errors
    d = 4.5 + 0.20
    expected = 40 * 30 * 4 - math.pi * (d / 2) ** 2 * 4
    assert solid.volume == pytest.approx(expected, rel=0.002)


def test_hole_too_close_to_edge_is_rejected():
    params = {"holes": [{"x": 19, "y": 0, "screw": "M3"}]}
    _, report, _ = build_part("mounting_plate", params, "PETG-CF")
    assert not report.ok
    assert any("wall" in e for e in report.errors)


def test_oversize_plate_rejected_by_schema():
    with pytest.raises(ValidationError):
        mp.Params(width=300)


def test_unknown_screw_rejected():
    with pytest.raises(ValueError):
        mp.Params(holes=[{"x": 0, "y": 0, "screw": "M7"}])


@pytest.mark.parametrize("style", ["through", "counterbore", "countersink", "insert"])
def test_all_hole_styles_validate(style):
    params = {"width": 50, "depth": 40, "thickness": 8,
              "holes": [{"x": 0, "y": 0, "screw": "M3", "style": style}]}
    _, report, _ = build_part("mounting_plate", params, "PLA")
    assert report.ok, report.errors
