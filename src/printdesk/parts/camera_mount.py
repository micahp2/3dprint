"""Backup-camera mount for a 2012 Lexus IS 350: a flat bolt-on brace, plus a pod that
bridges the angle between the brace and the trim ring and aims the camera.

Geometry (see docs/camera_mount.md):
  * The brace bolts to a completely flat plane inside the lid. That plane is 12 mm behind the ring
    face at the bottom edge of the opening and 30 mm behind it at the top edge, so the ring face is
    tilted relative to the brace by atan(18 / opening_h), about 27 degrees.
  * The pod is a straight prism, perpendicular to the ring face, filling the opening. Its front is
    flush with the ring face; its rear is cut off by the brace plane.
  * The camera pocket is tilted down by tilt_deg relative to the ring-face normal. It is open at
    the back (the area behind is open), and a flared window clears the wide-angle lens.

Coordinates (face frame F): x right, y up, z out of the car through the opening; the ring face is
z = 0. The brace plane passes through (0, 0, -mid_depth) tilted by the slope angle.

PROVISIONAL / not modelled yet: snap hooks, camera retention (screw or clip), TPU gasket, cable
strain relief, OEM styling, corner radii on the pod. The 15 degree tilt is relative to the ring face
and has not been tested on the car.
"""
import math

from build123d import Align, Axis, Box, Cone, Part, Pos, Rot, Vector, fillet
from pydantic import BaseModel, Field, model_validator

from .. import fasteners
from ..materials import Material

BOTTOM = (Align.CENTER, Align.CENTER, Align.MIN)
TOP = (Align.CENTER, Align.CENTER, Align.MAX)


class Params(BaseModel):
    # camera body: caliper readings 23.54 / 23.37 mm across the body, 26.49 mm front to back
    camera_w: float = Field(23.5, ge=10, le=60, description="camera width, X")
    camera_h: float = Field(23.4, ge=10, le=60, description="camera height, local Y")
    camera_len: float = Field(26.5, ge=10, le=80, description="camera front-to-back")
    lens_ring_d: float = Field(14.0, ge=5, le=40, description="outer diameter of the lens ring, caliper")
    fit_clearance: float = Field(0.4, ge=0.1, le=2.0, description="slack around the camera, total")
    # aim
    tilt_deg: float = Field(-22.0, ge=-45, le=45, description="camera tilt DOWN (positive) or UP (negative), relative to the ring-face normal")
    camera_offset_y: float = Field(2.0, ge=-15, le=15, description="front-face centre height vs opening centre")
    window_half_angle: float = Field(50.0, ge=20, le=75, description="flare of the lens window, degrees")
    fov_h: float = Field(136.0, ge=60, le=190, description="horizontal view to keep clear (OEM figure)")
    fov_v: float = Field(100.0, ge=40, le=160, description="vertical view to keep clear (OEM figure)")
    # mount
    min_wall: float = Field(1.2, ge=1.2, le=6, description="thinnest allowed wall around the camera pocket")
    front_wall: float = Field(1.6, ge=1.2, le=6, description="thinnest material in front of the camera")
    flange_length: float = Field(121.4, ge=50, le=200, description="strap measured 121.36 mm")
    flange_width: float = Field(44.0, ge=20, le=80)
    flange_thickness: float = Field(3.0, ge=2, le=10, description="on the ring side of the brace plane")
    bolt_spacing: float = Field(
        103.24, ge=30, le=190,
        description="centre to centre: (109.79 outer-edge + 96.69 inner-edge hole readings) / 2")
    bolt_screw: str = "M6"   # measured thread 5.92 mm, 20 mm long hex flange bolt
    # the opening in the car's trim ring; the pod fills it, minus a small gap
    # 35.03 x 34.76 was the shelf/outer edge, NOT the hole. Plug gauge (square, R5 corners): 32.5 mm is a
    # little loose, 34 mm is really tight, so the hole is ~34 mm; the pod is 34.0 - 0.6 = 33.4 mm.
    opening_w: float = Field(26.9, ge=15, le=100, description="sleeve + gap: the user's own 28 mm part passed with room to spare, so the sleeve is ~26.3 mm wide")
    opening_h: float = Field(26.8, ge=15, le=100, description="sleeve height + gap; tilted-gauge pods 27-29 mm tall passed")
    depth_span: float | None = Field(34.0, ge=15, le=100,
                                     description="distance over which the 12/30 mm depth readings were taken; defaults to opening_h")
    opening_gap: float = Field(0.6, ge=0.2, le=3.0, description="total slack between pod and opening")
    lite: bool = Field(False, description="fit-test version: bolt ears and a bar instead of the full brace plate")
    shelf_plate_w: float = Field(33.4, ge=0, le=60, description="front plate that sits in the 34 mm shelf recess and stops the pod; 0 = none")
    shelf_plate_h: float = Field(33.4, ge=0, le=60)
    shelf_plate_t: float = Field(3.0, ge=0, le=10)
    view_w: float = Field(34.0, ge=15, le=100, description="the outer opening the lens looks out through")
    view_h: float = Field(34.0, ge=15, le=100)
    pod_only: bool = Field(False, description="diagnostic: the pod with its pocket and no brace plate")
    pod_corner_radius: float = Field(5.0, ge=0.5, le=12, description="rounded corners of the pod (gauge used R5)")
    # the flat brace plane, measured with the depth rod from the ring face
    depth_bottom: float = Field(12.0, ge=1, le=80, description="ring face to brace plane at the bottom edge")
    depth_top: float = Field(30.0, ge=1, le=80, description="ring face to brace plane at the top edge")

    # --- derived geometry ---
    @property
    def pod_w(self) -> float:
        return self.opening_w - self.opening_gap

    @property
    def pod_h(self) -> float:
        return self.opening_h - self.opening_gap

    @property
    def slope_deg(self) -> float:
        """Angle between the ring face and the flat brace plane."""
        return math.degrees(math.atan((self.depth_top - self.depth_bottom) / (self.depth_span or self.opening_h)))

    @property
    def mid_depth(self) -> float:
        return (self.depth_top + self.depth_bottom) / 2

    @property
    def pocket_w(self) -> float:
        return self.camera_w + self.fit_clearance

    @property
    def pocket_h(self) -> float:
        return self.camera_h + self.fit_clearance

    @property
    def recess(self) -> float:
        """Depth of the camera's front-face centre behind the ring face: the top edge of the
        tilted face still sits front_wall behind the ring face."""
        return self.pocket_h / 2 * abs(math.sin(math.radians(self.tilt_deg))) + self.front_wall

    @model_validator(mode="after")
    def _check(self):
        fasteners.screw(self.bolt_screw)
        if self.depth_top <= self.depth_bottom:
            raise ValueError("depth_top must be greater than depth_bottom (top of the opening is deeper)")
        side_w = (self.pod_w - self.pocket_w) / 2
        if side_w < self.min_wall - 1e-6:
            raise ValueError(
                f"opening {self.opening_w} mm wide leaves only {side_w:.2f} mm wall beside the camera; "
                f"need >= {self.min_wall} mm")
        end_margin = (self.flange_length - self.bolt_spacing) / 2   # hole centre to flange end
        clearance = fasteners.screw(self.bolt_screw).clearance
        if end_margin - clearance / 2 < 3.0:
            raise ValueError(
                f"bolt holes leave only {end_margin - clearance / 2:.1f} mm of material to the flange ends; need >= 3 mm")
        if self.flange_width < self.pod_h + 6:
            raise ValueError("flange too narrow to carry the pod")
        if self.lens_ring_d + 1.0 > min(self.camera_w, self.camera_h):
            raise ValueError("lens ring larger than the camera face")
        # the lowest flange corner must stay well behind the ring face
        a = math.radians(self.slope_deg)
        z_low = -self.mid_depth + (self.flange_width / 2) * math.sin(a) + self.flange_thickness * math.cos(a)
        if z_low > -2.0:
            raise ValueError(
                f"the bottom edge of the flange would reach {z_low:.1f} mm from the ring face; "
                f"it must stay at least 2 mm behind it")
        return self


