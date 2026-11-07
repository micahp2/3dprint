"""Backup-camera mount: a bolt-on flange with a pod that seats in the trim-ring opening.

PROVISIONAL: every default below is an estimate read off photos (see docs/camera_mount.md).
Replace them with caliper measurements before printing anything in ASA.

Coordinates: flange in XY, centred; z=0 is the back face (against the inside of the lid),
the pod rises toward +Z through the opening, the lens looks along +Z.
Not yet modelled: snap hooks, camera retention screw/clip, TPU gasket, tilt, cable strain relief.
"""
from build123d import Align, Axis, Box, Cylinder, Part, Pos, fillet
from pydantic import BaseModel, Field, model_validator

from .. import fasteners
from ..materials import Material

BOTTOM = (Align.CENTER, Align.CENTER, Align.MIN)


class Params(BaseModel):
    # camera body: caliper readings 23.54 / 23.37 mm across the body, 26.49 mm front to back
    camera_w: float = Field(23.5, ge=10, le=60, description="camera width, X")
    camera_h: float = Field(23.4, ge=10, le=60, description="camera height, Y")
    camera_len: float = Field(26.5, ge=10, le=80, description="camera front-to-back, Z")
    lens_ring_d: float = Field(14.0, ge=5, le=40, description="outer diameter of the lens ring (estimated)")
    fit_clearance: float = Field(0.4, ge=0.1, le=2.0, description="slack around the camera, total")
    # mount
    min_wall: float = Field(2.0, ge=1.2, le=6, description="thinnest allowed wall around the camera pocket")
    front_wall: float = Field(1.6, ge=1.2, le=6)
    pod_height: float = Field(14.0, ge=6, le=40, description="pod height above the flange")
    flange_length: float = Field(121.4, ge=50, le=200, description="strap measured 121.36 mm")
    flange_width: float = Field(44.0, ge=20, le=80)
    flange_thickness: float = Field(3.0, ge=2, le=10)
    bolt_spacing: float = Field(
        103.24, ge=30, le=190,
        description="centre to centre: (109.79 outer-edge + 96.69 inner-edge hole readings) / 2")
    bolt_screw: str = "M6"   # measured thread 5.92 mm, 20 mm long hex flange bolt
    # the opening in the car's trim ring; the pod is sized to fill it, minus a small gap
    opening_w: float = Field(35.03, ge=15, le=100, description="trim opening width, caliper")
    opening_h: float = Field(34.76, ge=15, le=100, description="trim opening other dimension, caliper")
    opening_gap: float = Field(0.6, ge=0.2, le=3.0, description="total slack between pod and opening")

    @property
    def pod_w(self) -> float:
        return self.opening_w - self.opening_gap

    @property
    def pod_d(self) -> float:
        return self.opening_h - self.opening_gap

    @model_validator(mode="after")
    def _check(self):
        fasteners.screw(self.bolt_screw)
        side_w = (self.pod_w - (self.camera_w + self.fit_clearance)) / 2
        side_d = (self.pod_d - (self.camera_h + self.fit_clearance)) / 2
        if min(side_w, side_d) < self.min_wall:
            raise ValueError(
                f"opening {self.opening_w} x {self.opening_h} mm leaves only "
                f"{min(side_w, side_d):.2f} mm wall around the camera; need >= {self.min_wall} mm")
        end_margin = (self.flange_length - self.bolt_spacing) / 2   # centre of hole to flange end
        if end_margin - fasteners.screw(self.bolt_screw).clearance / 2 < 3.0:
            raise ValueError(
                f"bolt holes leave only {end_margin - fasteners.screw(self.bolt_screw).clearance / 2:.1f} mm "
                f"of material to the flange ends; need >= 3 mm")
        if self.flange_width < self.pod_d + 6:
            raise ValueError("flange too narrow to carry the pod")
        if self.lens_ring_d + 1.0 > min(self.camera_w, self.camera_h):
            raise ValueError("lens ring larger than the camera face")
        return self


def build(p: Params, material: Material) -> Part:
    total_h = p.flange_thickness + p.pod_height
    flange = Box(p.flange_length, p.flange_width, p.flange_thickness, align=BOTTOM)
    flange = fillet(flange.edges().filter_by(Axis.Z), 4)
    pod = Box(p.pod_w, p.pod_d, total_h, align=BOTTOM)
    body = flange + pod

    # camera pocket: open at the back (z=0), closed by the front wall
    pocket_w = p.camera_w + p.fit_clearance
    pocket_h = p.camera_h + p.fit_clearance
    pocket = Box(pocket_w, pocket_h, total_h - p.front_wall, align=BOTTOM)
    body = body - pocket

    # lens window through the front wall
    window = Pos(0, 0, total_h - p.front_wall - 0.1) * Cylinder(
        (p.lens_ring_d + 1.0) / 2, p.front_wall + 0.2, align=BOTTOM)
    body = body - window

    # bolt holes
    for sx in (-1, 1):
        body = body - Pos(sx * p.bolt_spacing / 2, 0, 0) * fasteners.through_hole(
            p.bolt_screw, p.flange_thickness, material)
    return body


def describe(p: Params, material: Material) -> dict:
    holes = []
    d = fasteners.hole_diameter(p.bolt_screw, material)
    for sx in (-1, 1):
        holes.append({"x": sx * p.bolt_spacing / 2, "y": 0.0, "z": p.flange_thickness / 2,
                      "diameter": d, "outer_diameter": d, "outer_z": p.flange_thickness / 2})
    return {"holes": holes,
            "extent": (p.flange_length, p.flange_width, p.flange_thickness + p.pod_height)}
