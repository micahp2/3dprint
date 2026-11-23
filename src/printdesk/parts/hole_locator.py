"""Measuring ruler: bolts on exactly where the brace does (same 103.24 mm M6 holes) and is no bigger
than the 44 mm strap that already fits. Two bolt ears, a thin bar along the bolt line and a thin
cross arm at the middle, with a millimetre scale, so the real position and size of the hole in the
panel can be read from inside the lid by looking at the four gaps around the cross.

Coordinates: x along the bolt line, y across it, (0, 0) midway between the bolts. Ticks every 5 mm;
the tens are numbered. Print flat, marked side up, no supports.
"""
from build123d import Align, Axis, Box, Part, Pos, Text, extrude, fillet
from pydantic import BaseModel, Field

from .. import fasteners
from ..materials import Material

BOTTOM = (Align.CENTER, Align.CENTER, Align.MIN)


class Params(BaseModel):
    bolt_spacing: float = Field(103.24, ge=30, le=190)
    bolt_screw: str = "M6"
    bar_width: float = Field(8.0, ge=6, le=14)
    arm_length: float = Field(44.0, ge=20, le=44, description="cross arm, no longer than the 44 mm strap that fits")
    thickness: float = Field(2.4, ge=1.6, le=6)
    mark_height: float = Field(0.5, ge=0.3, le=1.0)


def _text(s: str, x: float, y: float, z: float, h: float) -> Part:
    return Pos(x, y, z) * extrude(Text(s, font_size=2.6, align=(Align.CENTER, Align.CENTER)), amount=h)


def build(p: Params, material: Material) -> Part:
    t, mh, bw = p.thickness, p.mark_height, p.bar_width
    plate = Box(p.bolt_spacing, bw, t, align=BOTTOM)
    plate = plate + Box(bw, p.arm_length, t, align=BOTTOM)
    for sx in (-1, 1):
        ear = fillet(Box(18.0, 24.0, t, align=BOTTOM).edges().filter_by(Axis.Z), 4)
        plate = plate + Pos(sx * p.bolt_spacing / 2, 0, 0) * ear
    for sx in (-1, 1):
        plate = plate - Pos(sx * p.bolt_spacing / 2, 0, 0) * fasteners.through_hole(p.bolt_screw, t, material)

    marks = []
    half_x = int(p.bolt_spacing / 2 - 12) // 5 * 5          # stop short of the ears
    for k in range(-half_x, half_x + 1, 5):
        if abs(k) <= bw / 2 and k != 0:
            continue                                         # crowded where the arm crosses
        for s in (-1, 1):
            marks.append(Pos(k, s * 3.0, t) * Box(0.5, 2.0, mh, align=BOTTOM))
        if k % 10 == 0:
            marks.append(_text(f"{k}", k, 0.0, t, mh))
    half_y = int(p.arm_length / 2) // 5 * 5
    for k in range(-half_y, half_y + 1, 5):
        if k == 0:
            continue
        for s in (-1, 1):
            marks.append(Pos(s * 3.0, k, t) * Box(2.0, 0.5, mh, align=BOTTOM))
        if k % 10 == 0:
            marks.append(_text(f"{k}", 0.0, k, t, mh))
    out = plate
    for m in marks:
        out = out + m
    return out


def describe(p: Params, material: Material) -> dict:
    d = fasteners.hole_diameter(p.bolt_screw, material)
    return {"holes": [{"x": sx * p.bolt_spacing / 2, "y": 0.0, "z": p.thickness / 2, "diameter": d,
                       "outer_diameter": d, "outer_z": p.thickness / 2} for sx in (-1, 1)]}
