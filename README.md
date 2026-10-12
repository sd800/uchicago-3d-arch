# UChicago Campus in 3D

A public-source exterior model of the University of Chicago’s Hyde Park campus, with a self-contained interactive viewer, a layered Rhino model, and a 3DS mesh export.

**Open `index.html` directly in a modern browser.** The model, Three.js engine, display font and fallback image are embedded. Internet access, npm and a local server are unnecessary for viewing. WebGL 2 and graphics acceleration are needed for the interactive canvas. An image preview and building information remain available when rendering is unavailable.

The interface defaults to English. On first use, any Chinese language in the device’s preferred language list selects Chinese. The language button switches both ways; an available browser local storage remembers the manual choice.

## Deliverables

| File | Purpose |
| --- | --- |
| `index.html` | Offline English / Chinese 3D viewer |
| `output/UChicago_HydePark_Layered.3dm` | Rhino v7 model in meters, with 177 individual building layers and one outdoor environment layer |
| `output/UChicago_HydePark.3ds` | Triangulated meshes with short object names and material assignments |
| `output/layer_map.json` | Complete object-to-building/environment mapping for the 3DS export |
| `scripts/apply_layers_rhino.py` | Restore building layers after importing 3DS into Rhino |
| `output/建筑尺寸与来源.csv` | Per-building dimensions, height status, assumptions and source URLs |
| `output/道路宽度与来源.csv` | Mapped road/walkway widths and estimation flags |
| `output/campus_aerial.png` | Bird’s-eye preview rendered from the exported meshes |
| `output/campus_plan.png` | North-up footprint atlas with landmark codes and scale |
| `output/使用说明.md` | Chinese import, viewing and accuracy guide |
| `sources/SOURCES.md` | Source register and modeling decisions |
| `output/VALIDATION.md` | CAD and browser verification record |

## Scope and accuracy

The model covers the campus boundary mapped in OpenStreetMap and the adjacent Midway Plaisance. It includes historic quadrangles, the north residential/science area, medical buildings, east teaching buildings and the south campus. Small ancillary buildings and campus support properties are included where mapped. This is an independent model, not a university-issued BIM.

**1 model unit = 1 meter.** X points east, Y north and Z upward in a local UTM zone 16N coordinate frame. The origin is WGS84 longitude −87.607°, latitude 41.782°, with UTM offsets recorded in `output/model_summary.json`. Plan extents come from public map polygons, rather than fitting buildings to a diagram. The GeoJSON file stores local projected meters, as its metadata states; it is not longitude/latitude RFC 7946 GeoJSON.

Eight buildings use selected published maximum heights. Woodlawn uses dimensions in the public 2018 planning drawings, identified separately from as-built values. Remaining building heights are estimated from available floor counts or building use, with explicit status labels. Published maximum heights do not establish every roof or facade dimension. The table records the actual modeled maximum, which may differ slightly because of mesh discretization.

Landmarks receive distinct exterior forms: Gothic towers, pitched roofs and buttresses; Mansueto’s elliptical glazed shell and orthogonal grid; Logan’s tower and studio podium; Rubenstein’s staggered meeting volumes; stepped residential blocks; research penthouses; Keller’s colonnade and roof terrace; Robie’s horizontal brick body and projecting roofs. Details are simplified and approximate. Windows are illustrative repeated bays, rather than measured openings. Elevated connectors retain mapped plans but use estimated vertical dimensions.

The environment layer contains roads, sidewalks, plazas/paved areas, lawns, courtyard voids, sports surfaces, the approximate Law School pool, planting, benches and lights. Tree placements, planting density, lane markings and small furniture are illustrative. Road widths are documented approximations unless mapped width tags exist. Ground is flattened to relative Z=0; no surveyed terrain, interiors or underground structure is included. This model is suitable for campus-scale visualization and study, not survey, construction or fabrication.

## Rhino and 3DS

Open the `.3dm` for preserved Rhino layers, native closed massing extrusions, editable detail meshes, footprint curves and named views. It already declares meters. The `.3ds` preserves mesh/material/object information but has limited unit and layer support; select meters on import and run `scripts/apply_layers_rhino.py` if building layers are needed. Verify a known dimension after import, such as Rockefeller’s modeled tower peak near 63.09 m. Keep the mapping JSON next to the model, or choose it in the script’s file dialog.

## Rebuild from the saved source snapshot

```sh
python3 -m venv .venv
source .venv/bin/activate
pip install -r scripts/requirements.txt
npm ci
mkdir -p tmp
python3 scripts/build_campus.py
python3 scripts/render_preview.py
python3 scripts/render_plan.py
npm run build
python3 scripts/validate_rhino.py
npm run check:3ds
node scripts/check_locale.mjs
```

Source snapshots are retained so the reconstruction can be repeated without refetching map data. The initial build uses source data collected on 2026-10-12. References and attribution are in `sources/SOURCES.md` and `THIRD_PARTY_NOTICES.md`. The viewer bundles Three.js 0.186.1 and the licensed Manrope display font.
