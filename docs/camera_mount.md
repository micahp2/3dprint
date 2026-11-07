# Camera mount (2012 Lexus IS 350 sedan, aftermarket camera)

Status: v0, PROVISIONAL. Defaults are estimates read off photos, not measurements.

## Facts
- Car: 2012 IS 350 (VIN decodes to model year 2012, second generation). Body panels match the IS 250.
- Printer: Bambu P1S (hardened hot end, AMS). No A1 any more.
- Material: ASA for the car (heat/UV); PETG-CF is the fallback; TPU for a gasket. PLA only for fit tests.
- Original design (IS 250/350 OEM photo): flat bracket, two bolt holes, small camera housing in the middle.
- The previous hack (`lexus-backup-cam-mount.stl/.3mf`): a thin-walled box, ~28 x 28 x 32 mm,
  with no flange, bolt holes or latches. It is held by a separate strap with two bolts inside the lid.

## Estimates (replace with calipers)
| Item | Estimate | Source |
|---|---|---|
| Camera body | ~25.5 x 25.5 x 28 mm | photos with a tape |
| Lens ring | ~19 mm | photo |
| Trim ring inner opening | ~35 x 31 mm | photo 1 |
| Trim ring outer | ~48 x 43 mm | photo 1 |
| Strap bolt spacing | ~96 mm | photo of the strap |
| Strap bolt holes | ~5 mm (screw size unconfirmed; "10m" said) | photo |

## Open questions
1. Real bolt spacing, hole diameter and screw size (M5? M10?).
2. What the strap bolts thread into inside the lid.
3. Opening: true inner/outer size, corner radius, depth to the ledge, whether it is a trapezoid.
4. Camera: caliper dimensions, cable exit position.
5. The rough patch at the top of the pocket: leftover adhesive or a broken piece?

## Not yet modelled
Snap hooks, camera retention (screw or clip), TPU gasket, tilt, cable strain relief, OEM styling.
