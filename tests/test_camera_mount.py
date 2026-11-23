import math

import pytest
from build123d import Vector
from pydantic import ValidationError

from printdesk import fasteners, materials
from printdesk.cli import build_part
from printdesk.parts import camera_mount as cm


@pytest.fixture(scope="module")
def default_build():
    solid, report, p = build_part("camera_mount", {}, "ASA")
    return solid, report, p


def test_defaults_build_and_validate(default_build):
    solid, report, p = default_build
    assert report.ok, report.errors
    assert solid.is_valid and solid.volume > 0


def test_slope_comes_from_the_two_depth_readings():
    p = cm.Params()
    assert p.mid_depth == pytest.approx(21.0)
    assert p.slope_deg == pytest.approx(math.degrees(math.atan(18 / p.depth_span)), abs=1e-6)
    assert 27 < p.slope_deg < 29


def test_brace_back_face_lies_on_the_plane(default_build):
    solid, _, p = default_build
    for y_b in (-12.0, 0.0, 12.0):
        assert solid.is_inside(cm.brace_to_face(p, 15, y_b, +0.2))     # flange just above the plane
        assert not solid.is_inside(cm.brace_to_face(p, 15, y_b, -0.2))  # nothing behind it


def test_plane_depth_is_12_at_the_bottom_and_30_at_the_top(default_build):
    _, _, p = default_build
    bottom_edge_z = cm.brace_to_face(p, 0, -1, 0)  # on the plane, slightly below centre
    # depth along z of the plane at the face-frame heights y = -h/2 and +h/2
    a = math.radians(p.slope_deg)
    z_at = lambda y: -p.mid_depth - y * math.tan(a)
    assert z_at(-p.depth_span / 2) == pytest.approx(-p.depth_bottom, abs=1e-6)
    assert z_at(+p.depth_span / 2) == pytest.approx(-p.depth_top, abs=1e-6)
    # and the construction really puts the plane there
    c = cm.brace_to_face(p, 0, 0, 0)
    assert c.Z == pytest.approx(-21.0, abs=1e-6) and c.Y == pytest.approx(0, abs=1e-6)


def test_pod_front_is_flush_with_the_ring_face(default_build):
    solid, _, p = default_build
    # off the lens window, which flares across the middle of the front
    assert solid.is_inside(Vector(15, -10, -0.2))
    assert not solid.is_inside(Vector(15, -10, +0.2))
    bb = solid.bounding_box()
    assert bb.max.Z == pytest.approx(0, abs=0.01)


def test_pod_fills_the_opening(default_build):
    solid, _, p = default_build
    assert p.pod_w == pytest.approx(p.opening_w - p.opening_gap)
    assert p.pod_h == pytest.approx(p.opening_h - p.opening_gap)
    assert solid.is_inside(Vector(p.pod_w / 2 - 0.3, 0, -5))
    assert not solid.is_inside(Vector(p.pod_w / 2 + 0.3, 0, -5))


def test_bolt_holes_are_perpendicular_to_the_brace_and_clear_an_m6(default_build):
    solid, _, p = default_build
    d = fasteners.hole_diameter("M6", materials.get("ASA"))
    assert d > 5.92 + 0.5
    for sx in (-1, 1):
        x = sx * p.bolt_spacing / 2
        for z_b in (0.3, p.flange_thickness / 2, p.flange_thickness - 0.3):
            assert not solid.is_inside(cm.brace_to_face(p, x, 0, z_b))          # bore is open
        assert solid.is_inside(cm.brace_to_face(p, x + d / 2 + 0.5, 0, 1.0))    # material beside it
        assert solid.is_inside(cm.brace_to_face(p, x, d / 2 + 0.5, 1.0))
    # bolt line is at mid-slope: hole centre sits 21 mm behind the ring face (on the plane)
    c = cm.brace_to_face(p, p.bolt_spacing / 2, 0, 0)
    assert c.Z == pytest.approx(-21.0, abs=1e-6)


def test_bolt_spacing_matches_the_two_caliper_readings():
    p = cm.Params()
    outer, inner = 109.79, 96.69
    assert p.bolt_spacing == pytest.approx((outer + inner) / 2, abs=0.01)
    assert (outer - inner) / 2 == pytest.approx(6.55, abs=0.01)


