"""Build a crawlable homepage and a separate self-contained offline edition."""
import pathlib,json,base64,re
root=pathlib.Path(__file__).resolve().parents[1];out=root/'output'
records=json.loads((out/'buildings.json').read_text())
translations={r['code']:r for r in json.loads((root/'sources/building_names_zh.json').read_text())}
assert set(translations)=={r['code'] for r in records}, 'Chinese name coverage must match mapped buildings'
short={150457349: 'Rockefeller Chapel', 156128082: 'Harper Memorial', 1228219576: 'Mitchell Tower', 159093828: 'Mansueto Library', 194224828: 'Regenstein Library', 125667497: 'Robie House', 152422729: 'Logan Center', 441025431: 'Rubenstein Forum', 10657061: 'Campus North', 11687839: 'Woodlawn Commons', 152586235: 'Ratner Athletics', 387213841: 'Eckhardt Center', 143926554: 'Keller Center', 143926548: 'Edith Abbott Hall', 152422458: 'Law Quadrangle', 152284260: 'Crerar Library', 143457513: 'Saieh Hall', 142870150: 'Gordon Center', 157655069: 'Hutchinson Commons'}
notes={
142771603:'Ten-story hospital body using the architect’s 5.5 m floor module, with a setback mechanical zone reaching the contractor’s published 245 ft / 74.676 m peak. Local roof partitions and facade openings are approximate.',
150457349:'Separate carillon tower, nave, lower aisles, steep roofs and buttresses. The tower peak is published at 207 ft / 63.0936 m. Aisle heights, roof slopes, openings and decoration are approximate.',1228219576:'Tower widths use the historical official 31 × 35 ft dimensions. Corner turrets reach the published 127 ft 3 in / 38.7858 m. Belfry openings and crenellations are schematic.',156128082:'Two Gothic end towers use the historical published 135 ft / 41.148 m peak. The central reading hall, roof and turret details are approximate.',159093828:'Ellipsoidal glazed shell, steel grid at approximately 6 ft centers parallel to the ellipse axes, and an entry connector. The published dome peak is 35 ft / 10.668 m. Dome axes follow the public footprint; whole-building 240 × 120 ft dimensions are not assumed to be the exact glass boundary.',152422729:'Southwest limestone tower at the published 170 ft / 51.816 m height, lower studios, rooflights and large glass openings. Tower subdivisions and lower roof levels are approximate.',441025431:'Two-level base and staggered meeting-room tower volumes. Peak height follows the completed 52 m project case study. Individual levels, rotation and facade modules are approximate.',10657061:'Three white residential bars and open courtyards. Published floor counts inform estimated 50.3 / 37.5 / 18.5 m volumes; facade panels and height partitions are approximate.',11687839:'The 2018 public planning drawings give Block W at 184 ft / 56.0832 m and Blocks N/E/S at 94 ft / 28.6512 m. These are planning dimensions, not an as-built survey. Local partitions and facade detailing are approximate.',125667497:'Horizontal brick walls, low-pitched projecting roofs, upper bedrooms and central chimney. Height and eave overhangs are approximate; this is not a reconstruction from the complete HABS survey.',152586235:'Low sports halls, five external masts and cable supports. The current athletics page reports 100 ft mast peaks; the opening report also gives 125 ft mast lengths. Roof heights and cable geometry remain approximate.',152422458:'Higher six-floor law library separated from lower teaching wings, with approximate folded curtain walls and a reflecting pool. Exterior heights are estimated.',152284260:'Upper-floor overhang follows the published 11 ft / 3.3528 m description. Three above-ground levels and rooflights are simplified; total 15 m height is estimated.',387213841:'Glazed research blocks and a partial mechanical penthouse. Overall 117 ft / 35.6616 m height is published by the structural engineer. Mechanical-room footprint and curtain-wall modules are approximate.',194224828:'Mapped slipped segments, projecting bays and deep facade recesses are retained. Five above-ground floors plus a mechanical penthouse. Total 26.7 m height and penthouse footprint are estimated.',143926554:'Three-level colonnaded body with a setback fourth-floor sky suite, planted roof and solar panels. Overall 16.4 m height, columns and canopy are approximate.',143926548:'Mies van der Rohe horizontal brick, steel and glass building. Window bands and black steel perimeter are simplified; 9 m height is estimated.',143457513:'Former chapel body, pitched roofs, an entrance tower and a modern annex. Tower positions and roof/eave heights are approximate.',142870150:'Limestone and glass science blocks around the mapped Science Quadrangle. Five academic floors are documented; mechanical levels, facade bays and overall height are estimated.',157655069:'Low Gothic hall in the historic Tower Group, with a steep roof and pointed window bays. The Mitchell Tower is a separate layer. Exterior heights and roof pitch are estimated.'}
notes_zh=json.loads((root/'sources/model_notes_zh.json').read_text())
for r in records:
 tr=translations[r['code']]
 assert tr['name']==r['name'], 'Translation record is attached to the wrong building'
 r['name_zh']=tr['name_zh'];r['short_zh']=tr['short_zh'];r['aliases_zh']=tr['aliases_zh'];r['short']=short.get(r['osm_id'],r['name'])
 r['partition']=notes_zh.get(str(r['osm_id']),('模型依据公开地图轮廓表示建筑体块，并简化屋顶、檐口和连续窗带；窗位、层高及装饰为示意。' if r['partition'].startswith('公开平面轮廓') else r['partition']))
 r['basis']=r['basis'].replace('OSM building:levels；层高估算','采用 OpenStreetMap 的 building:levels 楼层记录，层高为估算。').replace('学校/项目资料层数；层高与局部标高估算','层数依据学校或项目公开资料，层高及局部标高为估算。').replace('未取得可靠层数/高度；按建筑功能与外形估算','未取得可靠的层数或高度资料，依据建筑用途与外形估算。').replace('公开资料最高高度；主体檐口、屋顶分区与立面细节为近似','最高点依据公开资料，檐口、屋顶分区及立面细节为近似表达。').replace('芝加哥市 Building Footprints stories','采用芝加哥市建筑轮廓数据的 stories 楼层记录').replace('；层高估算','，层高为估算。').replace('学校体育部桅杆峰值100 ft；另有125 ft构件报道；屋面高度估算','桅杆峰顶采用学校体育部介绍的100英尺；另有报道提及125英尺的桅杆构件。屋面高度为估算。').replace('市政府PD43公开2018规划图：西楼184 ft，东/北/南楼94 ft；非竣工测量','采用芝加哥市PD43的2018年公开规划图：西楼184英尺，东、北、南楼94英尺；这些是规划尺寸，未经过竣工实测。').replace('公开地图平面及Frank Lloyd Wright Trust外形；高度10.5m估算','平面采用公开地图，外形参考弗兰克·劳埃德·赖特信托的资料；高度10.5米为估算。')
 r['partition_en']=notes.get(r['osm_id'],'Georeferenced building footprint with simplified roof, cornice and repeated window bays. Courtyard voids are retained where mapped. Local heights and facade openings are approximate.')
 if r['height_status']=='published':r['basis_en']='Published maximum height from university or project sources; local roof and facade dimensions remain approximate.'
 elif r['height_status']=='planning':r['basis_en']='2018 Chicago PD43 planning drawings, pages 211 and 223: Block W 184 ft; Blocks N/E/S 94 ft. Not an as-built survey.'
 else:r['basis_en']=f"Estimated exterior height. Floor count used: {r['levels']:g}. " + ('Municipal stories record; assumed floor heights.' if '芝加哥市' in r['basis'] else 'Published/OSM floor counts or a functional massing estimate; local floor heights are assumed.')
