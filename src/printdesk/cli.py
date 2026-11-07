"""Command line: build a registered part from JSON params, validate it, export STEP/STL/3MF.

    uv run printdesk list
    uv run printdesk build mounting_plate --material PETG-CF --params '{"width": 60}' --out out/plate
"""
import argparse
import json
import sys
from pathlib import Path

from build123d import export_step, export_stl

from . import materials
from .parts import REGISTRY
from .validate import check


def build_part(name: str, params: dict, material_name: str):
    if name not in REGISTRY:
        raise SystemExit(f"unknown part {name!r}; known: {sorted(REGISTRY)}")
    mod = REGISTRY[name]
    material = materials.get(material_name)
    p = mod.Params(**params)
    solid = mod.build(p, material)
    report = check(solid, mod.describe(p, material), material)
    return solid, report, p


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(prog="printdesk")
    sub = ap.add_subparsers(dest="cmd", required=True)
    sub.add_parser("list")
    b = sub.add_parser("build")
    b.add_argument("part")
    b.add_argument("--material", default="PLA")
    b.add_argument("--params", default="{}", help="JSON object")
    b.add_argument("--out", required=True, help="output path without extension")
    a = ap.parse_args(argv)

    if a.cmd == "list":
        for name, mod in sorted(REGISTRY.items()):
            print(name)
            print(json.dumps(mod.Params.model_json_schema(), indent=2))
        return 0

    solid, report, p = build_part(a.part, json.loads(a.params), a.material)
    for w in report.warnings:
        print("warning:", w, file=sys.stderr)
    for e in report.errors:
        print("ERROR:", e, file=sys.stderr)
    if not report.ok:
        return 1
    out = Path(a.out)
    out.parent.mkdir(parents=True, exist_ok=True)
    export_step(solid, str(out.with_suffix(".step")))
    export_stl(solid, str(out.with_suffix(".stl")))
    meta = {"part": a.part, "material": a.material, "params": p.model_dump()}
    out.with_suffix(".json").write_text(json.dumps(meta, indent=2))
    print(f"ok: wrote {out}.step/.stl/.json")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
