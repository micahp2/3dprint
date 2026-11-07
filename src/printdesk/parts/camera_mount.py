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
    # camera body (measure with calipers)
    camera_w: float = Field(25.5, ge=10, le=60, description="camera width, X")
    camera_h: float = Field(25.5, ge=10, le=60, description="camera height, Y")
    camera_len: float = Field(28.0, ge=10, le=80, description="camera front-to-back, Z")
    lens_ring_d: float = Field(19.0, ge=5, le=40, description="outer diameter of the lens ring")
    fit_clearance: float = Field(0.4, ge=0.1, le=2.0, description="slack around the camera, total")
    # mount
    wall: float = Field(2.0, ge=1.2, le=6)
    front_wall: float = Field(1.6, ge=1.2, le=6)
    pod_height: float = Field(14.0, ge=6, le=40, description="pod height above the flange")
    flange_length: float = Field(122.0, ge=50, le=200)
    flange_width: float = Field(40.0, ge=20, le=80)
    flange_thickness: float = Field(3.0, ge=2, le=10)
    bolt_spacing: float = Field(96.0, ge=30, le=190, description="centre to centre")
    bolt_screw: str = "M5"
    # the opening in the car's trim ring (inner size) and how loose the pod may sit in it
    opening_w: float = Field(35.0, ge=15, le=100)
    opening_h: float = Field(31.0, ge=15, le=100)
    opening_gap: float = Field(0.6, ge=0.2, le=3.0)

    @property
    def pod_w(self) -> float:
        return self.camera_w + self.fit_clearance + 2 * self.wall

    @property
    def pod_d(self) -> float:
        return self.camera_h + self.fit_clearance + 2 * self.wall

    @model_validator(mode="after")
    def _check(self):
        fasteners.screw(self.bolt_screw)
        if self.pod_w > self.opening_w - self.opening_gap:
            raise ValueError(
                f"pod width {self.pod_w:.1f} mm does not fit opening {self.opening_w} mm "
                f"with a {self.opening_gap} mm gap; reduce wall/clearance or remeasure")
        if self.pod_d > self.opening_h - self.opening_gap:
            raise ValueError(
                f"pod height {self.pod_d:.1f} mm does not fit opening {self.opening_h} mm "
                f"with a {self.opening_gap} mm gap; reduce wall/clearance or remeasure")
        if self.flange_length - self.bolt_spacing < 2 * (fasteners.screw(self.bolt_screw).clearance + 4):
            raise ValueError("bolt holes too close to the flange ends")
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
