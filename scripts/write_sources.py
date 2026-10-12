"""Write a human-readable source register for the saved public-data snapshot."""
import json,pathlib
root=pathlib.Path(__file__).resolve().parents[1]
refs=json.loads((root/'sources/architecture_sources.json').read_text())
intro='''# Source register / 资料来源

Collected 2026-10-12. These sources establish mapped outlines, selected heights and architectural features. They do not provide a complete, authoritative campus BIM or measured exterior reconstruction.

## Map geometry and floor-count data

- [UChicago official campus map](https://maps.uchicago.edu/) and [2023 official directory PDF](https://d3qi0qp55mx5f5.cloudfront.net/maps/other-campus-maps/UCDirectoryMap_V2_2023.pdf): name, location and scope cross-check. The illustration is not used as a dimensioned survey. The 2023 PDF remains a reference, so recent map outlines come from the separate OSM snapshot.
- [OpenStreetMap API](https://api.openstreetmap.org/api/0.6/map?bbox=-87.612,41.779,-87.589,41.797): downloaded `osm_map.osm`; campus relation 13117436, Midway park relation 19743853, building outlines and road/walkway centerlines. Attribution: © OpenStreetMap contributors, [ODbL](https://www.openstreetmap.org/copyright). Individual feature URLs are in the building/road tables.
- [City of Chicago Building Footprints](https://data.cityofchicago.org/Buildings/Building-Footprints/syp8-uezg): `city_buildings.json` and `city_metadata.json`. Records match by mapped Chicago ID, otherwise by footprint overlap. `stories` supplies a floor-count clue where present; zero values are not interpreted as zero-height buildings. `z_coord` is not treated as building height. The saved historical municipal geometry is not substituted for current mapped plans.
- Projection: WGS84 to EPSG:32616, then local offsets from longitude −87.607°, latitude 41.782°. X east, Y north, Z up. Geographic outline precision is limited by the original mapping, not the millimeter resolution of the CAD file.

## Modeling and reconciliation

Eight selected buildings use published peak heights: Rockefeller, Mitchell, Harper, Mansueto, Logan, Rubenstein, Eckhardt and Center for Care and Discovery. Woodlawn instead uses 2018 PD43 planning dimensions. Other heights use published/OSM/municipal stories with assumed floor heights, or an explicit functional estimate. Each record distinguishes published, planning and estimated values.

Mitchell’s tower box is calibrated to the historical 31 × 35 ft dimensions, centered at the mapped tower. Its geospatial outline remains separately preserved in the footprint database. Mansueto’s whole-building 240 × 120 ft dimensions are not mistaken for the exact dome boundary: dome axes are approximated from the mapped outline, its peak uses 35 ft, and the steel lattice uses roughly six-foot centers parallel to ellipse axes. Roof segmentation, openings, ornaments, landscaping, road widths and connector elevations remain approximate.

Woodlawn’s [Chicago PD43 planning collection](https://gisapps.chicago.gov/gisimages/zoning_pds/PD43.pdf), PDF pages 211 and 223 (one-based), supplies Block W 184 ft and other blocks 94 ft. Pages are planning-stage rather than survey-certified as-built data. Some older proposal sheets and web descriptions have different dimensions/floor counts, so these are not blended into an invented exact value.

For Center for Care and Discovery, [McHugh Concrete’s completed project description](https://mchughconcrete.com/projects/university-of-chicago-hospital-center-for-care-discovery/) gives 245 ft overall. [Rafael Viñoly Architects](https://www.rvapc.com/works/university-of-chicago-medicine-center-for-care-discovery/) gives a 5.5 m floor-to-floor module; [UChicago Medicine](https://www.uchicagomedicine.org/find-a-location/uchicago-medicine-center-for-care-and-discovery-hyde-park) identifies ten stories. The model combines a 55 m occupied mass with an approximate setback mechanical volume reaching 74.676 m; the plant footprint itself is not a measured drawing.

Rubenstein uses the completed 52 m case study rather than an older 165 ft proposal. Logan uses the 2012 school announcement’s 170 ft rather than heights from earlier planning versions. Ratner’s current school page states 100 ft mast peaks, while an opening report describes 125 ft mast lengths; the modeled 100 ft maximum remains flagged estimated because of the unresolved distinction and unknown roof geometry. Mies’s campus building is Edith Abbott Hall / Crown Family School; IIT Crown Hall is not included as a UChicago building.

The source documents and images are architectural references. Photographs and planning drawings are not embedded as model textures or redistributed in the viewing/model archive.

## Landmark reference links

The machine-readable `architecture_sources.json` retains detailed values, units, conflicts and unknowns. The actual modeling choices are recorded in `output/buildings.json` and the bilingual `output/viewer_records.json`.

'''
for b in refs['buildings']:
 intro+='### '+b['name']+'\n\n'
 for source in b.get('sources',[]):
  if 'url' in source:intro+='- ['+source.get('title',source.get('publisher','Primary reference'))+']('+source['url']+')\n'
 intro+='\n'
(root/'sources/SOURCES.md').write_text(intro.rstrip()+'\n')
