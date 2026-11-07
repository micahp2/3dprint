"""Rectangular mounting plate with an arbitrary list of screw holes."""
from typing import Literal

from build123d import Align, Axis, Box, Part, Pos, fillet
from pydantic import BaseModel, Field, model_validator

from .. import fasteners
from ..materials import Material

HoleStyle = Literal["through", "counterbore", "countersink", "insert"]


class Hole(BaseModel):
    x: float = Field(description="mm from plate center")
    y: float = Field(description="mm from plate center")
    screw: str = "M3"
    style: HoleStyle = "through"


class Params(BaseModel):
    width: float = Field(40, ge=10, le=240, description="X size, mm")
    depth: float = Field(30, ge=10, le=240, description="Y size, mm")
    thickness: float = Field(4, ge=2, le=30, description="Z size, mm")
    corner_radius: float = Field(3, ge=0, le=40)
    holes: list[Hole] = Field(default_factory=lambda: [
        Hole(x=-15, y=-10), Hole(x=15, y=-10), Hole(x=-15, y=10), Hole(x=15, y=10)])

    @model_validator(mode="after")
    def _check(self):
        if self.corner_radius * 2 > min(self.width, self.depth):
            raise ValueError("corner_radius too large for plate")
        for h in self.holes:
            fasteners.screw(h.screw)
        return self


def _cutter(h: Hole, thickness: float, material: Material) -> Part:
    if h.style == "through":
        return fasteners.through_hole(h.screw, thickness, material)
    if h.style == "counterbore":
        return fasteners.counterbore(h.screw, thickness, material)
    if h.style == "countersink":
        return fasteners.countersink(h.screw, thickness, material)
    return fasteners.heat_set_pocket(h.screw, thickness, material)


def build(p: Params, material: Material) -> Part:
    plate = Box(p.width, p.depth, p.thickness, align=(Align.CENTER, Align.CENTER, Align.MIN))
    if p.corner_radius > 0:
        plate = fillet(plate.edges().filter_by(Axis.Z), p.corner_radius)
    for h in p.holes:
        plate = plate - Pos(h.x, h.y, 0) * _cutter(h, p.thickness, material)
    return plate


def describe(p: Params, material: Material) -> dict:
    """Features validation must verify in the finished solid."""
    holes = []
    for h in p.holes:
        d = fasteners.hole_diameter(h.screw, material)
        # blind insert pockets are probed near the top face, through holes mid-plate
        z = p.thickness - 0.5 if h.style == "insert" else p.thickness / 2
        holes.append({"x": h.x, "y": h.y, "z": z, "diameter": d,
                      "boss_needed": fasteners.min_boss_diameter(h.screw, material)})
    return {"holes": holes, "extent": (p.width, p.depth, p.thickness)}
