# Campus-wide optimized exteriors — 2026-10-18

## Scope and standard

All 158 ordinary building layers now have explicit exterior recipes, alongside the 19 existing individually modeled Highlights. The existing Highlight geometry/material sequences are protected against release 26.10.18.11. This pass targets recognizable exterior massing, local storeys/eaves, roof character, courts, entrances and facade groupings. It does not turn every building into a detailed measured reconstruction. Added window surrounds alone are not evidence of fidelity.

The mapped footprint and court openings remain the primary geometry source. Published owner/architect floor counts inform the specific corrections below. Local eave/ridge heights, partition positions, facade modules, entrance dimensions and small fittings remain estimates. Lesser documented houses and service buildings receive conservative family-based interpretations; they have not all been individually photo-verified. The catalog records this distinction for every layer.

## Principal corrections

- Snell–Hitchcock: low three-storey residential ranges replace the former oversized block; open court, connected roofs and separate front gables.
- International House: nine-storey north range, lower three-storey south wings and a west tower reaching twelve storeys; open mapped court and clay lower roofs.
- Renee Granville-Grossman: stepped five/seven/nine-storey court ranges, distinguishing brick wings and pale corner towers.
- Duchossois and Comer: six-storey precast/glazed medical ranges and a seven-storey green-glass patient block respectively; lower arrival wings, atrium and grounded entrance canopy.
- High Bay: one tall experimental storey and four north-light roof ranges, rather than a generic multistorey office block. Greenhouse: three glass roof ranges above a supported four-storey Donnelley base (corrected in the medical-side pass).
- Main Quadrangles: source-informed limestone ranges, rectangular paired upper lights instead of universal pointed office windows, connected slate/clay wing roofs, restrained entrance-side gables, thresholds and steps. Ryerson receives a supported observatory drum/dome. Kent separates its low lecture range from the taller laboratory wings.
- Pick Hall: concrete/flat-roof Brutalist massing replaces the invented Gothic treatment.
- Midway Studios: low studio/barn and house ranges. South Steam Plant: tall brick boiler hall, large divided industrial lights and paired roof flues from university built photographs.
- Garages: open deck slabs, columns, safety parapets and stair cores replace glass window grids. Cobb Gate has a physically open east–west pedestrian passage.

Roof intersections use straight planar hip/ridge facets on broad wing domains, preserving perimeter indents and court holes. Coplanar roof patches are unioned and hidden facets are removed at overlaps. Thin repeated components remain attached to their local wall/eave; this pass adds no generic rooftop equipment boxes or unsupported vertical fins. Explicit roof material colors are retained in the browser.

## Sources and interpretation

The full per-building list is `sources/building_optimization.json`. Particularly useful primary sources:

