import numpy as np
import trimesh

from printdesk.cli import build_part


def test_gauge_pieces_have_the_requested_heights_and_print_without_overhangs(tmp_path):
    from build123d import export_stl
    solid, report, p = build_part("tilted_gauge", {}, "PLA")
    assert report.ok, report.errors
    f = tmp_path / "g.stl"
    export_stl(solid, str(f))
    m = trimesh.load(str(f))
    assert m.is_watertight and abs(m.bounds[0][2]) < 1e-6
    pieces = sorted(m.split(only_watertight=False), key=lambda q: q.bounds[0][0])
    assert [round(q.extents[1], 1) for q in pieces] == p.heights
    assert all(abs(q.extents[0] - p.width) < 0.01 for q in pieces)
    n, z, a = m.face_normals, m.triangles_center[:, 2], m.area_faces
    down = np.degrees(np.arccos(np.clip(-n[:, 2], -1, 1))) < 45
    assert a[(n[:, 2] < 0) & down & (z > 0.1)].sum() < 1.0
