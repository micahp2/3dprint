"""Tilted-insertion gauge for the camera pod.

The pod is a prism perpendicular to the ring face, but it passes through a hole cut in the flat
inner panel, which is tilted about 28 degrees to the ring face. Seen along the pod's axis, that
hole is shorter in the tilt direction than it is in its own plane (roughly H*cos(tilt) minus the
sheet thickness * sin(tilt)). A plain square plug tested square-on does not show this, so this
gauge uses the real shape: the pod's outer prism, rounded corners, and the chisel-cut back where
the brace plane trims it.

Each piece is a hollow shell with the pod's real outside shape and a different height (the
dimension along the tilt). The number of small holes in its front is its rank: 1 hole = the
first (smallest) height, and so on. Push each in from OUTSIDE with the long side UP; the
largest that goes in and seats is the most the real pod can be.

Printed front-face-down with the open back up: walls are vertical, nothing overhangs, no supports.
Everything is laid out in print orientation.
"""
from build123d import Align, Axis, Box, Cylinder, Part, Pos, Rot, fillet
from pydantic import BaseModel, Field, model_validator

from ..materials import Material
from . import camera_mount as cm

BOTTOM = (Align.CENTER, Align.CENTER, Align.MIN)


class Params(BaseModel):
    heights: list[float] = Field([27.0, 28.0, 29.0, 30.0, 31.0], min_length=1, max_length=6,
                                 description="pod height along the tilt direction, mm")
    width: float = Field(33.4, ge=20, le=40, description="pod width (across the tilt), mm")
    corner_radius: float = Field(5.0, ge=1.0, le=12)
    wall: float = Field(1.6, ge=1.2, le=4)
    spacing: float = Field(40.0, ge=34, le=70)
    # same depth readings and slope as the camera mount
    depth_bottom: float = 12.0
    depth_top: float = 30.0
    opening_h: float = 34.0

    @model_validator(mode="after")
    def _check(self):
        if self.corner_radius - self.wall < 0.5:
            raise ValueError("corner radius must exceed the wall by at least 0.5 mm")
        return self


def build(p: Params, material: Material) -> Part:
    mp = cm.Params(depth_bottom=p.depth_bottom, depth_top=p.depth_top, opening_h=p.opening_h)
    deep = mp.depth_top + 10
    plane_side = cm._in_brace_frame(mp, Box(400, 400, 200, align=BOTTOM))
    n = len(p.heights)
    out = None
    for i, h in enumerate(p.heights):
        outer = fillet(Box(p.width, h, deep, align=BOTTOM).edges().filter_by(Axis.Z), p.corner_radius)
        inner = fillet(Box(p.width - 2 * p.wall, h - 2 * p.wall, deep - p.wall, align=BOTTOM)
                       .edges().filter_by(Axis.Z), p.corner_radius - p.wall)
        # front face is z = 0 in the face frame; the solid runs back to the brace plane
        pod = (Pos(0, 0, -deep) * outer) & plane_side
        pod = pod - Pos(0, 0, -deep) * inner      # inner stops `wall` short of the front: front cap stays
        for k in range(i + 1):                    # rank marker: i+1 small holes in the front cap
            x = (k - i / 2) * 6.0
            pod = pod - Pos(x, 0, -p.wall / 2) * Cylinder(1.5, p.wall + 2, align=(Align.CENTER, Align.CENTER, Align.CENTER))
        flat = Rot(X=180) * pod            # front face on the bed, open sloped back up: no overhangs
        flat = Pos(0, 0, -flat.bounding_box().min.Z) * flat
        piece = Pos((i - (n - 1) / 2) * p.spacing, 0, 0) * flat
        out = piece if out is None else out + piece
    return out


def describe(p: Params, material: Material) -> dict:
    return {"holes": []}