- [University Main Quadrangle architectural history](https://architecture.uchicago.edu/locations/main_quadrangle/) and [Cobb Hall](https://architecture.uchicago.edu/locations/cobb_lecture_hall/).
- [Snell–Hitchcock](https://housing.uchicago.edu/residence-life/residential-commons/snell-hitchcock/), [Burton–Judson](https://housing.uchicago.edu/residence-life/residential-commons/burton-judson-courts/), [Grossman](https://housing.uchicago.edu/residence-life/residential-commons/reneee-granville-grossman/) and [International House](https://architecture.uchicago.edu/locations/international_house/): official storey counts and architectural descriptions; local partitions are interpreted.
- [Duchossois](https://architecture.uchicago.edu/locations/duchossois_center_for_advanced_medicine/), [medical work-life account](https://neurology.uchicago.edu/education/residencywork-life), [Comer](https://chronicle.uchicago.edu/060202/comer.shtml).
- [High Bay architect project](https://www.architraveltd.com/uc-nhbb-archive): single-storey high bays and sawtooth northlights.
- [Ryerson history](https://physics.uchicago.edu/about/our-history/ryerson-laboratory/), [Pick Hall context](https://publicart.uchicago.edu/temporary-projects-commissions/dialogo-virginio-ferrari-and-chicago/), [Midway Studios archive](https://www.lib.uchicago.edu/e/scrc/findingaids/view.php?eadid=ICU.SPCL.MIDWAYSTUDIO).
- [South Steam Plant built photograph](https://chronicle.uchicago.edu/081211/plant.shtml) and [university operational account](https://chronicle.uchicago.edu/940818/steam.shtml): tall boiler hall and two flues; flue geometry remains proportional, not measured.

University images were reviewed as source references and are not redistributed as model textures. Original map/source snapshots remain intact.

## Validation

`npm run check:campus-optimization` checks complete recipe coverage, exported geometry, unchanged existing Highlight hashes, key height limits, roof material character, open Cobb Gate and mapped court centers. Rhino readback validates closed native solids and mesh objects. GLB/FBX independent loader checks compare the actual construction export, including online and direct-file/offline byte integrity. Ground, terrain and athletic-field checks cover the retained landscape. Browser contact sheets review every ordinary exterior; the full viewer is checked separately for terrain and scene integration.

These technical checks prevent geometry regressions. They do not certify measured dimensions or photographic equivalence for every estimated facade.

## Per-building decisions

| Code | Building | Exterior family | Storeys / main eave estimate | Evidence status |
|---|---|---|---|---|
| U001 | Campus North Parking Garage | garage | 4 / 13.2 m | conservative mapped exterior interpretation |
| U002 | Campus North Residential Commons | Existing Highlight retained | — | Protected against 26.10.18.11 |
| U003 | Gerald Ratner Athletics Center | Existing Highlight retained | — | Protected against 26.10.18.11 |
| U004 | Cochrane-Woods Art Center | retained | 2 / 9.8 m | existing individual massing retained; facade and entrance reviewed |
| U005 | Court Theatre | retained | 1 / 9.6 m | existing individual massing retained; facade and entrance reviewed |
| U006 | Henry Crown Field House | sports_hall | 1 / 10.5 m | conservative mapped exterior interpretation |
| U007 | David and Alfred Smart Museum of Art | retained | 2 / 9.8 m | existing individual massing retained; facade and entrance reviewed |
| U008 | Young Memorial Building | brick_academic | 3 / 12.0 m | conservative mapped exterior interpretation |
| U009 | Stagg Field | field_gate | 1 / 3.8 m | conservative mapped exterior interpretation |
| U010 | 847 East 56th Street | house | 3 / 9.6 m | conservative mapped exterior interpretation |
| U011 | Max Palevsky Commons Central | retained | 4 / 13.4 m | existing individual massing retained; facade and entrance reviewed |
| U012 | University of Chicago Auto Service Facility | service | 1 / 4.5 m | conservative mapped exterior interpretation |
| U013 | West Campus Combined Utility Plant | retained | 2 / 13.5 m | existing individual massing retained; facade and entrance reviewed |
| U014 | Max Palevsky Commons West | retained | 4 / 13.4 m | existing individual massing retained; facade and entrance reviewed |
| U015 | High Bay Research Building | high_bay | 1 / 7.3 m | source-specific silhouette correction |
| U016 | Michelson Center for Physics | laboratory | 4 / 16.5 m | conservative mapped exterior interpretation |
| U017 | Molecular Engineering Modular Offices | modular | 2 / 7.4 m | conservative mapped exterior interpretation |
| U018 | Max Palevsky Commons East | retained | 4 / 13.4 m | existing individual massing retained; facade and entrance reviewed |
| U019 | Accelerator Building | service_lab | 2 / 9.5 m | conservative mapped exterior interpretation |
| U020 | UChicago Child Development Center - Drexel | daycare | 2 / 7.4 m | conservative mapped exterior interpretation |
| U021 | Knapp Research Center | laboratory | 5 / 21.0 m | conservative mapped exterior interpretation |
| U022 | Joseph Regenstein Library | Existing Highlight retained | — | Protected against 26.10.18.11 |
| U023 | Medical Campus Parking Garage B | garage | 8 / 26.4 m | conservative mapped exterior interpretation |
| U024 | Joe and Rika Mansueto Library | Existing Highlight retained | — | Protected against 26.10.18.11 |
| U025 | Knapp Center for Biomedical Discovery | retained | 10 / 40.7 m | existing individual massing retained; facade and entrance reviewed |
| U026 | Greenhouse | roof_greenhouse | 4 + greenhouse / 21.3 m | four-storey supporting base and rooftop glass ranges |
| U027 | Bartlett Dining Commons | dining_hall | 1 / 10.6 m | conservative mapped exterior interpretation |
| U028 | William Eckhardt Research Center | Existing Highlight retained | — | Protected against 26.10.18.11 |
| U029 | Donnelley Biological Sciences Learning Center | laboratory | 4 / 17.0 m | conservative mapped exterior interpretation |
| U030 | Biopsychology Science Building | laboratory | 3 / 12.6 m | conservative mapped exterior interpretation |
| U031 | Rohr Chabad Jewish Center | house | 2 / 6.8 m | conservative mapped exterior interpretation |
| U032 | Mitchell Tower | Existing Highlight retained | — | Protected against 26.10.18.11 |
| U033 | Neubauer Collegium | historic_house | 3 / 10.2 m | conservative mapped exterior interpretation |
| U034 | Zoology | gothic_lab | 3 / 13.2 m | conservative mapped exterior interpretation |
| U035 | Cobb Gate | gate | 2 / 7.4 m | conservative mapped exterior interpretation |
| U036 | Anatomy | gothic_lab | 3 / 13.2 m | conservative mapped exterior interpretation |
| U037 | Quadrangle Club | tudor_club | 3 / 10.3 m | conservative mapped exterior interpretation |
| U038 | Hutchinson Commons | Existing Highlight retained | — | Protected against 26.10.18.11 |
| U039 | Snell-Hitchcock Halls | snell | 3 / 11.3 m | source-specific silhouette correction |
| U040 | 5706 South Woodlawn Avenue | house | 3 / 9.6 m | conservative mapped exterior interpretation |
| U041 | Hunnewell House | house | 3 / 9.6 m | conservative mapped exterior interpretation |
| U042 | Reynolds Club | reynolds | 3 / 12.5 m | conservative mapped exterior interpretation |
| U043 | Kersten Physics Teaching Center | modern_academic | 3 / 14.0 m | conservative mapped exterior interpretation |
| U044 | Center for Care and Discovery | ccd | 10 / 55.0 m | conservative mapped exterior interpretation |
| U045 | Gordon Center for Integrative Science | Existing Highlight retained | — | Protected against 26.10.18.11 |
| U046 | Office of Multicultural Student Affairs | house | 3 / 9.6 m | conservative mapped exterior interpretation |
| U047 | Ryder House | house | 3 / 9.6 m | conservative mapped exterior interpretation |
| U048 | Delta Upsilon House | house | 3 / 9.6 m | conservative mapped exterior interpretation |
| U049 | Newberger Hillel Center | brick_academic | 3 / 10.5 m | conservative mapped exterior interpretation |
| U050 | Erman Biology Center | gothic_lab | 3 / 13.2 m | conservative mapped exterior interpretation |
| U051 | Culver | laboratory | 4 / 16.5 m | conservative mapped exterior interpretation |
| U052 | Concert Office | house | 3 / 9.6 m | conservative mapped exterior interpretation |
| U053 | Institute of Politics | house | 3 / 9.6 m | conservative mapped exterior interpretation |
| U054 | Mandel Hall | great_hall | 1 / 13.2 m | conservative mapped exterior interpretation |
| U055 | 5728 S. Woodlawn | house | 3 / 9.6 m | conservative mapped exterior interpretation |
| U056 | Stevanovich Center for Financial Mathematics | historic_house | 3 / 10.2 m | conservative mapped exterior interpretation |
| U057 | Searle Chemical Laboratory | gothic_lab | 4 / 16.5 m | conservative mapped exterior interpretation |
| U058 | John Crerar Library | Existing Highlight retained | — | Protected against 26.10.18.11 |
| U059 | 5729 South Woodlawn Avenue | house | 2 / 7.2 m | conservative mapped exterior interpretation |
| U060 | Comparative Human Development Building | brick_academic | 4 / 13.8 m | conservative mapped exterior interpretation |
| U061 | Gender/Race Studies Building | house | 3 / 9.6 m | conservative mapped exterior interpretation |
| U062 | Calvert House | house | 3 / 9.6 m | conservative mapped exterior interpretation |
| U063 | NSIT Office | house | 3 / 9.6 m | conservative mapped exterior interpretation |
| U064 | Henry Hinds Laboratory for Geophysical Sciences | retained | 5 / 20.7 m | existing individual massing retained; facade and entrance reviewed |
| U065 | Comer Hospital East Wing | hospital | 6 / 25.5 m | conservative mapped exterior interpretation |
| U066 | Duchossois Center for Advanced Medicine | dcam | 6 / 27.0 m | source-specific silhouette correction |
| U067 | Ryerson Laboratory | ryerson | 4 / 17.2 m | conservative mapped exterior interpretation |
| U068 | Eckhart Hall | gothic_academic | 3 / 13.3 m | conservative mapped exterior interpretation |
| U069 | Kent Chemical Laboratory | kent | 3 / 13.5 m | conservative mapped exterior interpretation |
| U070 | Comer Children's Hospital | comer | 7 / 30.1 m | source-specific silhouette correction |
| U071 | SCRS Building | house | 3 / 9.6 m | conservative mapped exterior interpretation |
| U072 | U of C Nursery School | house | 2 / 7.2 m | conservative mapped exterior interpretation |
| U073 | Saieh Hall Annex | modern_annex | 3 / 12.6 m | conservative mapped exterior interpretation |
| U074 | McGiffert House | brick_academic | 4 / 13.7 m | conservative mapped exterior interpretation |
| U075 | Jones Laboratory | modern_academic | 4 / 16.8 m | conservative mapped exterior interpretation |
| U076 | Alpha Delta Phi House | house | 3 / 9.6 m | conservative mapped exterior interpretation |
| U077 | U of C Nursery School | house | 2 / 7.2 m | conservative mapped exterior interpretation |
| U078 | Cummings Life Sciences Center | retained | 11 / 44.7 m | existing individual massing retained; facade and entrance reviewed |
| U079 | Kovler | laboratory | 2 / 8.4 m | conservative mapped exterior interpretation |
| U080 | Saieh Hall for Economics | Existing Highlight retained | — | Protected against 26.10.18.11 |
| U081 | Frederick C. Robie House | Existing Highlight retained | — | Protected against 26.10.18.11 |
| U082 | American School | brick_academic | 4 / 14.5 m | conservative mapped exterior interpretation |
| U083 | University Bookstore | bookstore | 3 / 10.8 m | conservative mapped exterior interpretation |
| U084 | Edward H. Levi Hall | retained | 6 / 25.0 m | existing individual massing retained; facade and entrance reviewed |
| U085 | Frank R. Lillie House | house | 3 / 9.6 m | conservative mapped exterior interpretation |
| U086 | Abbott Hall | hospital | 7 / 26.5 m | conservative mapped exterior interpretation |
| U087 | Bernard A. Mitchell Hospital | hospital | 6 / 26.0 m | conservative mapped exterior interpretation |
| U088 | Institute for the Study of Ancient Cultures | isac | 3 / 12.3 m | conservative mapped exterior interpretation |
| U089 | Wilder House | house | 3 / 9.6 m | conservative mapped exterior interpretation |
| U090 | Gordon Parks Arts Hall | retained | 3 / 13.8 m | existing individual massing retained; facade and entrance reviewed |
| U091 | Surgery Brain | hospital | 6 / 25.5 m | conservative mapped exterior interpretation |
| U092 | Carlson | hospital | 7 / 27.5 m | conservative mapped exterior interpretation |
| U093 | Peck Pavilion | hospital | 7 / 27.5 m | conservative mapped exterior interpretation |
| U094 | Medical Campus Parking Garage A | garage | 4 / 13.2 m | conservative mapped exterior interpretation |
| U095 | Charles M. Harper Center | retained | 4 / 18.2 m | existing individual massing retained; facade and entrance reviewed |
| U096 | MRI | service_lab | 2 / 8.5 m | conservative mapped exterior interpretation |
| U097 | Walker Museum | gothic_academic | 3 / 13.5 m | conservative mapped exterior interpretation |
| U098 | Cobb Hall | cobb | 4 / 15.8 m | conservative mapped exterior interpretation |
| U099 | Belfield Hall | lab_school | 3 / 12.8 m | conservative mapped exterior interpretation |
| U100 | Pick Hall | pick | 4 / 17.2 m | conservative mapped exterior interpretation |
| U101 | Swift Hall | gothic_academic | 4 / 16.0 m | conservative mapped exterior interpretation |
| U102 | Rosenwald Hall | gothic_academic | 4 / 16.4 m | conservative mapped exterior interpretation |
| U103 | Rubloff Intensive Care | hospital | 7 / 28.0 m | conservative mapped exterior interpretation |
| U104 | Sunny Gymnasium | gothic_gym | 1 / 9.6 m | conservative mapped exterior interpretation |
| U105 | Armour | hospital | 5 / 20.5 m | conservative mapped exterior interpretation |
| U106 | Beecher Hall | quad_residence | 3 / 11.8 m | conservative mapped exterior interpretation |
| U107 | Bond Chapel | chapel | 1 / 8.6 m | conservative mapped exterior interpretation |
| U108 | Wyler Children's Hospital | hospital | 6 / 24.7 m | conservative mapped exterior interpretation |
| U109 | Judd Hall | lab_school | 3 / 12.8 m | conservative mapped exterior interpretation |
| U110 | University High School | lab_school | 3 / 12.8 m | conservative mapped exterior interpretation |
| U111 | Laboratory Middle School | lab_school | 3 / 12.8 m | conservative mapped exterior interpretation |
| U112 | Rockefeller Memorial Chapel | Existing Highlight retained | — | Protected against 26.10.18.11 |
| U113 | Franklin McLean Research Institute | hospital | 7 / 27.0 m | conservative mapped exterior interpretation |
| U114 | Gates-Blake Hall | gothic_academic | 3 / 12.8 m | conservative mapped exterior interpretation |
| U115 | Green Hall | quad_residence | 3 / 11.8 m | conservative mapped exterior interpretation |
| U116 | Billings | historic_hospital | 6 / 23.8 m | conservative mapped exterior interpretation |
| U117 | Stuart Hall | gothic_academic | 4 / 15.5 m | conservative mapped exterior interpretation |
| U118 | Haskell Hall | gothic_academic | 3 / 12.7 m | conservative mapped exterior interpretation |
| U119 | Kovler Gymnasium | sports_hall | 1 / 10.0 m | conservative mapped exterior interpretation |
| U120 | Gilman Smith | hospital | 7 / 27.0 m | conservative mapped exterior interpretation |
| U121 | Parking/Materials Management | garage | 4 / 13.2 m | conservative mapped exterior interpretation |
| U122 | Goldblatt Pavilion | hospital_low | 2 / 8.4 m | conservative mapped exterior interpretation |
| U123 | Goldblatt | hospital | 5 / 20.5 m | conservative mapped exterior interpretation |
| U124 | International House | international | 12 / 30.4 m | source-specific silhouette correction |
| U125 | Chicago Lying-In Hospital | historic_hospital | 6 / 23.8 m | conservative mapped exterior interpretation |
| U126 | Ida Noyes Hall | ida_noyes | 3 / 11.7 m | conservative mapped exterior interpretation |
| U127 | Kelly Hall | quad_residence | 3 / 11.8 m | conservative mapped exterior interpretation |
| U128 | Goodspeed Hall | gothic_academic | 3 / 12.6 m | conservative mapped exterior interpretation |
| U129 | UChicago Student Wellness Center | wellness | 1 / 4.8 m | conservative mapped exterior interpretation |
| U130 | UChicago President's Mansion | mansion | 3 / 10.8 m | conservative mapped exterior interpretation |
| U131 | Blaine Hall | lab_school | 3 / 12.8 m | conservative mapped exterior interpretation |
| U132 | Breckinridge House | tudor_residence | 3 / 10.5 m | conservative mapped exterior interpretation |
| U133 | Social Science Research Building | gothic_academic | 5 / 20.3 m | conservative mapped exterior interpretation |
| U134 | Wieboldt Hall | gothic_academic | 4 / 16.2 m | conservative mapped exterior interpretation |
| U135 | Bobs Roberts | hospital | 5 / 20.5 m | conservative mapped exterior interpretation |
| U136 | Harper Memorial Library | Existing Highlight retained | — | Protected against 26.10.18.11 |
| U137 | Classics Building | gothic_academic | 4 / 16.0 m | conservative mapped exterior interpretation |
| U138 | Hicks McElwee | hospital | 7 / 27.0 m | conservative mapped exterior interpretation |
| U139 | Foster Hall | quad_residence | 3 / 11.8 m | conservative mapped exterior interpretation |
| U140 | Chapin Hall | brick_academic | 5 / 17.3 m | conservative mapped exterior interpretation |
| U141 | Toyota Technological Institute | brick_academic | 3 / 11.3 m | conservative mapped exterior interpretation |
| U142 | University Press Building | warehouse | 3 / 12.0 m | conservative mapped exterior interpretation |
| U143 | Rubenstein Forum | Existing Highlight retained | — | Protected against 26.10.18.11 |
| U144 | Erna Heller Hall | brick_academic | 4 / 14.5 m | conservative mapped exterior interpretation |
| U145 | Chicago Theological Seminary | retained | 4 / 17.2 m | existing individual massing retained; facade and entrance reviewed |
| U146 | Taft House | house | 2 / 7.0 m | conservative mapped exterior interpretation |
| U147 | Campus ancillary building 663674229 | daycare | 2 / 7.5 m | conservative mapped exterior interpretation |
| U148 | Harris School of Public Policy Keller Center | Existing Highlight retained | — | Protected against 26.10.18.11 |
| U149 | Edith Abbott Hall / Crown Family School | Existing Highlight retained | — | Protected against 26.10.18.11 |
| U150 | The Study at the University of Chicago | retained | 14 / 45.5 m | existing individual massing retained; facade and entrance reviewed |
| U151 | Faculty Apartments | apartment | 9 / 28.9 m | conservative mapped exterior interpretation |
| U152 | 1155 East 60th Street | modern_academic | 4 / 15.3 m | conservative mapped exterior interpretation |
| U153 | Midway Studios | studios | 2 / 6.8 m | conservative mapped exterior interpretation |
| U154 | Burton-Judson Courts | burton | 6 / 15.8 m | source-specific silhouette correction |
| U155 | Logan Center for the Arts | Existing Highlight retained | — | Protected against 26.10.18.11 |
| U156 | Faculty Apartments | house | 2 / 7.0 m | conservative mapped exterior interpretation |
| U157 | Laird Bell Law Quadrangle | Existing Highlight retained | — | Protected against 26.10.18.11 |
| U158 | Midway Residence Hall | apartment | 8 / 25.6 m | conservative mapped exterior interpretation |
| U159 | Faculty Apartments | apartment | 3 / 9.9 m | conservative mapped exterior interpretation |
| U160 | South Campus Chiller Plant | retained | 2 / 13.5 m | existing individual massing retained; facade and entrance reviewed |
| U161 | Edelstone Center | brick_academic | 2 / 8.5 m | conservative mapped exterior interpretation |
| U162 | 6041 South Blackstone Avenue | house | 1 / 3.6 m | conservative mapped exterior interpretation |
| U163 | Kimbark South Parking Garage | garage | 4 / 13.2 m | conservative mapped exterior interpretation |
| U164 | 6045 Kenwood Building | brick_academic | 5 / 17.5 m | conservative mapped exterior interpretation |
| U165 | 6054 S. Drexel / Campus South Parking | garage_office | 4 / 16.7 m | conservative mapped exterior interpretation |
| U166 | Woodlawn Residential & Dining Commons | Existing Highlight retained | — | Protected against 26.10.18.11 |
| U167 | Center for Research Libraries | archive | 3 / 12.3 m | conservative mapped exterior interpretation |
| U168 | Renee Granville-Grossman Residential Commons | grossman | 9 / 20.4 m | source-specific silhouette correction |
| U169 | University of Chicago Steam Plant | steam_plant | 5 / 20.6 m | source-specific silhouette correction |
| U170 | 6044-6052 South Ingleside Avenue | apartment | 3 / 10.2 m | conservative mapped exterior interpretation |
| U171 | Woodlawn Social Services Center | service | 1 / 4.8 m | conservative mapped exterior interpretation |
| U172 | Steam Plant Auxiliary Building | service | 1 / 4.6 m | conservative mapped exterior interpretation |
| U173 | 6051-6057 South Drexel Avenue | apartment | 3 / 10.2 m | conservative mapped exterior interpretation |
| U174 | 6054-6056 South Ingleside Avenue | house | 3 / 9.6 m | conservative mapped exterior interpretation |
| U175 | 920-922 East 61st Street | house | 3 / 9.6 m | conservative mapped exterior interpretation |
| U176 | 924-926 East 61st Street | house | 3 / 9.6 m | conservative mapped exterior interpretation |
| U177 | 928 East 61st Street | house | 1 / 3.6 m | conservative mapped exterior interpretation |

The medical-side rows above are superseded where applicable by [Medical exterior optimization](MEDICAL_EXTERIOR_OPTIMIZATION.md) and the per-building medical source catalog.

Crerar and Harper were explicitly reworked at the user request in release 26.10.18.15; the other 17 Highlight mesh sequences remain protected against 26.10.18.11. The Science Quadrangle follow-up also corrects Kersten, Searle, Hinds and Jones; see [Science Quadrangle and libraries](SCIENCE_QUADRANGLE_AND_LIBRARIES.md).
