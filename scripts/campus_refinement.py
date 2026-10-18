"""Hyde Park campus-wide exterior refinement.

Mapped outlines, courtyard voids and individual heights remain authoritative.
Selected modern masses use university architecture profiles; joinery dimensions
and secondary landscape furniture are approximate public-source interpretations.
"""
import numpy as np
from shapely.geometry import Polygon,Point,LineString,box
from shapely.ops import unary_union,nearest_points
from shapely import affinity
import trimesh
BASE='https://architecture.uchicago.edu/locations/'
PROFILES={
 153266965:('palevsky','max_palevsky_residential_commons/'),153090078:('palevsky','max_palevsky_residential_commons/'),152969810:('palevsky','max_palevsky_residential_commons/'),
 143525608:('museum','cochrane_woods_art_center/'),152586233:('museum','cochrane_woods_art_center/'),
 151173253:('fieldhouse',''),152586234:('theatre',''),152284265:('levi','levihall/'),
 143527369:('laboratory','knapp_center_for_biomedical_discovery/'),89537392:('cummings','cummings_life_science_center/'),88865426:('hinds','henry_hinds_laboratory_for_geophysical_sciences/'),
 150456352:('booth',''),1953426:('international','international_house/'),151173255:('chapel','bond_chapel/'),
 150457341:('historic_hall','ida_noyes_hall/'),1968186:('courts',''),153539618:('historic_hall',''),157655071:('great_hall',''),
 145400410:('plant','west_campus_combined_utility_plant/'),533422554:('plant','south_campus_chiller_plant/'),
 860807638:('hotel',''),545084805:('arts','gordon_parks_arts_hall/'),144636084:('seminary','the_chicago_theological_seminary/'),
}

def oriented(ctx,c,u,n,width,depth,height,z):
 m=trimesh.creation.box(extents=(width,depth,height));t=np.eye(4);t[:2,0]=u;t[:2,1]=n;t[:3,3]=[*c,z+height/2];m.apply_transform(t);return m

