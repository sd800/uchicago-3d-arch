# Validation record

## 26.10.18.7 — Rockefeller Chapel exterior reconstruction

- Architectural review is separate from technical acceptance. Compared the rebuilt south front with the university library's built entrance photograph, the southwest aerial with its roof/volume arrangement, and the east elevation with the university's tower photograph. Corrected the full-width high nave, cross-roof valleys, window groups, portal proportions, supported buttresses and solid chevron crown parapet. Sources and view-specific observations are in `sources/highlight_architecture_audit.json`.
- Individual sculpture and small profiles remain abstracted; section/member dimensions are photo interpretations except for the published 207-foot tower peak. No claim is made that all 19 Highlights now meet the revised detailed-fidelity standard. Joinery coverage is recorded as a technical production check only.
- Final exported GLB rendered in the production map with Explore selection and original material colors; no console errors. Isolated south, east, southwest aerial and north low views inspected for geometry/support continuity.
- Native GLB and FBX: 1,377 mesh objects and 3,540,730 triangles. Every FBX position/index matches the corresponding GLB mesh; independent Three.js FBX and 3DS imports pass. Rhino read-back: 290 closed native solids, 1,087 closed meshes, 177 plan curves and 178 nonempty layers; all geometry valid.
- Fifteen physical Highlight form checks pass, including the nave/cross-roof junction, genuinely open bell-stage apertures, published crown height, connected eight-riser entrance and open southeast passage. Ground contact passes for all 177 buildings; terrain occlusion passes in 24 horizontal/low directions.
- SEO and lossless GLB HTTP/local-script/standalone byte integrity checks pass; 3DM/FBX/GLB download order is preserved. Complete model transfer is 3,317,355 bytes, from the 48,474,632-byte extension-free GLB. These delivery/geometry checks do not certify resemblance.

## 26.10.18.5 — GLB / FBX / 3DM delivery

- Native GLB: 1368 mesh objects, 3495468 triangles. Khronos glTF Validator: no errors or warnings on the extension-free download.
- Every native FBX vertex and triangle index matches the corresponding GLB object; meter units, Z-up settings and face normals verified. UChicago also imports with the independent Three.js FBXLoader.
- Web GLB accessor bytes match the native GLB after lossless meshopt/gzip decoding. HTTP, local classic-script and standalone data integrity checks pass.
- Guide lists 3DM, FBX and GLB in order; every linked artifact exists and fits the hosting per-file limit. Oversized native files use lossless XZ archives.
- Refined Rhino model: 288 closed native solids, 1,080 closed meshes, 177 plan curves in 178 nonempty layers; all geometry valid. Existing 19 Highlights and passage/form checks retained.

Earlier verification entries below describe their historical model versions.


Final build checked on 2026-10-12.

## CAD geometry

- Rhino 3DM v7 read back with rhino3dm: meter units, 178 nonempty layers, 1,084 objects; 214 native solid extrusions, 693 closed mesh objects, 177 plan curves. All geometry valid. Three named views preserved.
- Independently parsed 3DS with Three.js TDSLoader: 907 mesh objects, 912,482 vertices, 1,489,328 triangles. Every exported object name matches the layer mapping and is within the 10-character import limit.
- Export pipeline asserts finite coordinates, consistent winding for polygon extrusions, closed meshes, and per-object 3DS vertex/face count limits. Courtyard holes are triangulated with constrained Delaunay triangulation.
- Coordinate bounds in meters: X approximately 67.805–1494.920, Y 133.640–1447.435, Z −1–74.676. −1 is the base slab bottom; relative ground is Z=0.
- Rubenstein’s model peak verified at 52.00 m; Rockefeller at 63.09 m. Mansueto retains its glazed dome in the massing display when its steel grid and facade details are hidden.
- The Rhino Python layer-restoration helper is provided but not executed in an installed Rhino application here. Native .3dm layers are already stored and read-back verified.

## Initial offline viewer and interaction