recordsfile=out/'viewer_records.json';recordsfile.write_text(json.dumps(records,ensure_ascii=False,indent=2))

# Keep crawlable HTML small; the same renderer also powers a portable single-file edition.
from html import escape
from datetime import date
import hashlib

config=json.loads((root/'site.config.json').read_text())
site=config['url']
assert site == f"https://{config['domain']}/", 'Use one HTTPS root URL for every public reference.'
seo={'en':{k:config[k] for k in ('title','description','imageAlt')},'zh':config['zh']}
model=(out/'UChicago_HydePark.3ds').read_bytes()
base64model=base64.b64encode(model).decode()
preview='data:image/png;base64,'+base64.b64encode((out/'campus_aerial.png').read_bytes()).decode()
data={'modelByteLength':len(model),'modelTransferBytes':len(model),'layers':json.loads((out/'layer_map.json').read_text()),'palette':json.loads((out/'palette.json').read_text()),'records':records,'preview':'output/campus_aerial.png','modelUrl':'output/UChicago_HydePark.3ds','offlineModelScript':'assets/model-local.js','seo':seo}
schema={'@context':'https://schema.org','@graph':[
 {'@type':'WebSite','@id':site+'#website','url':site,'name':'UChicago Campus 3D Model','inLanguage':['en','zh-CN'],'sameAs':'https://github.com/sd800/uchicago-3d-arch','image':site+'assets/brand/phoenix-map.png'},
 {'@type':'WebPage','@id':site+'#webpage','url':site,'name':config['title'],'description':config['description'],'inLanguage':['en','zh-CN'],'isPartOf':{'@id':site+'#website'},'mainEntity':{'@id':site+'#model'},'primaryImageOfPage':{'@type':'ImageObject','url':site+'output/campus_aerial.png','width':2400,'height':1850}},
 {'@type':'3DModel','@id':site+'#model','name':'University of Chicago Hyde Park exterior campus model','description':'Independent public-source exterior model with 177 mapped buildings, individual building layers and a separate landscape layer. Model units are meters; unpublished heights and exterior details are estimates.','contentUrl':site+'output/UChicago_HydePark.3ds','encodingFormat':'application/x-3ds','contentSize':str(len(model))+' bytes','sha256':hashlib.sha256(model).hexdigest(),'thumbnailUrl':site+'output/campus_aerial.png','contentLocation':{'@type':'Place','name':'University of Chicago Hyde Park campus','address':{'@type':'PostalAddress','addressLocality':'Chicago','addressRegion':'IL','addressCountry':'US'}},'isBasedOn':['https://maps.uchicago.edu/','https://architecture.uchicago.edu/','https://data.cityofchicago.org/Buildings/Building-Footprints/syp8-uezg','https://www.openstreetmap.org/copyright']}
]}
def script_json(value):
 return json.dumps(value,ensure_ascii=False,separators=(',',':')).replace('</',r'<\/')

