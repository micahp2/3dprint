import pytest
from build123d import Vector
from pydantic import ValidationError

from printdesk.cli import build_part
from printdesk.parts import camera_mount as cm


def test_defaults_build_and_validate():
    solid, report, p = build_part("camera_mount", {}, "ASA")
    assert report.ok, report.errors
    bb = solid.bounding_box()
    assert bb.size.X == pytest.approx(121.4, abs=0.01)
    assert bb.size.Z == pytest.approx(3 + 14, abs=0.01)


def test_camera_pocket_is_void_and_lens_window_is_open():
    solid, _, p = build_part("camera_mount", {}, "ASA")
    total = p.flange_thickness + p.pod_height
    assert not solid.is_inside(Vector(0, 0, total / 2))          # inside the pocket
    assert not solid.is_inside(Vector(0, 0, total - 0.8))        # through the lens window
    assert solid.is_inside(Vector(p.pod_w / 2 - 0.5, 0, total / 2))  # pod wall present
    assert solid.is_inside(Vector(0, p.pod_d / 2 - 0.5, total / 2))


def test_pod_fills_the_opening():
    p = cm.Params()
    assert p.pod_w == pytest.approx(p.opening_w - p.opening_gap)
    assert p.pod_d == pytest.approx(p.opening_h - p.opening_gap)
    solid, _, _ = build_part("camera_mount", {}, "ASA")
    bb = solid.bounding_box()
    assert bb.size.Y >= p.pod_d      # flange carries the pod


def test_opening_too_small_for_the_camera_is_rejected():
    with pytest.raises(ValidationError):
        cm.Params(opening_w=26)          # leaves under 2 mm wall around the camera


def test_bolt_spacing_drives_hole_positions():
    solid, report, p = build_part("camera_mount", {"bolt_spacing": 90}, "ASA")
    assert report.ok, report.errors
    assert not solid.is_inside(Vector(45, 0, 1.5))
    assert solid.is_inside(Vector(cm.Params().bolt_spacing / 2, 0, 1.5))   # default position is now solid


def test_default_spacing_matches_the_two_caliper_readings():
    p = cm.Params()
    outer, inner = 109.79, 96.69          # far edge to far edge, near edge to near edge
    assert p.bolt_spacing == pytest.approx((outer + inner) / 2, abs=0.01)
    assert (outer - inner) / 2 == pytest.approx(6.55, abs=0.01)   # implied hole diameter


def test_bolt_holes_clear_an_m6_bolt():
    from printdesk import fasteners, materials
    d = fasteners.hole_diameter("M6", materials.get("ASA"))
    assert d > 5.92 + 0.5     # measured thread 5.92 mm


def test_unknown_bolt_size_rejected():
    with pytest.raises(ValueError):
        cm.Params(bolt_screw="M7")
