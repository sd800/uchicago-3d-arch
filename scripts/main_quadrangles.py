"""Main Quadrangles: authored exterior sections and courtyard interfaces.

Sources and the source/model feature correspondence are recorded per building
in sources/main_quadrangles_review.json. No source photographs are distributed.
Unpublished dimensions and carving shapes are proportional interpretations.
"""
from pathlib import Path
import json,math
import numpy as np
import trimesh
from shapely.geometry import Polygon,Point,LineString,box
from shapely.ops import unary_union,nearest_points
from science_exteriors import Kit,neighbor as science_neighbor

CAT=json.loads((Path(__file__).resolve().parents[1]/'sources/main_quadrangles_review.json').read_text())
BYID={r['osm_id']:r for r in CAT['buildings']}
IDS=set(BYID)-{1228219576}
STATS={}

def arch(w,h):
 spring=h-w*math.sqrt(3)/2
 # Two intersecting circular arcs; no faceted triangular substitute for a head.
 right=[(w/2-w+w*math.cos(a),spring+w*math.sin(a))for a in np.linspace(0,math.pi/3,10)]
 left=[(w/2+w*math.cos(a),spring+w*math.sin(a))for a in np.linspace(2*math.pi/3,math.pi,10)]
 return Polygon([(-w/2,0),(w/2,0),*right[:-1],(0,h),*left[1:],(-w/2,0)]).buffer(0)

