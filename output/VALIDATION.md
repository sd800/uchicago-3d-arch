# Validation record

Final build checked on 2026-10-12.

## CAD geometry

- Rhino 3DM v7 read back with rhino3dm: meter units, 178 nonempty layers, 1,084 objects; 214 native solid extrusions, 693 closed mesh objects, 177 plan curves. All geometry valid. Three named views preserved.
- Independently parsed 3DS with Three.js TDSLoader: 907 mesh objects, 912,482 vertices, 1,489,328 triangles. Every exported object name matches the layer mapping and is within the 10-character import limit.
- Export pipeline asserts finite coordinates, consistent winding for polygon extrusions, closed meshes, and per-object 3DS vertex/face count limits. Courtyard holes are triangulated with constrained Delaunay triangulation.
- Coordinate bounds in meters: X approximately 67.805–1494.920, Y 133.640–1447.435, Z −1–74.676. −1 is the base slab bottom; relative ground is Z=0.
- Rubenstein’s model peak verified at 52.00 m; Rockefeller at 63.09 m. Mansueto retains its glazed dome in the massing display when its steel grid and facade details are hidden.
- The Rhino Python layer-restoration helper is provided but not executed in an installed Rhino application here. Native .3dm layers are already stored and read-back verified.

## Offline viewer and interaction

- Served final HTML on loopback HTTP; response 200. Checked in the Codex in-app WebGL browser.
- Desktop viewport 1440 × 920 and mobile viewport 390 × 844 checked. Mobile document scroll width equals viewport width; header, language button and layer panel remain usable.
- English and Chinese switching checked; selected language persists on reload. Eight preference cases cover English, Chinese variants, mixed preference lists, manual choices and unsupported saved values.
- English name search, Chinese name search and ID search checked. Selection, displayed dimensions/source notes, Locate, Isolate, Show all, landscape/detail switches, height slice, Campus/Main Quads/Plan/Reset and help dialog checked.
- 3DS downloaded through the page. SHA-256 equals the deliverable: `d2b4f42c1ed3bbe04af65b43d49eb9cdeea83e87e6b6da0604dd5dfb5d5847f7`.
- Final title and primary metric numerals use embedded Manrope. The title uses normal letter spacing in desktop and mobile rules.
- Static inspection confirms embedded engine, model, preview and font, with no external script/style/font/image dependency. Source links are optional outbound reference links. The local file URL itself was not opened by the controlled browser; browser QA used loopback HTTP.
- This verification checks file integrity and viewer behavior, not surveying accuracy. See the per-building status and source records for published versus estimated dimensions.