- Served final HTML on loopback HTTP; response 200. Checked in the Codex in-app WebGL browser.
- Desktop viewport 1440 × 920 and mobile viewport 390 × 844 checked. Mobile document scroll width equals viewport width; header, language button and layer panel remain usable.
- English and Chinese switching checked; selected language persists on reload. Eight preference cases cover English, Chinese variants, mixed preference lists, manual choices and unsupported saved values.
- English name search, Chinese name search and ID search checked. Selection, displayed dimensions/source notes, Locate, Isolate, Show all, landscape/detail switches, height slice, Campus/Main Quads/Plan/Reset and help dialog checked.
- 3DS downloaded through the page. SHA-256 equals the deliverable: `d2b4f42c1ed3bbe04af65b43d49eb9cdeea83e87e6b6da0604dd5dfb5d5847f7`.
- Final title and primary metric numerals use embedded Manrope. The title uses normal letter spacing in desktop and mobile rules.
- Static inspection confirms embedded engine, model, preview and font, with no external script/style/font/image dependency. Source links are optional outbound reference links. The local file URL itself was not opened by the controlled browser; browser QA used loopback HTTP.
- This verification checks file integrity and viewer behavior, not surveying accuracy. See the per-building status and source records for published versus estimated dimensions.


## SEO and typography update — 2026-10-12

- Root HTML remains below 0.4 MB after adding reviewed Chinese names and search aliases. All 177 building names are present before JavaScript runs; model bytes load separately. A generated single-file HTML remains available for portable offline viewing.
- Canonical URL, Open Graph/Twitter metadata, JSON-LD, robots.txt, sitemap.xml and CNAME use `https://uchi.arch.songming.org/`.
- Generated SEO metadata, static directory, local resource references, schema links, sitemap and offline edition passed `scripts/check_seo.py`.
- HTTP loading, local classic-script loading and inline loading reproduce the original 3DS SHA-256; HTTP and local-script failures are handled. Eight device-language/remembered-choice cases passed.
- In-app WebGL browser verified model rendering, 177 building rows, Mansueto search, both language switches and a stable canonical URL. No console errors or warnings were recorded.
- English and Chinese headers are 20px at desktop width and 16px at 390px width, with normal/nonnegative letter spacing. Chinese body, titles, numbers, details and dialogs use the Innovation Harbour system font stack. Sidebar building text is 12px, metadata 10px, search 14px, and explanatory text 11–12px.
- About section is absent. Desktop and 390px layouts show no horizontal document overflow.
- CAD geometry and original model files are unchanged. Hosting and DNS setup are separate from repository metadata generation.

- Reviewed all 177 Chinese building names and short labels; 82 entries revised. Full English names remain visible in Chinese building details. Coverage checks verify Chinese labels for every mapped building and the corrected Law Quadrangle name.
- Reviewed Chinese UI, per-building descriptions and height-basis wording. Main Quads is「主庭院区」; Law Quadrangle is「法学院庭院」. Old labels remain searchable aliases. See `sources/TRANSLATION_NOTES.md` for naming decisions and references.


## Phoenix map-scroll logo — 2026-10-12

- Adapted the owner's original phoenix-key emblem by replacing the key with a closed rolled map scroll. Original reference file is unchanged.
- Preserved a full-resolution PNG with transparent corners and exported 192px header, 180px Apple touch icon, and 16px/32px favicons. ICO contains the 16px/32px PNG exports.
- Browser verified the 192px asset loads and displays at 36px in the existing 70px header. Campus canvas still renders; no console errors or warnings. SEO/resource-reference checks pass.
- Single-file offline edition embeds the same header and favicon PNGs without runtime external image dependencies.


## Landmark zoom-out fix — 2026-10-12

- Reproduced the issue by selecting Mitchell Tower and scrolling outward twice. The scale stopped changing at 50m because the fixed minimum zoom of 0.25 allowed only a fourfold zoom-out from the small fitted frustum.
- Minimum zoom now derives from the full model diagonal and current frustum's shorter side. It is recalculated on building/view fits and viewport resize; existing close-up maximum zoom is retained.
- Regression checks with actual Three.js OrbitControls reproduce the old failure and verify all 177 building targets across three viewport shapes (531 zoom-out/refit cases), requiring every campus bounding-box corner to be visible at the farthest view.
- Browser verified Mitchell Tower, Robie House in a 390px portrait viewport, and Mansueto Library after consecutive selection and zooming. Each can zoom outward well beyond the previous neighborhood limit. Campus, Plan and Reset remain usable; no browser errors or warnings.
- Updated both the served viewer bundle and the generated single-file offline viewer. CAD files are unchanged.
