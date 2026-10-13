# Changelog

All notable changes to UChicago Campus 3D Model are recorded here. Versions use `YY.M.D.NUM`, with a separate release sequence for each day in America/Chicago.

## 26.10.13.3 — 2026-10-13

- Restore the full viewing range from overhead to an exactly horizontal elevation. Add a bilingual Level control that retains the current bearing, local pivot and zoom.
- Replace low-angle ground-ray intersections with bounded orthographic panning and continuous vertical framing. Keep ground pivots stable and prevent abrupt travel, reversed directions, camera roll or tilt during pan and cursor zoom.
- Preserve pointer zoom at every elevation; carry inspection framing through resize and clear it when returning to campus, building or plan presets. Retain explicit rotation, immediate stopping, touch safeguards and selected-building highlights.
- Add 144 low-angle regression cases across six elevations, eight bearings and three viewport shapes, covering exact level views, pan, pointer zoom, ground pivots, resize, reset and absence of drift.

## 26.10.13.2 — 2026-10-13

- Remove flickering roof shadow bands with a fixed sampling kernel and receiver-plane depth correction. Fit a fixed sunlight volume to the campus and use a small physical shadow bias without screen-dependent sampling noise.
- Use subdued gray roof surfaces while preserving wall colors, stone trim and ground-level concrete. Keep roof colors coherent when exterior details are hidden.
- Give coplanar roof sheets and concrete accents distinct depth priorities. Keep thin roof sheets visible above closed building caps using a small orthographic bias that is consistent across depth-buffer formats; preserve CAD coordinates and normal building occlusion.
- Extend real WebGL checks with 800 roof samples covering lighting, coplanar accents, recessed sheets and taller occluders during pan, rotation and zoom. Reproduce and repair the actual North Campus roof conflict with delivered G. G. Brown geometry. Verify actual campus close-ups, North Campus navigation and unchanged CAD downloads.

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