def rebuild(ident,p,h,levels,ctx):
 if ident not in PROFILES:return None
 kind,reference=PROFILES[ident];a,b,c,d=p.bounds;cx,cy=p.centroid.coords[0];ms=ctx.ms
 def cap(g,z,mat='Metal'):
  for q in ctx.polygons(g):ms[mat].append(ctx.extrusion(q,z,.18))
 def band(g,z,mat='LightStone',w=.14):
  for q in ctx.polygons(g.boundary.buffer(w,join_style=2).intersection(g.buffer(.03))):ms[mat].append(ctx.extrusion(q,z,.16))
 features=[]
 if kind=='palevsky':
  h=13.4;levels=4;ctx.body(p,0,h,'PalevskyBrick',lev=4,arch=False);cap(p,h-.18,'PalevskyRoof');band(p,h-.48,'PalevskyPurple',.28)
  features=['Bright red-orange brick residence wings','Four-storey mapped courtyard massing','Purple parapet edges and deep rectangular entrance accents','Courtyard voids retained']
 elif kind=='museum':
  high=p.intersection(box(a,b,c,b+(d-b)*.38));rest=p.difference(high);h=9.8;levels=2
  ctx.body(rest,0,5.8,'Limestone',windows=False);ctx.body(high,0,h,'Limestone',lev=2,arch=False);cap(rest,5.7);cap(high,h-.1)
  # Flat stone wall ranges and a glazed garden-facing lobby.
  side=LineString([(a,b),(c,b)]).buffer(2,cap_style=2).intersection(p)
  ctx.body(side,0,3.6,'DarkGlass',lev=1,arch=False,cont=True);band(p,5.5)
  features=['Separate low gallery/teaching ranges','Limestone panel walls','Glazed garden-facing entrance range','Flat inset roofs around the mapped garden']
 elif kind=='fieldhouse':
  h=16.5;levels=2;ctx.body(p,0,11.4,'Brick',lev=2,arch=False);ms['Metal'].extend(ctx.pitched(p,11.4,5.1,'x'))
  band(p,3.7);band(p,10.9);features=['Long brick sports hall','Continuous pitched metal roof','Tall upper sports-hall bays','Grounded entrance apron']
 elif kind=='theatre':
  h=9.6;levels=1;ctx.body(p,0,6.8,'Brick',lev=1,arch=False);cap(p,6.8)
  fly=p.intersection(box(a+(c-a)*.4,b+(d-b)*.4,c-2,d-2));ctx.body(fly,6.8,2.8,'Frame',windows=False);cap(fly,h-.1)
  features=['Low brick theatre body','Separate auditorium roof volume','Recessed glazed lobby entrance']
 elif kind=='levi':
  h=25.;levels=6;ctx.body(p,0,h,'Limestone',lev=6,arch=False);cap(p,h-.1,'Metal')
  for z in [4.2,8.3,12.4,16.5,20.6,24.6]:band(p,z,'LightStone',.10)
  features=['Restrained modern limestone office block','Six regular window storeys','Subtle floor courses and recessed flat roof','No invented Gothic roof or pinnacles']
 elif kind=='cummings':
  # University description documents eleven storeys and forty external vents.
  # Continuous attached shafts, not detached rods or arbitrary rooftop boxes.
  levels=11;h=max(h,39.6);walltop=h-1.7
  core=p.buffer(-.75,join_style=2);ctx.body(core,0,walltop,'Concrete',lev=11,arch=False);cap(core,walltop)
  rect=box(a+6.7,b+.8,c-.8,d-.8);coords=np.asarray(rect.exterior.coords)
  for aa,bb in zip(coords[:-1],coords[1:]):
   u=(bb-aa)/np.linalg.norm(bb-aa);n=np.array([u[1],-u[0]])
   for j in range(10):
    center=aa+(bb-aa)*((j+.5)/10)
    shaft=Polygon([center-u*.72-n*.85,center+u*.72-n*.85,center+u*.72+n*.85,center-u*.72+n*.85])
    ctx.body(shaft,0,h,'Brick',windows=False);cap(shaft,h-.18,'LightStone')
    ms['Frame'].append(oriented(ctx,center+n*.88,u,n,1.05,.12,.72,h-1.2))
  features=['Eleven-storey concrete laboratory body','Forty attached, ground-to-roof brick-covered exhaust towers','Raised vent heads and inset flat roof','Secondary shaft widths and spacing are approximate']
 elif kind=='hinds':
  levels=max(1,round(levels));ctx.body(p,0,h-.6,'Concrete',lev=levels,arch=False);cap(p,h-.6,'Metal')
  for side in [a,c-5.5]:
   for yy in np.linspace(b+6,d-8,4):
    tower=p.intersection(box(side,yy,side+5.5,yy+3.8))
    ctx.body(tower,0,h,'Brick',windows=False);cap(tower,h-.18,'Brick')
  for z in np.linspace(.4,h-1,max(2,levels+1)):band(p,float(z),'Concrete',.22)
  features=['Flat grey concrete laboratory slabs','Eight attached red-brick vertical service accents following the mapped side bays','Inset roof edges and separate slab courses','Tower widths and local slab levels are exterior estimates']
 elif kind=='laboratory':
  levels=10;low=min(h*.2,7.5);inner=p.buffer(-1.15,join_style=2);ctx.body(p,0,low,'Limestone',lev=2,arch=False)
  ctx.body(inner,low,h-low,'DarkGlass',lev=8,arch=False,cont=True);cap(inner,h-.12)
  for z in np.linspace(low,h-.45,9):band(inner,float(z),'LightStone',.14)
  features=['Part-limestone two-storey base','Eight upper glass laboratory storeys','Continuous glazing and horizontal slab edges','Ten-storey documented building rhythm']
 elif kind=='booth':
  h=18.2;levels=4;ctx.body(p,0,15.0,'Limestone',lev=3,arch=False);cap(p,14.9)
  upper=p.buffer(-7,join_style=2);ctx.body(upper,15,3.2,'DarkGlass',lev=1,arch=False,cont=True);cap(upper,h-.12,'Metal')
  features=['Low limestone teaching wings and mapped courtyards','Set-back glazed upper range','Flat roofs and exposed stone bay rhythm','Grounded entrances rather than a solid roof lid']
 elif kind=='international':
  h=40.;levels=12;ctx.body(p,0,30.4,'Brick',lev=9,arch=True);cap(p,30.3,'Slate')
  tp=p.representative_point();tower=p.intersection(box(tp.x-8,tp.y-8,tp.x+8,tp.y+8));ctx.body(tower,30.4,9.2,'Brick',lev=3,arch=True);cap(tower,39.6,'Slate');band(tower,39.4)
  features=['Nine-storey residential wings','Separate three-storey upper tower','Gothic and Art Deco stone courses','Mapped courtyard retained open']
 elif kind=='chapel':
  h=13.1;levels=1;ctx.body(p,0,8.6,'Limestone',lev=1,arch=True);ms['Slate'].extend(ctx.pitched(p,8.6,4.5,'y'));band(p,8.4)
  features=['Single chapel nave','Steep slate roof','Tall lancet windows and stepped stone buttresses','Connection to Swift Hall retained from mapped connector']
 elif kind in ['historic_hall','great_hall','courts']:
  levels=2 if kind=='great_hall'else min(levels,5 if kind=='courts'else 3);eave=max(8,levels*3.6);h=eave+4.8
  ctx.body(p,0,eave,'Limestone',lev=levels,arch=True);ms['Slate'].extend(ctx.pitched(p,eave,4.8));band(p,eave-.3)
  features=['Separate Gothic wall/eaves/roof heights','Lancet/tall hall window rhythm','Stone window surrounds and entry portal','Mapped courtyards and setbacks retained']
 elif kind=='plant':
  h=13.5;levels=2;ctx.body(p,0,11.7,'Metal',lev=2,arch=False,cont=True);cap(p,11.7,'Metal')
  # Large screen housings follow a continuous service strip, not random boxes.
  strip=p.intersection(box(a+3,b+3,c-3,min(d-3,b+9)))
  if not strip.is_empty:ctx.body(strip,11.7,1.8,'Frame',windows=False);cap(strip,13.5)
  features=['Metal and glazed utility envelope','Continuous screened plant range','Low integrated service roof']
 elif kind in ['hotel','arts','seminary']:
  h=min(h,49.5)if kind=='hotel'else(13.8 if kind=='arts'else 17.2);levels=14 if kind=='hotel'else 4
  base=4.4;ctx.body(p,0,base,'DarkGlass',lev=1,arch=False,cont=True);upper=p.buffer(-.3,join_style=2);ctx.body(upper,base,h-base,'Brick'if kind=='seminary'else'LightStone',lev=levels-1,arch=False);cap(upper,h-.12,'Metal')
  features=['Separate glazed ground-floor frontage','Regular upper teaching/residential bays','Thin roof edge and recessed entrances']
 return {'profile':kind,'height':h,'levels':levels,'features':features,'reference':BASE+reference if reference else'https://maps.uchicago.edu/','approximation':'Mapped footprint, documented architectural character; secondary dimensions and partition lines are exterior estimates.'}