class Quad(Kit):
 def __init__(self,t,ms):super().__init__(t,ms);self.entries=[];self.dormers=0;self.gables=0;self.traceries=0;self.apertures=0
 def pane(self,c,u,n,z,w,h,pointed=False,divisions=2,glass='WindowGlass',offset=.035,tracery=False):
  pr=arch(w,h)if pointed else box(-w/2,0,w/2,h)
  self.profile(pr,c,u,n,z,.065,glass,offset)
  # Two nested masonry orders create actual splayed depth, with every member
  # meeting its sill/head; none project beyond the local supporting eave.
  for depth,width,off in [(.15,.15,offset+.055),(.24,.075,offset+.145)]:
   self.profile(pr.buffer(width,join_style=2).difference(pr.buffer(-.025,join_style=2)),c,u,n,z,depth,'QuadTrim',off)
  for j in range(1,divisions):
   x=w*(j/divisions-.5);self.profile(box(x-.035,0,x+.035,h*.80).intersection(pr),c,u,n,z,.13,'QuadTrim',offset+.17)
  self.profile(box(-w/2,h*.48,w/2,h*.48+.06).intersection(pr),c,u,n,z,.13,'QuadTrim',offset+.17)
  if tracery:
   # Paired sub-lancets and a pierced roundel, bounded by the parent aperture.
   for sign in [-1,1]:
    pp=arch(w*.42,h*.68);from shapely.affinity import translate
    pp=translate(pp,xoff=sign*w*.24,yoff=h*.02)
    self.profile(pp.boundary.buffer(.035).intersection(pr),c,u,n,z,.13,'QuadTrim',offset+.18)
   ring=Point(0,h*.79).buffer(w*.15,quad_segs=12).boundary.buffer(.035)
   self.profile(ring.intersection(pr),c,u,n,z,.14,'QuadTrim',offset+.19);self.traceries+=1
  self.panes+=1
 def portal(self,p,side,eave,width=2.8,height=4.0,fraction=.5,steps=3,pointed=True):
  target=np.asarray({'N':[0,1],'S':[0,-1],'E':[1,0],'W':[-1,0]}[side]);candidates=[]
  for a,b,u,n,ln in self.walls(p):
   if np.dot(n,target)>.9 and ln>width+1:candidates.append((ln,a,b,u,n))
  if not candidates:return
  ln,a,b,u,n=max(candidates,key=lambda e:e[0]);c=a+u*ln*fraction
  zz=.14*steps;pr=arch(width,height)if pointed else box(-width/2,0,width/2,height)
  # Deep, dark actual door leaf plus independently offset stone archivolts.
  self.profile(pr,c,u,n,zz,.10,'DoorWood',.055)
  for inset,dep,off in [(.18,.24,.12),(.38,.16,.32)]:self.profile(pr.buffer(inset,join_style=2).difference(pr.buffer(inset-.10,join_style=2)),c,u,n,zz,dep,'QuadTrim',off)
  self.bar(c+n*.28,u,n,.065,.17,height*.76,zz,'Furniture')
  for z in [zz+.9,zz+height*.50]:
   for sign in [-1,1]:self.bar(c+u*sign*width*.24+n*.29,u,n,width*.30,.09,.055,z,'Furniture')
  for j in range(steps):self.bar(c+n*(.50+j*.38),u,n,width+1.3,.40,.14*(steps-j),0,'Paving')
  self.entries.append({'center':[float(v)for v in c],'normal':n.tolist(),'landing_m':zz,'width_m':width})
 def gable(self,c,u,n,z,w,rise,depth=3.0,window=True):
  triangle=Polygon([(-w/2,-.14),(w/2,-.14),(0,rise)])
  self.profile(triangle,c,u,n,z,.32,'QuadStone',-.08)
  for sign in [-1,1]:
   a=np.array(c)+np.array(u)*sign*w/2;tip=np.array(c)
   self.ms['QuadTrim'].append(self.t.cylinder((*a,z),(*tip,z+rise),.11,6))
  if window and rise>2.0:self.pane(c,u,n,z+.25,min(1.8,w*.34),min(2.1,rise*.56),False,2,offset=.26)
  # Actual gabled roof return slopes down behind the end wall, not a floating
  # triangular panel. It intersects the primary roof along supported valleys.
  u,n,c=map(np.asarray,[u,n,c]);verts=np.array([np.r_[c-u*w/2,z],np.r_[c+u*w/2,z],np.r_[c,z+rise],np.r_[c-u*w/2-n*depth,z],np.r_[c+u*w/2-n*depth,z],np.r_[c-n*depth,z+rise]])
  m=trimesh.Trimesh(verts,[[0,2,1],[3,4,5],[0,3,5],[0,5,2],[2,5,4],[2,4,1],[0,1,4],[0,4,3]],process=False);trimesh.repair.fix_normals(m);self.ms['RoofClay'].append(m);self.gables+=1
 def dormer(self,c,u,n,eave,w=1.7,rise=1.4,depth=2.6):
  # Foot is below the sloping roof at this setback: roof light is attached.
  c=np.asarray(c)-np.asarray(n)*1.2;self.bar(c-np.asarray(n)*depth/2,u,n,w,depth,1.3,eave+.45,'QuadStone')
  self.pane(c,u,n,eave+.65,w*.65,.85,False,2,offset=.035)
  self.gable(c,u,n,eave+1.75,w+.3,rise,depth,False);self.dormers+=1
 def stats(self):
  s=super().stats();s.update({'source_specific_quadrangle':True,'window_surrounds':self.panes,'entrances':len(self.entries),'buttresses':0,'courses':0,'roof_dormers':self.dormers,'projecting_gables':self.gables,'traceried_openings':self.traceries,'true_apertures':self.apertures,'entries':self.entries});return s

def authored_shell(k,p,eave,levels,bay=3.8,pointed_top=False,side=None,front_gables=(),dormers=0,roof='RoofClay',rise=4.0):
 k.solid(p,0,eave,'QuadStone');k.t.roof_shell(p,eave,rise,k.t,roof)
 for z in [.3,eave-.24]:k.band(p,z,.20,'QuadTrim',.18)
 for j in range(1,levels):k.band(p,eave*j/levels-.12,.13,'QuadTrim',.12)
 normals={'N':np.array([0,1]),'S':np.array([0,-1]),'E':np.array([1,0]),'W':np.array([-1,0])};target=normals.get(side)
 faces=list(k.walls(p));main=max([(ln,a,b,u,n)for a,b,u,n,ln in faces if target is not None and np.dot(n,target)>.92],default=None,key=lambda v:v[0])
 for a,b,u,n,ln in faces:
  if ln<3.3:continue
  count=max(1,round(ln/bay));step=ln/count;front=target is not None and np.dot(n,target)>.92
  for j in range(count):
   center=a+u*(j+.5)*step
   for level in range(levels):
    floor=eave/levels;hh=min(8.0 if levels==1 else 3.0,floor*.58);zz=level*floor+.26*floor;point=pointed_top and level==levels-1
    ww=min(step*.60,2.7 if front else 1.75)
    k.pane(center,u,n,zz,ww,hh,point,2 if ww>1.3 else 1,tracery=point and ww>2.1)
 if main:
  ln,a,b,u,n=main
  for frac in front_gables:
   w=min(6.5,ln/max(2,len(front_gables)*1.5));k.gable(a+u*ln*frac,u,n,eave,w,rise+.55,4.0)
  for j in range(dormers):k.dormer(a+u*ln*(j+.5)/dormers,u,n,eave)
 return main