# ---------------------------------------------------------------------------- geometry helpers
def brace_to_face(p: Params, x: float, y_b: float, z_b: float) -> Vector:
    """Brace-frame point (z_b measured from the plane toward the ring) -> face-frame point."""
    a = math.radians(p.slope_deg)
    return Vector(x, y_b * math.cos(a) + z_b * math.sin(a),
                  -p.mid_depth - y_b * math.sin(a) + z_b * math.cos(a))


def _in_brace_frame(p: Params, shape):
    return Pos(0, 0, -p.mid_depth) * Rot(X=-p.slope_deg) * shape


def _in_camera_frame(p: Params, shape):
    return Pos(0, p.camera_offset_y, -p.recess) * Rot(X=p.tilt_deg) * shape


def build(p: Params, material: Material) -> Part:
    # pod: prism perpendicular to the ring face, trimmed by the brace plane
    deep = p.depth_top + 10
    pod = Box(p.pod_w, p.pod_h, deep, align=BOTTOM)
    pod = Pos(0, 0, -deep) * fillet(pod.edges().filter_by(Axis.Z), p.pod_corner_radius)
    ring_side_of_plane = _in_brace_frame(p, Box(400, 400, 200, align=BOTTOM))
    pod = pod & ring_side_of_plane

    # brace: flat plate whose back face lies on the plane
    if p.lite:
        # same plane, hole positions and thickness; just ears around the bolts joined by a bar
        flange = Box(p.bolt_spacing, 14.0, p.flange_thickness, align=BOTTOM)
        for sx in (-1, 1):
            ear = Box(18.0, 24.0, p.flange_thickness, align=BOTTOM)
            ear = fillet(ear.edges().filter_by(Axis.Z), 4)
            flange = flange + Pos(sx * p.bolt_spacing / 2, 0, 0) * ear
    else:
        flange = Box(p.flange_length, p.flange_width, p.flange_thickness, align=BOTTOM)
        flange = fillet(flange.edges().filter_by(Axis.Z), 4)
    for sx in (-1, 1):
        flange = flange - Pos(sx * p.bolt_spacing / 2, 0, 0) * fasteners.through_hole(
            p.bolt_screw, p.flange_thickness, material)
    body = pod if p.pod_only else pod + _in_brace_frame(p, flange)

    if p.shelf_plate_t > 0:
        plate = fillet(Box(p.shelf_plate_w, p.shelf_plate_h, p.shelf_plate_t, align=BOTTOM).edges().filter_by(Axis.Z),
                       p.pod_corner_radius)
        body = body + Pos(0, 0, -p.shelf_plate_t) * plate

    # camera pocket: tilted, open at the back
    pocket = _in_camera_frame(p, Pos(0, 0, 0) * Box(p.pocket_w, p.pocket_h, p.camera_len + 80, align=TOP))
    body = body - pocket

    # flared lens window through the material in front of the camera
    r0 = (p.lens_ring_d + 1.0) / 2
    reach = p.recess + p.pocket_h / 2 + 4
    r1 = r0 + reach * math.tan(math.radians(p.window_half_angle))
    window = _in_camera_frame(p, Pos(0, 0, -0.3) * Cone(r0, r1, reach + 0.3, align=BOTTOM))
    body = body - window
    return body


