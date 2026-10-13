# Changelog

All notable changes to UChicago Campus 3D Model are recorded here. Versions use `YY.M.D.NUM`, with a separate release sequence for each day in America/Chicago.

## 26.10.13.1 — 2026-10-13

- Render ground, roads, walks, paving, lawns, gardens, water and markings in a stable cartographic stack. Keep only their upward-facing skins so intersecting terrain facets and extrusion seams cannot obscure the map.
- Preserve CAD vertex positions and downloads, with normal depth occlusion for buildings, trees, walls and furniture. Retain depth testing for transparent glass and stabilize exterior detail surfaces.
- Fit the orthographic depth range to campus bounds at every view and avoid regenerating unchanged shadows during navigation.
- Apply elevation sections consistently to surfaces and shadow casters, removing shadows cast by clipped geometry.
- Invalidate cached viewer scripts by content checksum so browser reloads receive the current renderer.
- Add CAD surface/frustum checks and a real WebGL regression scene with 48 moving views, 144 pixel samples and section-shadow checks. Verify pan, rotation, layer toggles and actual campus images.

## 26.10.12.8 — 2026-10-12

- Use ground-aligned navigation: left-drag or one finger pans, right-drag rotates, and the Rotate control enables explicit drag rotation.
- Keep the pivot over visible ground, preserve local building inspection, and zoom toward the pointer. Remove inertia and limit low-angle views and abrupt zoom steps.
- Prevent drags, multi-touch and canceled gestures from selecting buildings accidentally; add keyboard navigation and coalesce rendering with display frames.
- Retain the intended selection during loading and preserve map scale during viewport resizing.
- Show model loading progress through data reading, decoding, geometry parsing and scene preparation. Parse geometry in a background worker.
- Maintain calendar release commit messages, this English changelog and the root VERSION file.

## 26.10.12.7 — 2026-10-12

- Rename the English title to UChicago Campus 3D Model throughout the viewer, document metadata, sharing information and export labels.

## 26.10.12.6 — 2026-10-12

- Preserve the campus-wide zoom-out range after focusing on a landmark, including responsive viewport changes.

## 26.10.12.5 — 2026-10-12

- Use normal letter spacing for the campus subtitle.

## 26.10.12.4 — 2026-10-12

- Match the footer text size to the Innovation Harbour viewer and remove the duplicate visible-building counter from the footer.

## 26.10.12.3 — 2026-10-12

- Add the maroon phoenix and rolled-map project logo, matching favicon and device icon assets.

## 26.10.12.2 — 2026-10-12

- Add search metadata, canonical and sharing URLs, structured model data, a sitemap, robots rules and a crawlable bilingual building directory.
- Configure uchi.arch.songming.org and refine bilingual titles, typography, sidebar readability and Chinese building translations.
- Simplify the viewer by removing the lengthy campus description panel.

## 26.10.12.1 — 2026-10-12

- Introduce the Hyde Park exterior campus model with 177 building layers, a separate environment layer and 19 architectural highlights.
- Provide metric 3DS and layered Rhino files, an interactive English/Chinese website and a self-contained offline edition.
- Include building visibility, dimensions and sources, landmark exploration, plan views, exterior details, slicing and image export.
