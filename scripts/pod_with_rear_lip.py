"""The owner's printed pod (28 x 28 x 32 mm, data/original_pod_28x28x32.stl) with a lip on its REAR end, inside the
trunk lid, so it is fed in from inside lens-end first and stops against the panel.

Pod frame (as printed): lens plate at z=+16 (round bore), rear plate at z=-16 with a narrow cable slit, open on the
-y side. Panel frame (built here): z=0 is the face of the panel the lip bears on, +z is into the trunk, the pod
sticks out into -z. The pod's axis is tilted `tilt` degrees to the panel normal (18 in the owner's mount3
assembly), so the lip seats flat while the pod hangs at that angle. The prism between the rear plate and the lip
is filled in (a stub of the pod's outline) and a wide cable channel runs through it and the lip, open at the bottom.

    uv run --with manifold3d --with networkx --with shapely python scripts/pod_with_rear_lip.py --out out/pod_rear_lip
"""
import argparse
import tempfile
from pathlib import Path

import numpy as np
import trimesh
from build123d import Align, Axis, Box, Pos, export_stl, fillet
from trimesh.transformations import rotation_matrix as rot

POD = Path(__file__).resolve().parents[1] / "src/printdesk/parts/data/original_pod_28x28x32.stl"


def to_mesh(shape):
    with tempfile.TemporaryDirectory() as d:
        f = Path(d) / "s.stl"
        export_stl(shape, str(f))
        return trimesh.load(str(f))


def box(x0, x1, y0, y1, z0, z1):
    m = trimesh.creation.box(extents=[x1 - x0, y1 - y0, z1 - z0])
    m.apply_translation([(x0 + x1) / 2, (y0 + y1) / 2, (z0 + z1) / 2])
    return m


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", required=True)
    ap.add_argument("--lip", type=float, default=34.0, help="square lip, mm")
    ap.add_argument("--lip-t", type=float, default=2.5)
    ap.add_argument("--tilt", type=float, default=18.0, help="pod axis vs panel normal, degrees (owner's mount3)")
    ap.add_argument("--slot", type=float, default=10.0, help="cable slot width, mm (original slit was ~2)")
    a = ap.parse_args()

    boolean = lambda op, ms: getattr(trimesh.boolean, op)(ms, engine="manifold")
    pod = trimesh.load(str(POD))
    # widen the cable slit in the rear plate (z -16 .. -14.7): original ~2 mm wide, 14 mm long up from the open side
    pod = boolean("difference", [pod, box(-a.slot / 2, a.slot / 2, -15, 1.0, -16.5, -14.3)])

    # stub: the pod's 28 x 28 outline extended rearward from the rear plate (overlapping it by 1.3 mm)
    stub = box(-14, 14, -14, 14, -16 - 30, -16 + 1.3)

    # channel for the cable, through the stub and (later) the lip, open towards -y
    channel = None   # made in the panel frame below: a straight slot open to the lip's -y edge

    # pod frame -> panel frame: lens end towards -z, axis tilted so its rear end is higher (+y) than the lens end
    T = rot(np.radians(-a.tilt), [1, 0, 0]) @ rot(np.pi, [0, 1, 0])
    # then move the pod's rear-plate centre to the origin, so the pod's axis crosses the lip's front face there
    rear = (T @ np.array([0, 0, -16, 1.0]))[:3]
    for m in (pod, stub):
        m.apply_transform(T)
        m.apply_translation(-rear)

    t = a.lip_t
    lip = to_mesh(Pos(0, 0, 0) * fillet(Box(a.lip, a.lip, t, align=(Align.CENTER, Align.CENTER, Align.MIN))
                                         .edges().filter_by(Axis.Z), 5.0))
    channel = box(-a.slot / 2, a.slot / 2, -60, 1.0, -14, t + 6)     # straight through wedge and lip, open at -y
    half_space = box(-60, 60, -60, 60, -80, t)          # keep everything in front of the lip's back face
    stub = boolean("intersection", [stub, half_space])
    for n, m in (('pod', pod), ('stub', stub), ('lip', lip)):
        print(n, 'volume', m.is_volume, 'vol', round(m.volume, 1), 'ext', m.extents.round(1))
    body = boolean("union", [pod, stub, lip])
    body = boolean("difference", [body, channel])
    # the pod's tilted rear corner pokes out behind the lip's back face: trim it flat so the lip's back is the flat face
    body = boolean("intersection", [body, half_space])

    # print: lip's back face on the bed, pod standing up
    body.apply_transform(rot(np.pi, [0, 1, 0]))
    body.apply_translation([0, 0, -body.bounds[0][2]])
    out = Path(a.out)
    out.parent.mkdir(parents=True, exist_ok=True)
    body.export(str(out.with_suffix(".stl")))
    print("ok extents", body.extents.round(1), "watertight", body.is_watertight, "vol %.1f cm3" % (body.volume / 1000),
          "bodies", len(body.split(only_watertight=False)))


if __name__ == "__main__":
    main()
