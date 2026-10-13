from urllib.parse import urlsplit
"""Validate generated search metadata, static content and referenced local assets."""
from pathlib import Path
from html.parser import HTMLParser
import json,re,xml.etree.ElementTree as ET

root=Path(__file__).resolve().parents[1]
class Page(HTMLParser):
 def __init__(self):
  super().__init__();self.tags=[];self.scripts={};self.current=None
 def handle_starttag(self,tag,attrs):
  attrs=dict(attrs);self.tags.append((tag,attrs))
  if tag=='script' and attrs.get('id'):self.current=attrs['id'];self.scripts[self.current]=''
 def handle_endtag(self,tag):
  if tag=='script':self.current=None
 def handle_data(self,text):
  if self.current:self.scripts[self.current]+=text

html=(root/'index.html').read_text();page=Page();page.feed(html)
config=json.loads((root/'site.config.json').read_text());url=config['url']
assert len(html.encode())<1_000_000, 'Keep model payloads out of crawlable HTML'
assert not re.search(r'__[A-Z_]+__',html), 'Unfilled template placeholder'
meta={a.get('name',a.get('property')):a.get('content') for t,a in page.tags if t=='meta'}
assert meta['description']==config['description']
assert meta['og:title']==meta['twitter:title']==config['title']
assert meta['og:description']==meta['twitter:description']==config['description']
assert meta['og:url']==url
assert meta['og:image']==meta['twitter:image']==url+'output/campus_aerial.png'
assert meta['og:image:alt']==meta['twitter:image:alt']==config['imageAlt']
assert meta['robots'].startswith('index, follow')
assert [a['href'] for t,a in page.tags if t=='link' and a.get('rel')=='canonical']==[url]
assert not any('hreflang' in a for _,a in page.tags), 'One URL has no separate language alternates'
assert len([a for t,a in page.tags if t=='h1'])==1
assert '<title>'+config['title']+'</title>' in html
payload=json.loads(page.scripts['campus-data'])
assert 'model' not in payload and payload['modelUrl']=='output/UChicago_HydePark.3ds'
assert len(payload['records'])==177
translations=json.loads((root/'sources/building_names_zh.json').read_text())
assert {r['code'] for r in translations}=={r['code'] for r in payload['records']}
for r in payload['records']:
 assert re.search(r'[\u4e00-\u9fff]',r['name_zh']) and re.search(r'[\u4e00-\u9fff]',r['short_zh'])
 assert '四合院' not in r['name_zh'] and '法学组团' not in r['name_zh']
law=next(r for r in payload['records'] if r['name']=='Laird Bell Law Quadrangle')
assert law['name_zh']=='莱尔德·贝尔法学院庭院' and law['short_zh']=='法学院庭院'
static_codes=[a['data-building-name'] for _,a in page.tags if 'data-building-name' in a]
assert set(static_codes)=={r['code'] for r in payload['records']}
assert len(static_codes)==177
assert "Architectural landmarks" not in html
assert "Project files &amp; source documentation" not in html
assert "Download Rhino model" in html and "Download 3DS" in html
assert "campus-about" not in html and "About this campus model" not in html
assert '<noscript>' in html
for tag,a in page.tags:
 for attr in ('src','href'):
  path=a.get(attr,'')
  if path and not path.startswith(('https:','http:','data:','#')):
   assert (root/urlsplit(path).path).is_file(), f'Missing local resource: {path}'
assert (root/'assets/fonts/Manrope.ttf').is_file()
assert (root/payload['offlineModelScript']).is_file()
graph=json.loads(page.scripts['campus-schema'])['@graph']
assert {node['@type'] for node in graph}=={'WebSite','WebPage','3DModel'}
assert len({node['@id'] for node in graph})==len(graph)
model=next(n for n in graph if n['@type']=='3DModel')
assert model['contentUrl']==url+payload['modelUrl']
assert next(n for n in graph if n['@type']=='WebPage')['mainEntity']['@id']==model['@id']
assert (root/'CNAME').read_text().strip()==config['domain']
assert 'Sitemap: '+url+'sitemap.xml' in (root/'robots.txt').read_text()
sitemap=ET.parse(root/'sitemap.xml');ns={'s':'http://www.sitemaps.org/schemas/sitemap/0.9'}
assert [e.text for e in sitemap.findall('s:url/s:loc',ns)]==[url]
offline=(root/'output/UChicago_Campus_Offline.html').read_text()
assert not re.search(r'<script[^>]+src=',offline)
assert 'data:font/ttf;base64,' in offline and 'data:image/png;base64,' in offline
assert '<meta name="robots" content="noindex, follow">' in offline
assert '芝加哥大学 · 三维校区' in (root/'scripts/viewer.js').read_text()
print(f'SEO checks passed: {len(html.encode()):,} bytes; 177 buildings; metadata, schema, sitemap and offline edition.')

assert "viewer.bundle.js?v=" in html, "Viewer updates must invalidate the browser cache"
