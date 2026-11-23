"""Go/no-go plug gauge for finding the real size of an opening: a row of thin plugs, each on a
flat handle that is too big to fall through, with its width embossed on the handle.

Print it in 10-15 minutes, try each plug in the hole, and report the largest one that drops in
with a little play. Plugs are square with rounded corners (corner_radius), so they also show
whether the corners are the limit. Handle flat on the bed, plug standing up from it: no overhangs, no supports.
"""
from build123d import (Align, Box, Part, Plane, Pos, RectangleRounded, Text, extrude)
from pydantic import BaseModel, Field, model_validator

from ..materials import Material

BOTTOM = (Align.CENTER, Align.CENTER, Align.MIN)


class Params(BaseModel):
    sizes: list[float] = Field([28.0, 29.5, 31.0, 32.5, 34.0], min_length=1, max_length=6,
                               description="plug widths (and heights), mm")
    corner_radius: float = Field(5.0, ge=0.5, le=12)
    plug_height: float = Field(4.0, ge=2, le=30, description="how far each plug goes into the hole")
    handle: float = Field(42.0, ge=30, le=60, description="square handle size, bigger than any plug")
    handle_thickness: float = Field(1.2, ge=1.2, le=6)
    spacing: float = Field(46.0, ge=35, le=80)

    @model_validator(mode="after")
    def _check(self):
        if max(self.sizes) + 4 > self.handle:
            raise ValueError("handle must be at least 4 mm bigger than the largest plug")
        if self.corner_radius * 2 >= min(self.sizes):
            raise ValueError("corner radius too big for the smallest plug")
        return self


def _label(text: str, size: float, z: float) -> Part:
    t = Text(text, font_size=size, align=(Align.CENTER, Align.CENTER))
    return Pos(0, 0, z) * extrude(t, amount=0.6)


def build(p: Params, material: Material) -> Part:
    out = None
    n = len(p.sizes)
    for i, s in enumerate(p.sizes):
        x = (i - (n - 1) / 2) * p.spacing
        handle = Box(p.handle, p.handle, p.handle_thickness, align=BOTTOM)
        wall = 1.6   # hollow shell so the whole row prints in about 20 minutes
        plug = extrude(RectangleRounded(s, s, p.corner_radius), amount=p.plug_height)
        plug = plug - extrude(RectangleRounded(s - 2 * wall, s - 2 * wall, max(p.corner_radius - wall, 0.5)),
                              amount=p.plug_height)
        # handle flat on the bed, plug standing on it: nothing overhangs, so no supports are needed.
        # The label is raised inside the hollow plug, on the handle.
        plug = Pos(0, 0, p.handle_thickness) * plug
        piece = handle + plug + _label(f"{s:g}", 9, p.handle_thickness)
        piece = Pos(x, 0, 0) * piece
        out = piece if out is None else out + piece
    return out


def describe(p: Params, material: Material) -> dict:
    return {"holes": []}
