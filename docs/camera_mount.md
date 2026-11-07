# Camera mount (2012 Lexus IS 350 sedan, aftermarket camera)

Status: v1 draft. Most dimensions are now caliper readings; the open items are listed below.

## Facts
- Car: 2012 IS 350 sedan, VIN JTHBE5C26C5029206 (model year 2012, second generation).
  Original camera: Dorman 590-645, OE 86790-53011 (sedan). The convertible part (590-649,
  OE 86790-53021) is a different part. Listing dimensions are template values, not usable.
- Original viewing angle: 136 deg horizontal, 100 deg vertical (use for the lens window).
- Printer: Bambu P1S (hardened hot end, AMS). No A1 any more.
- Material: ASA for the car (heat/UV); PETG-CF is the fallback; TPU for a gasket. PLA only for fit tests.
- Original design: a flat bracket with two bolt holes and a small camera housing in the middle.
- Previous hack (`lexus-backup-cam-mount.stl/.3mf`): a thin-walled box ~28 x 28 x 32 mm, no flange,
  bolt holes or latches. It is held by a separate strap with two bolts inside the lid.

## Measurements (calipers unless noted)
| Item | Value |
|---|---|
| Camera body, across | 23.54 and 23.37 mm |
| Camera front to back | 26.49 mm |
| Camera cable diameter | 3.06 mm |
| Lens ring diameter | ~14 mm (photo estimate, not measured) |
| Trim opening | 35.03 mm wide x 34.76 mm (other dimension) |
| Bolt | M6 (thread 5.92 mm), 20.01 mm long, hex flange head with washer |
| Strap length | 121.36 mm |
| Strap bolt holes | 109.79 mm far edge to far edge, 96.69 mm near edge to near edge. So centre spacing 103.24 mm and hole diameter 6.55 mm (holes 9.06 mm from each end of the 121.36 mm strap, matching the photo) |
| Cable | Camera has 6 m video lead and 1 m power lead |

## Open questions
1. What the bolts thread into inside the lid, and the real centre-to-centre spacing in the car.
2. Depth: how far behind the opening face the strap sits; clearance behind the camera.
3. Corner radii of the opening, and whether its sides are straight (photo 2 looked trapezoidal).
4. The rough patch at the top of the pocket: leftover adhesive or a broken piece?
5. Lens ring diameter.

## Not yet modelled
Snap hooks, camera retention (screw or clip), TPU gasket, tilt, cable strain relief,
window flare for the wide-angle view, corner radii on the pod, OEM styling.
