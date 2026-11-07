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
| Lens ring diameter | 14 mm, edge to edge all the way round (owner measured) |
| Brace mounting plane | The plane where the brace's bolts lock is 12 mm behind the ring face at the BOTTOM of the opening and 30 mm behind it at the TOP (~27 deg slope across the 34.76 mm span). The whole area behind the camera is open, so this is a mounting plane, not an obstruction. Still needed: where the bolts sit on that slope and the depth at their height, the real slope angle, and the camera aim |
| Old strap pad (gray tab) | Looks like a wedge in the edge-on photo; probably filled the slope. Dimensions not yet measured |
| Trim opening | 35.03 mm wide x 34.76 mm (other dimension) |
| Bolt | M6 (thread 5.92 mm), 20.01 mm long, hex flange head with washer |
| Strap length | 121.36 mm |
| Strap bolt holes | 109.79 mm far edge to far edge, 96.69 mm near edge to near edge. So centre spacing 103.24 mm and hole diameter 6.55 mm (holes 9.06 mm from each end of the 121.36 mm strap, matching the photo) |
| Cable | Camera has 6 m video lead and 1 m power lead |

## Open questions
1. What the bolts thread into inside the lid, and the real centre-to-centre spacing in the car.
2. Slope behind the opening: which side is shallow (12 mm) and which deep (30 mm); depth at the middle
   of each edge and the centre; whether the surface is a plane. Wedge pad dimensions. Desired camera aim.
3. Corner radii of the opening, and whether its sides are straight (photo 2 looked trapezoidal).
4. The rough patch at the top of the pocket: leftover adhesive or a broken piece?

## Design (v2)
- The brace bolts to a completely flat plane (owner). The bolt line is at mid-slope, 21 mm behind the
  ring face. The ring face is tilted relative to that plane by atan((30-12)/34.76) = 27.4 deg.
- Pod: a straight prism perpendicular to the ring face, filling the opening (minus a 0.6 mm gap), front
  flush with the ring face, rear cut off by the brace plane. Flange: 121.4 x 44 x 3 mm on the ring side
  of the plane, M6 holes 103.24 mm apart, perpendicular to the plane.
- Camera pocket tilted DOWN 15 deg relative to the ring-face normal (not tested on the car; the real
  angle could not be measured). The back is open. The flared window keeps the original camera's
  136 x 100 deg view clear; `extra_checks` reports the clear angles (default: ~69 deg each side, 54 down).
- STL export is in print orientation (ring face down on the bed); STEP is in the car frame.
  The brace overhangs and needs support.

## Known limitations
- The flared window cuts through the bottom lip of the pod's front, so the lowest rim is open at the face.
- The flange sits on the ring side of the plane (assumed); if the strap actually sits behind the plane,
  the pod needs to be 3 mm longer.
- 15 deg is relative to the ring face, not the horizon.

## Not yet modelled
Snap hooks, camera retention (screw or clip), TPU gasket, cable strain relief, corner radii on the pod,
OEM styling.
