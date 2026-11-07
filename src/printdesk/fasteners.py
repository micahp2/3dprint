"""Metric fastener geometry tables (mm) and cutter builders for build123d."""
from dataclasses import dataclass

from build123d import Align, Cone, Cylinder, Part, Pos

from .materials import Material

BOTTOM = (Align.CENTER, Align.CENTER, Align.MIN)


@dataclass(frozen=True)
class Screw:
    d: float            # nominal thread diameter
    clearance: float    # normal-fit through-hole diameter
    head_d: float       # socket/pan head diameter
    head_h: float       # head height
    csk_d: float        # countersink diameter at surface (90 deg flat head)
    nut_af: float       # nut across-flats
    nut_h: float        # nut thickness
    insert_d: float     # heat-set insert hole diameter
    insert_len: float   # heat-set insert hole depth


SCREWS: dict[str, Screw] = {
    "M2":   Screw(2.0, 2.4, 3.8, 2.0, 4.0, 4.0, 1.6, 3.2, 4.0),
    "M2.5": Screw(2.5, 2.9, 4.5, 2.5, 5.0, 5.0, 2.0, 3.6, 5.0),
    "M3":   Screw(3.0, 3.4, 5.5, 3.0, 6.0, 5.5, 2.4, 4.0, 5.7),
    "M4":   Screw(4.0, 4.5, 7.0, 4.0, 8.0, 7.0, 3.2, 5.6, 8.1),
    "M5":   Screw(5.0, 5.5, 8.5, 5.0, 10.0, 8.0, 4.0, 6.4, 9.5),
    "M6":   Screw(6.0, 6.6, 10.0, 6.0, 12.0, 10.0, 5.0, 8.0, 12.7),
    "M8":   Screw(8.0, 9.0, 13.0, 8.0, 16.0, 13.0, 6.5, 10.0, 15.0),
}


def screw(size: str) -> Screw:
    try:
        return SCREWS[size]
    except KeyError:
        raise ValueError(f"unknown screw {size!r}; known: {list(SCREWS)}")


def hole_diameter(size: str, material: Material) -> float:
    return screw(size).clearance + material.hole_comp


def through_hole(size: str, depth: float, material: Material) -> Part:
    """Cylinder from z=0 up to z=depth (plain clearance hole)."""
    d = hole_diameter(size, material)
    return Cylinder(d / 2, depth, align=BOTTOM)


def counterbore(size: str, depth: float, material: Material, head_depth: float | None = None) -> Part:
    """Clearance hole plus a socket-head counterbore opening at z=depth (top face)."""
    s = screw(size)
    hd = head_depth if head_depth is not None else s.head_h + 0.3
    head_r = (s.head_d + material.hole_comp + 0.3) / 2
    shaft = through_hole(size, depth, material)
    head = Pos(0, 0, depth - hd) * Cylinder(head_r, hd + 0.5, align=BOTTOM)
    return shaft + head


def countersink(size: str, depth: float, material: Material) -> Part:
    """Clearance hole plus a 90-degree countersink at the top face (z=depth)."""
    s = screw(size)
    shaft = through_hole(size, depth, material)
    top_r = (s.csk_d + material.hole_comp) / 2
    r0 = hole_diameter(size, material) / 2
    h = top_r - r0  # 45 degree flank
    cone = Pos(0, 0, depth - h) * Cone(r0, top_r, h, align=BOTTOM)
    cap = Pos(0, 0, depth) * Cylinder(top_r, 0.5, align=BOTTOM)  # clean cut above surface
    return shaft + cone + cap


def heat_set_pocket(size: str, depth: float, material: Material) -> Part:
    """Blind pocket for a heat-set insert, opening at z=depth, going down insert_len."""
    s = screw(size)
    d = s.insert_d + material.hole_comp * 0.5
    return Pos(0, 0, depth - s.insert_len) * Cylinder(d / 2, s.insert_len + 0.5, align=BOTTOM)


def min_boss_diameter(size: str, material: Material) -> float:
    """Smallest outside diameter keeping min_wall around the clearance hole."""
    return hole_diameter(size, material) + 2 * material.min_wall