def rebuild(ident,p,h,levels,t):
 row=BYID[ident];c=row['code'];k=Quad(t,t.ms);a,b,d,e=p.bounds;cx,cy=p.centroid.coords[0];s=row['section'];ev=s['eave_m'];rise=s['roof_rise_m'];levels=s['levels'];side=s['entry'];profile=c.lower()+'_quadrangle'
 if c=='U057':
  result=science_neighbor(ident,p,h,levels,t)
  # Preserve four roof heat-recovery chambers; give each a bounded real louver
  # bank and panel seams rather than another decorative roof box.
  for parts in list(t.ms['MedicalSteel']):
   lo,hi=parts.bounds
   if lo[2]>18.7:
    for z in np.arange(lo[2]+.35,hi[2]-.15,.45):k.bar(((lo[0]+hi[0])/2,lo[1]-.02),(1,0),(0,-1),hi[0]-lo[0]-.3,.07,.08,float(z),'MedicalPlant')
  k.portal(p,'E',18.8,3.3,6.2,steps=3);peak=22.34
 elif c=='U084':
  # Levi's photographed east-west pedestrian opening is physically open,
  # with the glazed bridge above it spanning the separate stone piers.
  cy=(b+e)/2;void=box(a-1,cy-3.1,d+1,cy+3.1);lower=p.difference(void)
  k.solid(lower,0,6.4,'QuadStone');k.solid(p,6.4,18.6,'QuadStone');k.solid(p,25,.15,'RoofMembrane')
  for aa,bb,u,n,ln in k.walls(p):
   if ln<5:continue
   for j in range(max(1,round(ln/3.5))):
    cc=aa+(bb-aa)*(j+.5)/max(1,round(ln/3.5))
    for zz in [2.0,7.1,11.3,15.5,19.7]:
     if zz<6.4 and abs(cc[1]-cy)<4:continue
     k.pane(cc,u,n,zz,1.65,2.0,False,2)
  for xx,n in [(a,(-1,0)),(d,(1,0))]:k.pane((xx,cy),(0,1),n,6.5,6.0,3.6,False,4)
  for zz in [6.4,10.6,14.8,19,23.2,24.9]:k.band(p,zz,.13,'QuadTrim')
  for xx in [a-1,d+1]:k.solid(box(xx-1,cy-3.1,xx+1,cy+3.1),0,.18,'Paving')
  k.apertures=1;peak=25.15
 elif c=='U035':
  # Covered east-west walk preserved at grade. Pointed arch shoulders meet
  # the actual lintel; the opening must never be filled by a generic facade.
  mid=(b+e)/2;gx=(a+d)/2;void=unary_union([box(a-1,mid-1.9,d+1,mid+1.9),box(gx-2.15,b-1,gx+2.15,e+1)]);k.solid(p.difference(void),0,4.9,'QuadStone');k.solid(p,4.9,3.0,'QuadStone');t.roof_shell(p,7.9,2.3,t,'RoofClay')
  for xx,n,u in [(a,(-1,0),(0,-1)),(d,(1,0),(0,1))]:
   ap=arch(3.8,4.9);k.profile(box(-3.0,0,3.0,5.1).difference(ap),(xx,mid),u,n,0,.40,'QuadStone',-.15)
   k.profile(ap.buffer(.18).difference(ap),(xx,mid),u,n,0,.32,'QuadTrim',.1)
   for sign in [-1,1]:k.bar((xx,mid+sign*2.4),u,n,.38,.65,.7,5.7,'QuadTrim')
  for yy,n,u in [(b,(0,-1),(1,0)),(e,(0,1),(-1,0))]:
   ap=arch(4.3,4.9);k.profile(box(-3.4,0,3.4,5.1).difference(ap),(gx,yy),u,n,0,.4,'QuadStone',-.15);k.profile(ap.buffer(.2).difference(ap),(gx,yy),u,n,0,.32,'QuadTrim',.1)
  k.apertures=2;peak=10.33
 elif c=='U069':
  main=p.intersection(box(a-1,b-1,d+1,b+22));lecture=p.difference(main)
  authored_shell(k,main,14.8,3,3.8,True,'S',[.12,.88],2,rise=5.1)
  # Kent's northern lecture theatre is an octagonal volume, not a full-height
  # rectangular tower. The existing mapped bevels govern its base.
  k.solid(lecture,0,11.8,'QuadStone');t.roof_shell(lecture,11.8,5.4,t,'RoofClay')
  for aa,bb,u,n,ln in k.walls(lecture):
   if ln>4:k.pane((aa+bb)/2,u,n,3.2,min(ln*.55,3.0),4.0,True,2,tracery=True)
  k.portal(main,'S',14.8,3.3,5.2);peak=20.6
 elif c=='U067':
  south=p.intersection(box(a-1,b-1,d+1,b+25));north=p.difference(south)
  authored_shell(k,south,18.4,4,3.8,False,'S',[.13,.87],2,rise=5.5)
  authored_shell(k,north,14.0,3,3.6,False,'N',[],1,rise=4.2)
  obs=Point(655.4,905.3).buffer(4.1,quad_segs=8).intersection(south);k.solid(obs,18.4,5.6,'QuadStone');k.band(obs,23.7,.25,'QuadTrim')
  # Retain a closed observatory drum and rounded copper dome with a shutter
  # rib; no flat green square can substitute for the observatory silhouette.
  for j in range(8):
   th=(j+.5)*math.pi/4;n=np.array([math.cos(th),math.sin(th)]);u=np.array([-n[1],n[0]]);k.pane(np.array([655.4,905.3])+n*3.9,u,n,20.0,1.4,2.4,True,1)
  dome=trimesh.creation.uv_sphere(radius=4.1,count=[12,20]);v=dome.vertices;dome.update_faces(np.all(v[dome.faces,2]>=-1e-6,axis=1));dome.remove_unreferenced_vertices();dome=dome.convex_hull;dome.vertices+=np.array([655.4,905.3,24.0]);t.ms['RoofPatina'].append(dome)
  # sphere upper hemisphere is capped on the same seated drum datum.
  k.solid(obs,23.96,.08,'RoofPatina');k.portal(south,'S',18.4,3.0,4.8);peak=28.1
 elif c=='U097':
  authored_shell(k,p,14.6,3,3.6,True,'S',[.12,.88],2,rise=6.0)
  xy=(698.5,b+3.5);q=Point(*xy).buffer(3.1,quad_segs=2).intersection(p);k.solid(q,0,19.8,'QuadStone')
  for aa,bb,u,n,ln in k.walls(q):
   if ln>1.8:k.pane((aa+bb)/2,u,n,14.2,ln*.56,4.7,True,2,tracery=True)
  k.band(q,19.8,.35,'QuadTrim');k.solid(q,20.15,.15,'RoofClay')
  # Turret roof follows octagonal plan to its seated apex.
  cone=trimesh.creation.cone(radius=3.25,height=5.2,sections=8);cone.apply_translation([*xy,20.3]);t.ms['RoofClay'].append(cone)
  k.portal(p,'N',14.6,2.5,4.0);peak=25.5
 elif c=='U102':
  authored_shell(k,p,18.4,4,3.9,False,'N',[.15,.85],2,rise=5.3)
  # The documented meteorology tower stands at the northeast entrance,
  # continuous with the masonry below; its tall openwork head is distinct.
  xy=(674.1,770.6);q=Point(*xy).buffer(3.8,quad_segs=2).intersection(p);k.solid(q,0,28.0,'QuadStone')
  for zz in [5.4,10.2,15.0,19.8,24.6,27.7]:k.band(q,zz,.20,'QuadTrim')
  for aa,bb,u,n,ln in k.walls(q):
   if ln>2:
    for zz in [3.0,7.8,12.6,17.4,22.2]:k.pane((aa+bb)/2,u,n,zz,ln*.40,2.5,False,1)
    k.pane((aa+bb)/2,u,n,25.5,ln*.60,1.8,True,2)
  k.solid(q,28.0,.25,'RoofMembrane');k.band(q,28.25,.65,'QuadTrim',.22);k.portal(p,'N',18.4,3.0,4.7);peak=29.1
 elif c=='U107':
  # Bond nave runs east-west; the old y-axis roof was transverse to the nave.
  k.solid(p,0,8.7,'QuadStone');t.ms['RoofSlate'].extend(t.pitched(p,8.7,4.5,'x'))
  for aa,bb,u,n,ln in k.walls(p):
   if ln<7:continue
   count=5 if abs(u[0])>.8 else 1
   for j in range(count):
    cc=aa+u*ln*(j+.5)/count;k.pane(cc,u,n,2.2,1.6 if count>1 else 3.0,4.7,True,2,tracery=True)
    if count>1:
     cp=aa+u*ln*j/count
     for zz,ww,dep,hh in [(0,.55,1.0,4.3),(4.3,.45,.72,2.8)]:k.bar(cp+n*dep*.35,u,n,ww,dep,hh,zz,'QuadStone')
  k.portal(p,'W',8.7,2.5,4.4,steps=2);peak=13.3
 elif c=='U038':
  # Hutchinson's tall single dining volume has full-height traceried windows,
  # an open high roof and separate low service/west range.
  nave=p.intersection(box(a+6,b-1,d+1,e+1));service=p.difference(nave);k.solid(service,0,10.8,'QuadStone');t.roof_shell(service,10.8,3.3,t,'RoofClay')
  core=nave.buffer(-.45,join_style=2);k.solid(core,0,13.7,'WindowGlass')
  for aa,bb,u,n,ln in k.walls(nave):
   count=max(1,round(ln/5.7));step=ln/count;holes=[]
   for j in range(count):
    ww=min(3.35,step*.64);cc=step*(j+.5);pr=arch(ww,7.4)
    from shapely.affinity import translate
    holes.append(translate(pr,xoff=cc,yoff=4.4));k.pane(aa+u*cc,u,n,4.4,ww,7.4,True,3,offset=-.26,tracery=True)
   k.profile(box(0,0,ln,13.8).difference(unary_union(holes)),aa,u,n,0,.38,'QuadStone',-.15);k.apertures+=count
  t.ms['RoofClay'].extend(t.pitched(nave,13.8,6.0,'x'))
  # Masonry gable ends carry large traceried lights under the long nave ridge.
  for xx,n,u in [(nave.bounds[0],(-1,0),(0,-1)),(nave.bounds[2],(1,0),(0,1))]:
   half=(nave.bounds[3]-nave.bounds[1])/2;yc=(nave.bounds[1]+nave.bounds[3])/2
   pr=Polygon([(-half,0),(half,0),(0,6.0)]);opening=translate(arch(3.8,3.7),yoff=.45)
   k.profile(pr.difference(opening),(xx,yc),u,n,13.8,.35,'QuadStone',-.15)
   k.pane((xx,yc),u,n,14.25,3.8,3.7,True,3,offset=.055,tracery=True)
  k.band(nave,13.6,.3,'QuadTrim');k.portal(nave,'S',13.8,2.8,4.2);peak=20.0
 else:
  authored_shell(k,p,ev,levels,s.get('bay_m',3.8),s.get('pointed_top',False),side,s.get('gables',[]),s.get('dormers',0),s.get('roof','RoofClay'),rise)
  if s.get('opposite_gables'):
   target={'N':[0,-1],'S':[0,1],'E':[-1,0],'W':[1,0]}[side]
   faces=[(ln,aa,bb,u,n)for aa,bb,u,n,ln in k.walls(p)if np.dot(n,target)>.92]
   if faces:
    ln,aa,bb,u,n=max(faces,key=lambda q:q[0])
    for fraction in s['gables']:k.gable(aa+u*ln*fraction,u,n,ev,min(6.5,ln/(len(s['gables'])*1.5)),rise+.55,4.0)
  k.portal(p,side,ev,s.get('portal_width',2.8),min(5.1,ev*.33),s.get('portal_fraction',.5),steps=s.get('steps',3),pointed=c!='U100');peak=ev+rise+.6
  if c=='U098':
   # Cobb's identifiable projecting entrance is a tall Gothic composition,
   # not the same small door as the adjoining residential ranges.
   cc=np.array([522.6,771.0]);u=np.array([0.,1.]);n=np.array([1.,0.]);wing=box(519.2,766.7,523.0,775.3)
   k.solid(wing,0,19.2,'QuadStone');k.gable((523.0,771),u,n,19.2,8.6,5.4,5.5)
   k.pane((523.0,771),u,n,7.8,4.6,8.6,True,3,tracery=True)
   k.pane((523.0,771),u,n,4.7,4.5,1.8,False,4)
   k.portal(wing,'E',19.2,3.2,4.25,steps=3)
   for yy in [766.8,775.2]:
    k.bar((523.0,yy),u,n,.65,.75,21.0,0,'QuadTrim')
    cone=trimesh.creation.cone(radius=.55,height=2.0,sections=8);cone.apply_translation([523.0,yy,21.0]);t.ms['QuadTrim'].append(cone)
   peak=max(peak,24.6)
  if c=='U100':
   # Pick's flat-roofed modern body is intentionally exempt from Gothic roofs.
   peak=ev+.2
  if c in ['U098','U117','U139']:
   # Mapped corner projections receive supported short polygonal turrets,
   # differentiated from the tall meteorology tower on Rosenwald.
   coords={'U098':[(d-2,b+2),(d-2,e-2)],'U117':[(d-4,b+8),(d-4,e-3)],'U139':[(d-2,b+2),(d-2,e-2)]}[c]
   for xy in coords:
    q=Point(*xy).buffer(1.35 if c!='U139'else 1.8,quad_segs=4).intersection(p)
    if q.area<1:continue
    k.solid(q,0,ev+1.1,'QuadStone');k.band(q,ev+.9,.22,'QuadTrim');cone=trimesh.creation.cone(radius=1.5 if c!='U139'else 2.0,height=rise+1.3,sections=8);cone.apply_translation([*xy,ev+1.1]);t.ms['RoofClay'].append(cone);peak=max(peak,ev+rise+2.4)
  if c in ['U034','U036','U050','U051']:
   # Hull laboratories' stone mullioned gables and real paired cloisters are
   # retained on their own mapped ranges, not one filled courtyard slab.
   for aa,bb,u,n,ln in k.walls(p):
    if ln>20:
     for fraction in [.25,.75]:
      cc=aa+u*ln*fraction;k.bar(cc+n*.1,u,n,.6,.35,ev*.86,0,'QuadTrim')
  if c=='U039':
   # Snell/Hitchcock remains three low residential floors; broad red roof and
   # shallow dormers must not turn the dormitory into a tall academic block.
   peak=ev+rise+.6
 STATS[ident]=k.stats()
 return {'profile':profile,'height':peak,'levels':levels,'features':row['modeled_features'],'reference':row['references'][0],'references':row['references'],'modeling_level':'detailed exterior reconstruction','source_specific_sections':s,'quadrangle_detail':{'code':c,'entries':k.entries,'dormers':k.dormers,'projecting_gables':k.gables,'traceried_openings':k.traceries,'true_apertures':k.apertures},'manual_joinery':k.stats(),'approximation':CAT['dimension_status'],'limits':CAT['dimension_status'],'source_scope':'Exterior photo and aerial comparison, retained georeferenced mapped footprint; sculpture abstracted.'}