template=(root/'scripts/viewer.template.html').read_text()
bundle=(root/'tmp/viewer.bundle.js').read_text()
initial=[]
for r in records:
 code=escape(r['code'],quote=True);name=escape(r['name'])
 initial.append(f'<div class="row"><span class="building-name" data-building-name="{code}">{name}</span><span class="building-meta">{code} · {r["height"]:.2f} m</span></div>')

license=((root/'THIRD_PARTY_NOTICES.md').read_text()+'\n'+(root/'assets/fonts/OFL.txt').read_text()).replace('--','- -')
template=template.replace('</head>','<!--\n'+license+'\n-->\n</head>')
for token,value in {'__SITE_URL__':site,'__SEO_TITLE__':escape(config['title'],quote=True),'__SEO_DESCRIPTION__':escape(config['description'],quote=True),'__IMAGE_ALT__':escape(config['imageAlt'],quote=True),'__STRUCTURED_DATA__':script_json(schema),'__INITIAL_BUILDINGS__':''.join(initial),'__INITIAL_COUNT__':str(len(records))}.items():
 template=template.replace(token,value)

def edition(payload,font_url,image_url,icons,logo,script,robots):
 text=template
 for token,value in {'__CAMPUS_DATA__':script_json(payload),'__TITLE_FONT_URL__':font_url,'__PREVIEW_IMAGE__':image_url,'__FAVICON__':icons['32'],'__FAVICON_16__':icons['16'],'__APPLE_ICON__':icons['apple'],'__LOGO__':logo,'__VIEWER_SCRIPT__':script,'__ROBOTS__':robots}.items():
  text=text.replace(token,value)
 assert not any(token in text for token in ('__CAMPUS_DATA__','__TITLE_FONT_URL__','__PREVIEW_IMAGE__','__FAVICON__','__FAVICON_16__','__APPLE_ICON__','__LOGO__','__VIEWER_SCRIPT__','__ROBOTS__')), 'Unfilled template placeholder'
 return text

assets=root/'assets'
(assets/'viewer.bundle.js').write_text(bundle)
# Classic scripts work beside index.html under file:// without fetching or CORS.
(assets/'model-local.js').write_text('window.__UCHICAGO_MODEL_BASE64__='+json.dumps(base64model)+';\n')
html=edition(data,'assets/fonts/Manrope.ttf','output/campus_aerial.png',{'32':'assets/favicon-32.png','16':'assets/favicon-16.png','apple':'assets/apple-touch-icon.png'},'assets/brand/phoenix-map-192.png','<script defer src="assets/viewer.bundle.js?v='+hashlib.sha256(bundle.encode()).hexdigest()[:12]+'"></script>','index, follow, max-image-preview:large')
(root/'index.html').write_text(html,encoding='utf-8')
standalone={**data,'model':base64model,'preview':preview}
def png_data(path):return 'data:image/png;base64,'+base64.b64encode(path.read_bytes()).decode()
icons={'32':png_data(assets/'favicon-32.png'),'16':png_data(assets/'favicon-16.png'),'apple':png_data(assets/'apple-touch-icon.png')}
offline=edition(standalone,'data:font/ttf;base64,'+base64.b64encode((assets/'fonts/Manrope.ttf').read_bytes()).decode(),preview,icons,png_data(assets/'brand/phoenix-map-192.png'),'<script>'+bundle.replace('</script',r'<\/script')+'</script>','noindex, follow')
assert not re.search(r'<script[^>]+src=',offline)
(out/'UChicago_Campus_Offline.html').write_text(offline,encoding='utf-8')
(root/'CNAME').write_text(config['domain']+'\n')
(root/'robots.txt').write_text('User-agent: *\nAllow: /\n\nSitemap: '+site+'sitemap.xml\n')
(root/'sitemap.xml').write_text('<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n  <url><loc>'+site+'</loc><lastmod>'+date.today().isoformat()+'</lastmod></url>\n</urlset>\n')
print('SEO index.html:',len(html.encode()),'bytes;',len(records),'static building names;')
print('Single-file offline HTML:',len(offline.encode()),'bytes')
