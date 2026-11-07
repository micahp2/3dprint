"""Material properties that affect CAD. Values are starting guesses for a P1S;
overwrite them with measured numbers from the calibration print (see docs)."""
from dataclasses import dataclass


@dataclass(frozen=True)
class Material:
    name: str
    hole_comp: float      # mm added to hole diameters (printed holes come out small)
    min_wall: float       # mm, absolute floor for structural walls
    ams_ok: bool          # can be fed through the AMS
    enclosed: bool        # needs the chamber closed
    notes: str = ""


MATERIALS: dict[str, Material] = {
    "PLA": Material("PLA", 0.20, 1.2, True, False),
    "PETG-CF": Material("PETG-CF", 0.25, 1.6, True, False, "abrasive; hardened nozzle"),
    "ABS": Material("ABS", 0.25, 1.6, True, True, "shrinks; keep parts small/low warp"),
    "ASA": Material("ASA", 0.25, 1.6, True, True),
    "TPU": Material("TPU", 0.10, 1.2, False, False, "external spool only; slow"),
}


def get(name: str) -> Material:
    try:
        return MATERIALS[name]
    except KeyError:
        raise ValueError(f"unknown material {name!r}; known: {sorted(MATERIALS)}")
