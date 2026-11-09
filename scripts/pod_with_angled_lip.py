"""The owner's printed pod (28 x 28 x 32 mm, data/original_pod_28x28x32.stl) with a flange that lies in the panel plane.

Pod frame (as printed, unchanged): lens plate at z=+16 (round bore), rear plate at z=-16 with a cable slit, open on
the -y side ("top"). The panel plane cuts through the pod at `tilt` degrees to the pod's cross-section: it starts
near the lens end on the open top side (`inset` mm behind the lens face) and angles back towards the rear plate on
the closed side. The flange is a slab 2.5 mm thick behind that plane, a ring around the pod's outline, so the pod
fed in from inside stops with the flange against the panel and the lens end sticking through the hole. The pod
interior and the rear stay as they were; the rear plate slit is widened for the cable plugs.

Printed with the open side up (closed wall on the bed), so the flange is a fin leaning 18 degrees off vertical:
no supports. `--bottom-ext` > 0 adds flange below the closed wall (needs supports under the pod floor).

    uv run --with manifold3d --with networkx --with shapely python scripts/pod_with_angled_lip.py --out out/pod_angled_lip
"""
import argparse
from pathlib import Path

import numpy as np
import trimesh
from trimesh.transformations import rotation_matrix as rot

POD = Path(__file__).resolve().parents[1] / "src/printdesk/parts/data/original_pod_28x28x32.stl"


def box(x0, x1, y0, y1, z0, z1):
    m = trimesh.creation.box(extents=[x1 - x0, y1 - y0, z1 - z0])
    m.apply_translation([(x0 + x1) / 2, (y0 + y1) / 2, (z0 + z1) / 2])
    return m


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", required=True)
    ap.add_argument("--lip-w", type=float, default=33.0, help="flange width across the pod (x), mm")
    ap.add_argument("--lip-t", type=float, default=2.0)
    ap.add_argument("--top-ext", type=float, default=2.5, help="flange beyond the open top edge, mm")
    ap.add_argument("--bottom-ext", type=float, default=0.0, help="flange beyond the closed wall, mm (needs supports)")
    ap.add_argument("--tilt", type=float, default=48.0, help="panel plane vs pod cross-section, degrees")
    ap.add_argument("--inset", type=float, default=2.0, help="where the plane meets the open top edge, mm behind the lens face")
    ap.add_argument("--slot", type=float, default=10.0, help="rear plate cable slot width, mm (original slit ~2)")
    ap.add_argument("--cam-x", type=float, default=24.2, help="inside width between the side walls, mm (camera 23.5)")
    ap.add_argument("--cam-z", type=float, default=27.2, help="inside length between the end plates, mm (camera 26.5)")
    a = ap.parse_args()

    boolean = lambda op, ms: getattr(trimesh.boolean, op)(ms, engine="manifold")
    pod = trimesh.load(str(POD))
    pod = boolean("difference", [pod, box(-a.slot / 2, a.slot / 2, -15, 1.0, -16.5, -14.3)])

    # snug the camera (23.5 x 23.4 across, 26.5 front to back): thicken the side walls and both end plates inward
    fills = []
    xi, zi = a.cam_x / 2, a.cam_z / 2
    if xi < 12.8:
        for sx in (-1, 1):
            fills.append(box(min(sx * xi, sx * 12.9), max(sx * xi, sx * 12.9), -14.0, 12.9, -14.8, 14.8))
    if zi < 14.71:
        rear = box(-12.9, 12.9, -14.0, 12.9, -14.8, -zi)
        rear = boolean("difference", [rear, box(-a.slot / 2, a.slot / 2, -15, 1.0, -16.5, 0)])
        lens = box(-12.9, 12.9, -14.0, 12.9, zi, 14.8)
        bore = trimesh.creation.cylinder(radius=17.9 / 2, height=10, sections=64)
        bore.apply_translation([-0.27, 0.33, 14])
        lens = boolean("difference", [lens, bore])
        fills += [rear, lens]
    if fills:
        pod = boolean("union", [pod] + fills)

    th = np.radians(a.tilt)
    s, c = np.sin(th), np.cos(th)
    zf = 16.0 - a.inset
    p0 = np.array([0, -14.0, zf])                    # plane meets the open top edge here
    # local frame of the flange: x, u (down the plane towards the closed side), f (plane normal, towards the lens)
    M = np.eye(4)
    M[:3, 0] = [1, 0, 0]
    M[:3, 1] = [0, c, -s]
    M[:3, 2] = [0, s, c]
    M[:3, 3] = p0
    v0 = -a.top_ext / c
    v1 = (28.0 + a.bottom_ext) / c
    lip = box(-a.lip_w / 2, a.lip_w / 2, v0, v1, -a.lip_t, 0.0)
    lip.apply_transform(M)
    # ring: keep only what is outside the pod's outline (shrunk 0.1 mm so it overlaps the 1.2 mm walls)
    lip = boolean("difference", [lip, box(-13.9, 13.9, -13.9, 13.9, -60, 60)])
    if a.bottom_ext <= 0:
        lip = boolean("intersection", [lip, box(-60, 60, -60, 14.0, -60, 60)])   # flush with the closed wall
    body = boolean("union", [pod, lip])

    # print: closed wall (y=+14) on the bed, open side up
    body.apply_transform(rot(np.radians(-90), [1, 0, 0]))          # new z = -y
    body.apply_translation([0, 0, -body.bounds[0][2]])
    body.apply_translation([0, -body.bounds.mean(axis=0)[1], 0])
    out = Path(a.out)
    out.parent.mkdir(parents=True, exist_ok=True)
    body.export(str(out.with_suffix(".stl")))
    print("lens stands past the plane: top %.1f mm, closed side %.1f mm" % (a.inset, 16 - (zf - 28 * np.tan(th))))
    print("ok extents", body.extents.round(1), "watertight", body.is_watertight, "vol %.1f cm3" % (body.volume / 1000),
          "bodies", len(body.split(only_watertight=False)))


if __name__ == "__main__":
    main()