def describe(p: Params, material: Material) -> dict:
    d = fasteners.hole_diameter(p.bolt_screw, material)
    holes = []
    if p.pod_only:
        return {"holes": holes}
    for sx in (-1, 1):
        c = brace_to_face(p, sx * p.bolt_spacing / 2, 0.0, p.flange_thickness / 2)
        holes.append({"x": c.X, "y": c.Y, "z": c.Z, "diameter": d, "outer_diameter": d,
                      "outer_z": c.Z})
    return {"holes": holes}


def print_orientation(solid: Part, p: "Params | None" = None) -> Part:
    """Brace plane (the back of the flange) flat on the bed, pod standing up from it. The pocket
    is open at the back, so it opens onto the bed; almost nothing overhangs and no supports are
    needed except possibly a bridged roof over the pocket. The pod's front face is a sloped top."""
    p = p or Params()
    flat = Rot(X=p.slope_deg) * Pos(0, 0, p.mid_depth) * solid
    return Pos(0, 0, -flat.bounding_box().min.Z) * flat


# ---------------------------------------------------------------------------- extra checks
def _ray_dir(p: Params, az_deg: float, el_deg: float) -> Vector:
    """Direction for a view angle (az right, el up) about the camera axis, in the face frame."""
    az, el, t = map(math.radians, (az_deg, el_deg, p.tilt_deg))
    x, y, z = math.sin(az) * math.cos(el), math.sin(el), math.cos(az) * math.cos(el)
    return Vector(x, y * math.cos(t) - z * math.sin(t), y * math.sin(t) + z * math.cos(t))


def _ray_clear(solid: Part, p: Params, az: float, el: float, step: float = 1.0) -> bool:
    origin = Vector(0, p.camera_offset_y, -p.recess)
    d = _ray_dir(p, az, el)
    if d.Z <= 1e-6:
        return False
    t_exit = -origin.Z / d.Z                     # where the ray crosses the ring face
    exit_x, exit_y = origin.X + d.X * t_exit, origin.Y + d.Y * t_exit
    if abs(exit_x) > p.view_w / 2 or abs(exit_y) > p.view_h / 2:
        return False                             # would hit the lid around the opening
    n = int(t_exit / step)
    for i in range(1, n + 1):
        q = origin + d * (i * step)
        if solid.is_inside(q):
            return False
    return True


def clear_half_angle(solid: Part, p: Params, direction: str) -> float:
    """Largest view angle (degrees, from the camera axis) that is clear in a direction."""
    az_el = {"right": lambda a: (a, 0), "left": lambda a: (-a, 0),
             "up": lambda a: (0, a), "down": lambda a: (0, -a)}[direction]
    clear = 0.0
    for a in range(0, 86, 3):
        if _ray_clear(solid, p, *az_el(float(a))):
            clear = float(a)
        else:
            break
    return clear


def extra_checks(solid: Part, p: Params, material: Material, report) -> None:
    want_h, want_v = p.fov_h / 2, p.fov_v / 2
    got = {d: clear_half_angle(solid, p, d) for d in ("left", "right", "up", "down")}
    report.info = {"clear_view_deg": got, "slope_deg": round(p.slope_deg, 1),
                   "recess_mm": round(p.recess, 2)}
    short = []
    if min(got["left"], got["right"]) < want_h:
        short.append(f"horizontal ±{min(got['left'], got['right']):.0f}° clear (want ±{want_h:.0f}°)")
    if got["up"] < want_v or got["down"] < want_v:
        short.append(f"vertical {got['down']:.0f}° down / {got['up']:.0f}° up clear (want {want_v:.0f}°)")
    if short:
        report.warnings.append("view is clipped by the opening: " + "; ".join(short))