def finish(p,h,levels,gothic,ctx,kind=None):
 """Linked construction joinery for every ordinary building, bounded in cost."""
 ms=ctx.ms;trim='LightStone'if gothic else'Metal';eave=h-min(5.5,h*.22)if gothic and kind not in ['international']else h
 if kind=='chapel':eave=8.6
 if kind in ['historic_hall','great_hall','courts']:eave=h-4.8
 stats={'window_surrounds':0,'entrances':0,'buttresses':0,'courses':0}
 # Refine the actual facade ranges emitted by each individual body builder.
 # Multi-height wings must not receive full-height floating trim or windows.
 for q,zbase,wallheight,storeys,arched,continuous in ctx.construction_facades:
  for ring in [q.exterior,*q.interiors]:
   cc=np.asarray(ring.coords)
   for a,b in zip(cc[:-1],cc[1:]):
    v=b-a;length=np.linalg.norm(v)
    if length<3.7:continue
    u=v/length;n=np.array([u[1],-u[0]]);count=max(1,int(length/3.7));step=length/count;ww=step-.16 if continuous else min(3.7*.48,2.0)
    for level in range(max(1,int(storeys))):
     z=zbase+(level+.23)*wallheight/max(1,storeys);wh=min(wallheight/max(1,storeys)*.56,8.5 if arched else 2.8)
     if z+wh>zbase+wallheight-.25:continue
     for j in range(count):
      c=a+u*((j+.5)*step)+n*.19;trim='LightStone'if arched else'Metal'
      for dz in [0,wh*.73 if arched else wh]:ms[trim].append(oriented(ctx,c,u,n,ww+.24,.13,.13,z+dz-.065))
      for dx in [-ww/2-.06,ww/2+.06]:ms[trim].append(oriented(ctx,c+u*dx,u,n,.12,.13,wh*.73 if arched else wh,z))
      stats['window_surrounds']+=1
    if arched and length>12:
     for t in np.arange(2.2,length-1.8,7.4):
      c=a+u*t+n*.24;hh=min(wallheight*.74,10)
      ms['Limestone'].append(oriented(ctx,c,u,n,.7,.65,hh,zbase));ms['LightStone'].append(oriented(ctx,c,u,n,.82,.78,.22,zbase+hh));stats['buttresses']+=1
  for z in [zbase+.27,zbase+wallheight-.28]:
   for ring in ctx.polygons(q.boundary.buffer(.12,join_style=2).intersection(q.buffer(.04))):ms['LightStone'if arched else'Metal'].append(ctx.extrusion(ring,z,.18));stats['courses']+=1
 # Keep the principal Gothic frontage facing the quadrangles, not the sparse
 # Ellis street wall. Other frontages follow their mapped street/campus side.
 target=np.array([630.,830.])if gothic else np.array([p.centroid.x,p.bounds[1]-100])
 candidates=[]
 for a,b in [(a,b)for poly in ctx.polygons(p)for a,b in zip(np.asarray(poly.exterior.coords)[:-1],np.asarray(poly.exterior.coords)[1:])]:
  v=b-a;length=np.linalg.norm(v)
  if length<5:continue
  u=v/length;n=np.array([u[1],-u[0]]);c=(a+b)/2;score=np.dot(n,(target-c)/max(np.linalg.norm(target-c),1));candidates.append((score,length,c,u,n))
 if candidates:
  _,length,c,u,n=max(candidates,key=lambda x:(x[0],min(x[1],20)));width=min(2.6,length*.38);c=c+n*.23
  ms['DarkGlass'].append(oriented(ctx,c,u,n,width,.14,2.6,.18))
  for dx in [-width/2-.13,width/2+.13]:ms['LightStone'if gothic else'Frame'].append(oriented(ctx,c+u*dx,u,n,.24,.3,2.85,.1))
  ms[trim].append(oriented(ctx,c,u,n,width+.5,.3,.23,2.95));ms['Frame'].append(oriented(ctx,c,u,n,.055,.20,2.6,.18));ms['Concrete'].append(oriented(ctx,c+n*.45,u,n,width+.8,1.3,.15,.02))
  stats['entrances']=1
 return stats

