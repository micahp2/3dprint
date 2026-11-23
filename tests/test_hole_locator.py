from build123d import Vector

from printdesk.cli import build_part


def test_ruler_bolts_match_the_brace_and_it_stays_inside_the_strap_footprint():
    solid, report, p = build_part("hole_locator", {}, "PLA")
    assert report.ok, report.errors
    t = p.thickness
    for sx in (-1, 1):
        assert not solid.is_inside(Vector(sx * p.bolt_spacing / 2, 0, t / 2))        # bolt hole open
        assert solid.is_inside(Vector(sx * p.bolt_spacing / 2 + 6, 0, t / 2))        # ear beside it
    assert solid.is_inside(Vector(0, 20, t / 2)) and solid.is_inside(Vector(30, 1, t / 2))   # arm and bar
    assert not solid.is_inside(Vector(20, 15, t / 2))       # open quadrant: the hole shows through
    bb = solid.bounding_box()
    assert bb.size.Y <= 44.0 + 1e-6 and bb.size.X <= 121.4 + 1e-6
    assert bb.min.Z == 0 and bb.max.Z <= t + p.mark_height + 1e-6