def finish(ident):
 d=STATS[ident];return {key:d.get(key,0)for key in ['window_surrounds','entrances','buttresses','courses','traceried_openings','roof_dormers','projecting_gables']}


def harper(ms,p,h,body,t):
 """Specific tall reading hall, recessed tracery and differentiated tower ends."""
 k=Quad(t,ms);a,b,c,d=p.bounds;cx,cy=p.centroid.coords[0]
 towers=p.intersection(unary_union([box(a-1,b-1,a+16,d+1),box(c-16,b-1,c+1,d+1)]));middle=p.difference(towers)
 k.solid(middle,0,15.5,'QuadStone');upper_hall=box(a+16,649.0,c-16,669.35)
 k.solid(upper_hall.buffer(-.48,join_style=2),15.5,10.7,'WindowGlass')
 upper=[]
 for xx in np.linspace(a+16+(c-a-32)/16,c-16-(c-a-32)/16,8):
  cut=LineString([(xx,b-2),(xx,d+2)]).intersection(upper_hall)
  for yy,nn in [(cut.bounds[1],(0,-1)),(cut.bounds[3],(0,1))]:
   k.pane((xx,yy),(1,0),nn,16.,3.8,8.7,True,3,offset=-.22,tracery=True)
   # Heraldic spandrel panel stays below each real reading-room bay.
   k.bar((xx,yy),[1,0],nn,2.5,.20,.65,14.5,'QuadTrim');upper.append((xx,yy))
  for yy,nn in [(cut.bounds[1],(0,-1)),(cut.bounds[3],(0,1))]:
   for z in [1.6,7.1]:k.pane((xx,yy),(1,0),nn,z,2.2,3.15,False,2)
 # Actual wall perforations, revealing a recessed plane rather than a glass
 # rectangle pasted to a solid stone wall. Repeated tiny mapped indents never
 # restart the eight-bay reading-hall rhythm.
 for aa,bb,u,n,ln in k.walls(upper_hall):
  holes=[]
  for xx,yy in upper:
   pt=np.array([xx,yy]);off=float(np.dot(pt-aa,u));dist=abs(float(np.dot(pt-aa,n)))
   if dist<.5 and 0<off<ln:
    from shapely.affinity import translate
    holes.append(translate(arch(3.8,8.7),xoff=off,yoff=.5))
  k.profile(box(0,0,ln,10.7).difference(unary_union(holes)),aa,u,n,15.5,.35,'QuadStone',-.1)
  k.apertures+=len(holes)
 t.roof_shell(upper_hall,26.2,5.8,t,'RoofClay')
 for z in [.35,5.7,11.8,15.2]:k.band(middle,z,.24,'QuadTrim',.24)
 k.band(upper_hall,25.8,.24,'QuadTrim',.24)
 # Reading-hall buttress/bay dividers stop at the crenellated parapet.
 for yy,nn in [(b,(0,-1)),(669.3,(0,1))]:
  for xx in np.linspace(a+16,c-16,9):
   section=LineString([(xx,b-2),(xx,d+2)]).intersection(upper_hall)
   if section.is_empty:continue
   ywall=section.bounds[1]if nn[1]<0 else section.bounds[3]
   k.bar((xx,ywall),[1,0],nn,.50,.45,11.0,15.0,'QuadTrim')
 for idx,q in enumerate(t.polygons(towers)):
  k.solid(q,0,37.6,'QuadStone');k.solid(q,37.6,.2,'RoofMembrane');k.band(q,37.8,.6,'QuadTrim',.32)
  for aa,bb,u,n,ln in k.walls(q):
   if ln<5:continue
   for f in [.28,.72]:
    cc=aa+u*ln*f
    for z in [1.5,6.3,11.1]:k.pane(cc,u,n,z,min(2.3,ln*.20),3.2,False,2)
    k.pane(cc,u,n,26.4,min(3.0,ln*.25),8.7,True,2,tracery=True)
   for j in range(5):k.pane(aa+u*ln*(j+.5)/5,u,n,17.5,min(.75,ln*.11),2.7,True,1)
   # Screen parapets have separated, supported crest blocks, not fine spikes.
   for f in np.linspace(.08,.92,max(3,round(ln/1.4))):k.bar(aa+u*ln*f,u,n,.65,.5,.60,38.4,'QuadTrim')
  for aa,bb,u,n,ln in k.walls(q):
   if ln>6:
    for f in [.02,.50,.98]:k.bar(aa+u*ln*f,u,n,.48,.38,15.8,21.4,'QuadTrim')
  for z in [.4,5.5,10.4,15.9,21.4,25.5,36.8]:k.band(q,z,.24,'QuadTrim',.24)
  xa,ya,xb,yb=q.bounds
  for xx,yy in [(xa+.8,ya+.8),(xa+.8,yb-.8),(xb-.8,ya+.8),(xb-.8,yb-.8)]:
   pt=nearest_points(q.buffer(-.85),Point(xx,yy))[0];pier=Point(pt.x,pt.y).buffer(.72,quad_segs=2)
   k.solid(pier,21.4,18.9,'QuadStone');k.band(pier,39.8,.25,'QuadTrim');k.solid(pier.buffer(-.18),40.3,.848,'QuadTrim')
 # Actual north and south doors, nested archivolts and connected grade steps.
 for side in ['N','S']:k.portal(middle,side,15.5,3.1,5.0,steps=4)
 # Stone shields / sculptural blocks are deliberately abstracted. They stay
 # confined to the photographed spandrel/portal locations, not random roof boxes.
 for x,y in upper:
  nn=(0,-1)if y<cy else(0,1);shield=Polygon([(-.45,0),(.45,0),(.45,.65),(0,.85),(-.45,.65)])
  k.profile(shield,(x,y),(1,0),nn,13.6,.18,'QuadStone',.18)
 return {'reference':BYID[156128082]['references'][0],'references':BYID[156128082]['references'],'features':BYID[156128082]['modeled_features'],'modeling_level':'detailed exterior reconstruction','central_reading_hall_bays':8,'tower_peak_m':41.148,'manual_joinery':k.stats(),'quadrangle_detail':{'true_reading_apertures':k.apertures,'traceried_openings':k.traceries,'entries':k.entries},'limits':CAT['dimension_status']+' Towers retain the published maximum. Heraldic and figurative carving is represented as bounded abstract stone relief, not a scanned replica.'}