def landscape(ctx):
 footprint=ctx.footprints;clear=ctx.roadarea.union(ctx.walkarea).union(footprint);report={'entry_aprons':0,'courtyards':0,'path_edge_length_m':0}
 # Replace undefined pale residual ground with coherent parcel treatments.
 occupied=unary_union([ctx.greenarea,ctx.gardenarea,ctx.roadarea,ctx.walkarea,ctx.kerb,ctx.sports,ctx.trackarea,*ctx.parking,*ctx.water,footprint])
 leftover=ctx.scope.difference(occupied).buffer(0)
 planted=[];hard=[]
 for q in ctx.polygons(leftover):
  if q.area<2:continue
  near=footprint.distance(q.representative_point())
  (hard if near<4.5 or q.area<24 else planted).append(q)
 ctx.env(unary_union(planted),.087,.045,'Grass');ctx.env(unary_union(hard),.075,.04,'Paving')
 # Slightly darker planted margins tie walls to adjacent paths. No new road
 # crossings or parking paint are fabricated here.
 beds=footprint.buffer(1.05,join_style=2).difference(footprint).difference(ctx.roadarea.buffer(.6)).difference(ctx.walkarea.buffer(.35)).intersection(ctx.scope)
 ctx.env(beds,.11,.075,'Garden')
 edge=ctx.walkarea.boundary.buffer(.09,join_style=2).difference(footprint).difference(ctx.roadarea).intersection(ctx.scope)
 ctx.env(edge,.126,.018,'Paving');report['path_edge_length_m']=round(ctx.walkarea.boundary.length,2)
 for f in ctx.buildings:
  p=f['poly'];record=f['record'];cent=p.centroid
  for poly in ctx.polygons(p):
   for ring in poly.interiors:
    court=Polygon(ring);inner=court.buffer(-1.5)
    if inner.is_empty:continue
    border=court.difference(inner).difference(ctx.walkarea);ctx.env(border,.12,.04,'Paving');ctx.env(inner.difference(ctx.walkarea),.10,.065,'Grass');report['courtyards']+=1
  # Existing mapped footpaths reach the footprint; only bridge the final short
  # connection. Long speculative paths through buildings are deliberately absent.
  a,b=nearest_points(p,ctx.walkarea)
  if 0.2<a.distance(b)<5:
   apron=LineString([a,b]).buffer(1.3,cap_style=2).difference(footprint).difference(ctx.roadarea)
   ctx.env(apron,.10,.045,'Paving');report['entry_aprons']+=1
 report['infill_lawn_m2']=round(unary_union(planted).area,2);report['infill_paving_m2']=round(unary_union(hard).area,2)
 return report
