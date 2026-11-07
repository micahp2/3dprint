"""Part registry. Each part module exposes Params (pydantic model), build(params, material)
and describe(params, material) listing features that validation must find in the geometry."""
from . import camera_mount, mounting_plate

REGISTRY = {
    "mounting_plate": mounting_plate,
    "camera_mount": camera_mount,
}
