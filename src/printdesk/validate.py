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

    # every specified hole must really be void at its position, and solid just outside it
    for i, h in enumerate(spec.get("holes", [])):
        d = h["diameter"]
        centre = Vector(h["x"], h["y"], h["z"])
        if part.is_inside(centre):
            r.errors.append(f"hole {i} at ({h['x']}, {h['y']}) is not void in the model")
            continue
        # wall check: probe outward from the hole edge along +x and -x
        for sign in (1, -1):
            edge = Vector(h["x"] + sign * (d / 2 + 0.05), h["y"], h["z"])
            if not part.is_inside(edge) and abs(edge.X) < size[0] / 2 - 1:
                r.warnings.append(
                    f"hole {i} at ({h['x']}, {h['y']}): no material right beside the hole "
                    f"(overlaps another feature?)")
                break
        # wall thickness to the nearest outer edge in X and Y
        half_x, half_y = size[0] / 2, size[1] / 2
        wall = min(half_x - abs(h["x"]), half_y - abs(h["y"])) - d / 2
        if wall < material.min_wall:
            r.errors.append(
                f"hole {i} at ({h['x']}, {h['y']}) leaves {wall:.2f} mm wall to the edge; "
                f"{material.name} needs >= {material.min_wall} mm")
    return r
