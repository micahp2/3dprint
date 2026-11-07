import pytest
from build123d import Vector
from pydantic import ValidationError

from printdesk.cli import build_part
from printdesk.parts import camera_mount as cm


def test_defaults_build_and_validate():
    solid, report, p = build_part("camera_mount", {}, "ASA")
    assert report.ok, report.errors
    bb = solid.bounding_box()
    assert bb.size.X == pytest.approx(122, abs=0.01)
    assert bb.size.Z == pytest.approx(3 + 14, abs=0.01)


def test_camera_pocket_is_void_and_lens_window_is_open():
    solid, _, p = build_part("camera_mount", {}, "ASA")
    total = p.flange_thickness + p.pod_height
    assert not solid.is_inside(Vector(0, 0, total / 2))          # inside the pocket
    assert not solid.is_inside(Vector(0, 0, total - 0.8))        # through the lens window
    assert solid.is_inside(Vector(p.pod_w / 2 - 0.5, 0, total / 2))  # pod wall present
    assert solid.is_inside(Vector(0, p.pod_d / 2 - 0.5, total / 2))


def test_pod_must_fit_the_opening():
    with pytest.raises(ValidationError):
        cm.Params(opening_w=28)          # pod is ~30 mm wide


def test_bigger_camera_grows_the_pod():
    p1, p2 = cm.Params(), cm.Params(camera_w=23.0)
    assert p2.pod_w == pytest.approx(p1.pod_w - 2.5)


def test_bolt_spacing_drives_hole_positions():
    solid, report, p = build_part("camera_mount", {"bolt_spacing": 90}, "ASA")
    assert report.ok, report.errors
    assert not solid.is_inside(Vector(45, 0, 1.5))
    assert solid.is_inside(Vector(96 / 2, 0, 1.5))   # old position is now solid


def test_unknown_bolt_size_rejected():
    with pytest.raises(ValueError):
        cm.Params(bolt_screw="M7")