def test_camera_pocket_is_tilted_open_at_the_back_and_clear_at_the_lens(default_build):
    solid, _, p = default_build
    t = math.radians(p.tilt_deg)
    origin = Vector(0, p.camera_offset_y, -p.recess)
    axis = Vector(0, -math.sin(t), math.cos(t))
    for s in (-0.5, 0.5, 5, 15, 26):     # in front of the lens, then along the camera body (s behind it)
        assert not solid.is_inside(origin - axis * s)
    # the wall in front of the camera, away from the lens window, is present; the face's shallow edge
    # is its top for a down-tilt and its bottom for an up-tilt
    sgn = 1 if p.tilt_deg >= 0 else -1
    yc = sgn * (p.pocket_h / 2 - 0.5)
    corner = Vector(p.pocket_w / 2 - 0.5, p.camera_offset_y + yc * math.cos(t) - 0.4 * math.sin(t),
                    -p.recess + yc * math.sin(t) + 0.4 * math.cos(t))
    assert solid.is_inside(corner)


def test_default_pocket_walls_hold_the_camera_with_the_requested_tilt():
    assert cm.Params(tilt_deg=15).tilt_deg == 15
    assert cm.Params(tilt_deg=0).recess == pytest.approx(cm.Params().front_wall)
    assert cm.Params(tilt_deg=30).recess > cm.Params(tilt_deg=15).recess


def test_default_tilt_keeps_the_original_cameras_view_clear(default_build):
    _, report, p = default_build
    clear = report.info["clear_view_deg"]
    # the camera sits tilted UP against the chute; the 28.6 mm chute trims the OEM 136 x 100 view a little
    assert min(clear["left"], clear["right"]) >= 60
    assert clear["down"] >= p.fov_v / 2 and clear["up"] >= 45


def test_view_clearance_shrinks_with_more_tilt_and_warns():
    _, r0, _ = build_part("camera_mount", {"tilt_deg": 0}, "ASA")
    _, r30, _ = build_part("camera_mount", {"tilt_deg": 30}, "ASA")
    c0, c30 = r0.info["clear_view_deg"], r30.info["clear_view_deg"]
    assert c30["down"] < c0["down"]                      # tilting down uses up the downward view
    assert min(c30["left"], c30["right"]) < min(c0["left"], c0["right"])   # deeper recess narrows it
    assert any("view is clipped" in w for w in r30.warnings)


def test_depth_readings_must_make_the_top_deeper():
    with pytest.raises(ValidationError):
        cm.Params(depth_top=10, depth_bottom=12)


def test_opening_too_small_for_the_camera_is_rejected():
    with pytest.raises(ValidationError):
        cm.Params(opening_w=26)          # leaves under 2 mm wall beside the camera


def test_unknown_bolt_size_rejected():
    with pytest.raises(ValueError):
        cm.Params(bolt_screw="M7")


def test_print_orientation_puts_the_brace_plane_on_the_bed(default_build):
    solid, _, p = default_build
    flat = cm.print_orientation(solid, p)
    bb = flat.bounding_box()
    assert bb.min.Z == pytest.approx(0, abs=1e-6)
    assert flat.volume == pytest.approx(solid.volume, rel=1e-6)
    # the flange's back face is the bed: material just above it, none below, at a point off the pod
    assert flat.is_inside(Vector(40, 0, 0.3))
    assert not flat.is_inside(Vector(40, 0, -0.3))
    # and the pod stands up above it
    assert bb.max.Z > 20


def test_lite_keeps_the_fit_geometry_but_prints_much_less():
    full, _, p = build_part("camera_mount", {}, "PLA")
    lite, rep, pl = build_part("camera_mount", {"lite": True}, "PLA")
    assert rep.ok, rep.errors
    assert lite.volume < 0.75 * full.volume
    # same bolt holes on the same plane, same pod
    for sx in (-1, 1):
        x = sx * pl.bolt_spacing / 2
        assert not lite.is_inside(cm.brace_to_face(pl, x, 0, 1.0))
        assert lite.is_inside(cm.brace_to_face(pl, x + 5, 0, 1.0))
    assert lite.is_inside(Vector(15, -10, -0.2)) and not lite.is_inside(Vector(15, -10, 0.2))
    assert lite.is_inside(Vector(pl.pod_w / 2 - 0.3, 0, -5))
