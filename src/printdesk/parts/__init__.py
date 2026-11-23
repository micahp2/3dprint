"""Part registry. Each part module exposes Params (pydantic model), build(params, material)
and describe(params, material) listing features that validation must find in the geometry."""
from . import camera_mount, hole_locator, mounting_plate, opening_gauge, tilted_gauge

REGISTRY = {
    "mounting_plate": mounting_plate,
    "camera_mount": camera_mount,
    "opening_gauge": opening_gauge,
    "tilted_gauge": tilted_gauge,
    "hole_locator": hole_locator,
}
