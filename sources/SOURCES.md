# Source register / 资料来源

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

### Rockefeller Memorial Chapel

- [University photographic archive: southwest aerial](https://photoarchive.lib.uchicago.edu/db.xqy?one=apf2-06545.xml)
- [University photographic archive: built south entrance](https://photoarchive.lib.uchicago.edu/db.xqy?one=apf2-06824.xml)
- [Historic front elevation drawing, checked against built photographs](https://photoarchive.lib.uchicago.edu/db.xqy?one=apf2-06570.xml)

- [Primary reference](https://www.rockefeller.uchicago.edu/the-spaces/rockefeller-architecture/)
- [Primary reference](https://www.rockefeller.uchicago.edu/the-spaces/rockefeller-interior/)

### Mitchell Tower

- [Primary reference](https://upload.wikimedia.org/wikipedia/commons/d/db/The_University_of_Chicago%3B_an_official_guide_%28IA_universityofchic00robe%29.pdf)
- [Primary reference](https://campub.lib.uchicago.edu/pdf/?docId=mvol-0445-0005-0004)

### Hutchinson Commons / Reynolds Club / Mandel Hall

- [Primary reference](https://architecture.uchicago.edu/locations/tower_group_mitchell_tower_hutchinson_commons_reynolds_club_mandel_hall/)
- [Primary reference](https://campub.lib.uchicago.edu/pdf/?docId=mvol-0007-0008-0006)

### Joe and Rika Mansueto Library

- [Primary reference](https://www.lib.uchicago.edu/mansueto/tech/numbers/)

### Joseph Regenstein Library

- [Primary reference](https://www.lib.uchicago.edu/spaces/joseph-regenstein-library/)

### Frederick C. Robie House

- [Primary reference](https://www.flwright.org/explore/frederick-c-robie-house)
- [Primary reference](https://www.loc.gov/resource/hhh.il0039.sheet/?sp=17&st=image)
- [Primary reference](https://tile.loc.gov/storage-services/master/pnp/habshaer/il/il0000/il0039/data/il0039data.pdf)
- [Primary reference](https://npgallery.nps.gov/GetAsset/7475e81f-3634-4a9e-87c7-e3c35f8556a0)

### Reva and David Logan Center for the Arts

- [Primary reference](https://news.uchicago.edu/story/reva-and-david-logan-center-arts-preview-period-begin-march-26)
- [Primary reference](https://architecture.uchicago.edu/locations/reva_and_david_logan_center_for_the_arts/)

### David Rubenstein Forum

- [Primary reference](https://global.ctbuh.org/resources/papers/4631-Gallagher_DavidRubensteinForum.pdf)
- [Primary reference](https://architecture.uchicago.edu/locations/david_rubenstein_forum/)

### Saieh Hall for Economics

- [Primary reference](https://architecture.uchicago.edu/locations/department_of_economics_and_becker_friedman_institute/)
- [Primary reference](https://www.annumarchitects.com/projects/university-of-chicago/)

### William Rainey Harper Memorial Library

- [Primary reference](https://campub.lib.uchicago.edu/text/?docId=mvol-0001-0016-0000)
- [Primary reference](https://campub.lib.uchicago.edu/pdf/?docId=mvol-0445-0005-0004)
- [Primary reference](https://architecture.uchicago.edu/locations/william_rainey_harper_memorial_library/)

### Gerald Ratner Athletics Center

- [Primary reference](https://athletics.uchicago.edu/sports/2023/6/12/ratner.aspx)
- [Primary reference](https://chronicle.uchicago.edu/031009/ratner-arch.shtml)

### Campus North Residential Commons / Baker Dining Commons

- [Primary reference](https://studiogang.com/projects/university-of-chicago-campus-north-residential-commons/)
- [Primary reference](https://housing.uchicago.edu/residence-life/residential-commons/campus-north/)
- [Primary reference](https://transsolar.com/projects/chicago-campus-north-residence-hall-dining-commons)
- [Primary reference](https://tgda.net/projects/university-of-chicago-campus-north-residence-commons/)

### Woodlawn Residential and Dining Commons

- [Primary reference](https://www.turnerconstruction.com/projects/woodlawn-residential-dining-commons)
- [Primary reference](https://www.pmainc.com/project/woodlawn-commons-at-university-of-chicago/)
- [Primary reference](https://www.elkus-manfredi.com/project/university-of-chicago-woodlawn-residential-and-dining-commons/)

### William Eckhardt Research Center

- [Primary reference](https://www.thorntontomasetti.com/project/eckhardt-research-center)
- [Primary reference](https://thornton.s3.amazonaws.com/content_files/969/TheUniversityofChicago_WERC_Project_Sheet.pdf)

### Keller Center / Harris School of Public Policy

- [Primary reference](https://architecture.uchicago.edu/locations/keller_center/)
- [Primary reference](https://harris.uchicago.edu/about/who-we-are/keller-center)
- [Primary reference](https://harris.uchicago.edu/files/inline-files/Welcome%20Guide_Student_FINAL_0.pdf)

### Edith Abbott Hall / Crown Family School

- [Primary reference](https://architecture.uchicago.edu/locations/crownschool/)

### Laird Bell Law Quadrangle / D'Angelo Law Library

- [Primary reference](https://architecture.uchicago.edu/locations/laird_bell_law_quadrangle/)
- [Primary reference](https://www.law.uchicago.edu/students/libraryservices)

### Ellen and Melvin Gordon Center for Integrative Sciences

- [Primary reference](https://www.powerconstruction.net/projects/science-lab-construction/university-chicago-gordon-center-integrative-sciences)
- [Primary reference](https://fliphtml5.com/cbqrb/tilx/Power_Construction_Higher_Education_Brochure_/25/)
- [Primary reference](https://architecture.uchicago.edu/locations/gordon_center_for_integrative_science/)

### John Crerar Library

- [Primary reference](https://www.lib.uchicago.edu/crerar/about-crerar-library/history/)
- [Primary reference](https://architecture.uchicago.edu/locations/john_crerar_library/)