def landscape(t):
 patch=box(488,640,746,1040);foot=t.footprints;avoid=foot.union(t.roadarea);walk=t.walkarea.intersection(patch)
 # Keep source-mapped path centerlines and lawn islands authoritative. A narrow
 # seated stone edge and paving joints refine these existing paths only.
 border=walk.boundary.buffer(.13,join_style=2).difference(avoid);t.env(border,.145,.055,'QuadTrim')
 count=0
 for axis,start,stop in [('x',500,744),('y',646,1035)]:
  for q in np.arange(start,stop,4.2):
   line=LineString([(q,640),(q,1040)])if axis=='x'else LineString([(488,q),(746,q)])
   joint=line.buffer(.022,cap_style=2).intersection(walk).difference(avoid)
   if joint.area>.03:t.env(joint,.167,.012,'Paving');count+=1
 # Original mapped Botany Pond edge, seated stone coping and low planting;
 # leave water shape and island in the source data, never replace by a circle.
 pond=unary_union(t.water).intersection(box(600,960,650,1010));edge=pond.boundary.buffer(.35).difference(pond).difference(foot).difference(t.walkarea)
 t.env(edge,.13,.22,'QuadStone')
 # Short connections from the authored door landing to an existing mapped
 # walk; no new arbitrary cross-lawn routes or crossings.
 links=0
 for f in t.buildings:
  row=f['record'];detail=(row.get('campus_refinement')or{}).get('quadrangle_detail')or(row.get('exterior_reconstruction')or{}).get('quadrangle_detail')
  if not detail:continue
  for ent in detail.get('entries',[]):
   xy=np.array(ent['center'])+np.array(ent['normal'])*1.8;pt=Point(*xy);near=nearest_points(pt,t.walkarea)[1]
   if 0.1<pt.distance(near)<12:
    q=LineString([pt,near]).buffer(min(1.5,ent.get('width_m',3)/2),cap_style=2).difference(avoid);t.env(q,.15,.045,'Paving');links+=1
 # Sparse benches/lamp standards along existing central promenades. Seating
 # outside walks and building/pond masks prevents new obstructions.
 benches=0
 for x,y,angle in [(600,817,0),(600,851,0),(631,817,0),(631,851,0),(592,986,90),(631,986,90),(552,690,0),(607,693,0),(689,808,90),(543,808,90)]:
  pt=Point(x,y)
  if foot.buffer(1).contains(pt)or walk.buffer(.4).contains(pt)or pond.contains(pt):continue
  u=np.array([math.cos(math.radians(angle)),math.sin(math.radians(angle))]);n=np.array([-u[1],u[0]]);k=Kit(t,t.eg)
  k.bar((x,y),u,n,1.8,.48,.10,.48,'Furniture');k.bar(np.array([x,y])+n*.19,u,n,1.8,.09,.42,.58,'Furniture')
  for sign in [-1,1]:k.bar(np.array([x,y])+u*sign*.65,u,n,.09,.40,.48,0,'Furniture')
  benches+=1
 return {'existing_path_edge_m':round(walk.boundary.length,2),'paving_joint_segments':count,'mapped_pond_edge_refined_m':round(edge.length,2),'short_entry_links':links,'benches':benches,'invented_cross_lawn_paths':0}
