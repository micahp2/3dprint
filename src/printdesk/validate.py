"""Geometry checks run on a finished solid before it may be exported or queued."""
from dataclasses import dataclass, field

from build123d import Part, Vector

from .materials import Material

# Bambu P1S build volume (mm)
BUILD_VOLUME = (256.0, 256.0, 256.0)
TOL = 0.05


@dataclass
class Report:
    errors: list[str] = field(default_factory=list)
    warnings: list[str] = field(default_factory=list)

    @property
    def ok(self) -> bool:
        return not self.errors


def check(part: Part, spec: dict, material: Material) -> Report:
    r = Report()

    if not part.is_valid:
        r.errors.append("solid is not valid")
    if part.volume <= 0:
        r.errors.append("solid has no volume")
        return r

    bb = part.bounding_box()
    size = (bb.size.X, bb.size.Y, bb.size.Z)
    for axis, s, limit in zip("XYZ", size, BUILD_VOLUME):
        if s > limit:
            r.errors.append(f"{axis} size {s:.1f} mm exceeds build volume {limit:.0f} mm")

    ex = spec.get("extent")
    if ex:
        for axis, got, want in zip("XYZ", size, ex):
            if abs(got - want) > TOL:
                r.errors.append(f"{axis} size {got:.2f} mm, expected {want:.2f} mm")

    if material.name == "TPU" and size[2] > 120:
        r.warnings.append("tall TPU part: expect poor results")

    holes = spec.get("holes", [])
    half_x, half_y = size[0] / 2, size[1] / 2
    for i, h in enumerate(holes):
        where = f"hole {i} at ({h['x']}, {h['y']})"
        d, od = h["diameter"], h["outer_diameter"]

        # 1. the bore must really be void, and solid immediately outside the widest feature
        if part.is_inside(Vector(h["x"], h["y"], h["z"])):
            r.errors.append(f"{where} is not void in the model")
            continue
        if od > d + 1e-6 and part.is_inside(Vector(h["x"], h["y"], h["outer_z"])):
            r.errors.append(f"{where}: head recess/countersink is missing from the model")
        # the shaft's own wall: probe outside the bore at the bore's probe height
        for sign in (1, -1):
            edge = Vector(h["x"] + sign * (d / 2 + 0.05), h["y"], h["z"])
            if abs(edge.X) < half_x - 1 and not part.is_inside(edge):
                r.warnings.append(f"{where}: no material beside the bore (overlaps another feature?)")
                break

        # 2. wall to the plate edge, measured from the widest feature
        wall = min(half_x - abs(h["x"]), half_y - abs(h["y"])) - od / 2
        if wall < material.min_wall:
            r.errors.append(
                f"{where} leaves {wall:.2f} mm wall to the edge; "
                f"{material.name} needs >= {material.min_wall} mm")

        # 3. wall between this hole and every later hole
        for j in range(i + 1, len(holes)):
            o = holes[j]
            gap = ((h["x"] - o["x"]) ** 2 + (h["y"] - o["y"]) ** 2) ** 0.5 \
                - od / 2 - o["outer_diameter"] / 2
            if gap < material.min_wall:
                r.errors.append(
                    f"holes {i} and {j} leave {gap:.2f} mm between them; "
                    f"{material.name} needs >= {material.min_wall} mm")
    return r
