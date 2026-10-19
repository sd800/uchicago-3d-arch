"""Crerar source-comparison reconstruction and bounded Science Quad exteriors.

See sources/science_quadrangle_review.json. Published dimensions are used only
where identified; sections, minor members and secondary bays are estimates.
"""
import numpy as np
import trimesh
from shapely.geometry import Polygon,Point,LineString,box
from shapely.ops import unary_union,nearest_points
from campus_refinement import oriented

CRERAR_REFERENCE='https://marcararc.co/portfolio/crerar-reno/'
CRERAR_FEATURES=['Three above-ground levels with a genuinely recessed lower envelope and 11-foot upper cantilever','Thick limestone panel walls with recessed 25-foot-wide renovated top-floor glass bays','Independent stone entrance arch, recessed two-storey glazing and connected granite steps','Two shaped glazed atrium/stair rooflights and smaller renovation skylights','Stone panel joints, window reveals, soffit divisions, handrails and low planting walls']
HARPER_REFERENCE='https://architecture.uchicago.edu/locations/william_rainey_harper_memorial_library/'
HARPER_FEATURES=['Two differentiated Gothic end towers at the retained published maximum','Central high reading-hall range with eight tall traceried window bays','Two lower academic floors, stone courses and grounded central entrance','Connected pitched roof and four attached corner turrets on each tower','Recessed paired lower lights, narrow tower gallery lights and upper Gothic windows']

class Kit:
 def __init__(self,ctx,ms):self.t=ctx;self.ms=ms;self.panes=0
 def solid(self,g,z,h,mat):
  for p in self.t.polygons(g):self.ms[mat].append(self.t.extrusion(p,z,h))
 def band(self,p,z,h=.18,mat='CrerarStone',depth=.2):self.solid(p.buffer(.08,join_style=2).difference(p.buffer(-depth,join_style=2)),z,h,mat)
 def bar(self,c,u,n,w,depth,h,z,mat):self.ms[mat].append(oriented(self.t,np.array(c),np.array(u),np.array(n),w,depth,h,z))
 def profile(self,p,c,u,n,z,depth,mat,offset=0):
  c,u,n=map(np.asarray,[c,u,n])
  for q in self.t.polygons(p):
   m=self.t.extrusion(q,0,depth);v=m.vertices.copy();m.vertices=np.column_stack([c[0]+u[0]*v[:,0]+n[0]*(v[:,2]+offset),c[1]+u[1]*v[:,0]+n[1]*(v[:,2]+offset),z+v[:,1]]);trimesh.repair.fix_normals(m);self.ms[mat].append(m)
 def pane(self,c,u,n,z,w,h,arch=False,glass='CrerarGlass',trim='CrerarMetal',divisions=3,offset=.10):
  profile=Polygon([(-w/2,0),(w/2,0),(w/2,h*.74),(w*.30,h*.94),(0,h),(-w*.30,h*.94),(-w/2,h*.74)])if arch else box(-w/2,0,w/2,h)
  self.profile(profile,c,u,n,z,.09,glass,offset)
  ring=profile.buffer(.085,join_style=2).difference(profile.buffer(-.035,join_style=2));self.profile(ring,c,u,n,z,.15,trim,offset+.04)
  for j in range(1,divisions):
   x=w*(j/divisions-.5);cut=box(x-.035,0,x+.035,h).intersection(profile);self.profile(cut,c,u,n,z,.13,trim,offset+.08)
  self.panes+=1
 def walls(self,p):
  for q in self.t.polygons(p):
   for ring in [q.exterior,*q.interiors]:
    cc=np.array(ring.coords)
    for a,b in zip(cc[:-1],cc[1:]):
     ln=np.linalg.norm(b-a)
     if ln>2:
      u=(b-a)/ln;yield a,b,u,np.array([u[1],-u[0]]),ln
 def ribbon(self,p,z,h,mat='CrerarGlass',bay=3):
  for a,b,u,n,ln in self.walls(p):self.pane((a+b)/2,u,n,z,ln-.35,h,glass=mat,divisions=max(2,int(ln/bay)))
 def rail(self,a,b,z=1.0):
  a,b=np.asarray(a),np.asarray(b);self.ms['CrerarMetal'].append(self.t.cylinder((*a,z),(*b,z),.035,6))
  for f in np.linspace(0,1,max(2,int(np.linalg.norm(b-a)/2.4)+1)):
   c=a+(b-a)*f;self.ms['CrerarMetal'].append(self.t.cylinder((*c,.04),(*c,z),.035,6))
 def stats(self):return {'framed_openings':self.panes,'transoms':0,'roof_coping_m':0,'hollow_bells':0,'added_triangles':sum(len(m.faces)for parts in self.ms.values()for m in parts),'authored_joinery':True}

def crerar(ms,p,h,body,t):
 k=Kit(t,ms);a,b,c,d=p.bounds;cx,cy=p.centroid.coords[0];entry_y=b+23.0;lower=p.buffer(-3.3528,join_style=2)
 body(lower,0,10.3,'CrerarGlass',windows=False);k.solid(lower,0,.95,'CrerarStone')
 # Broad structural grid stays behind the cantilever rather than decorating a
 # solid pale box with a regular classroom window pattern.
 for yy in [b+12,b+73]:
  k.bar((lower.bounds[2]+.08,yy),(0,1),(1,0),5.0,.72,10.3,0,'CrerarStone')
 for aa,bb,u,n,ln in k.walls(lower):
  count=max(1,round(ln/8.6));step=ln/count
  for j in range(count+1):
   point=aa+u*j*step
   if n[0]>.8 and abs(point[1]-entry_y)<4.5:continue
   k.bar(point+n*.08,u,n,.65,.45,10.3,0,'CrerarStone')
  for z in [4.4,9.35]:
   beam=box(0,z,ln,z+.8)
   if n[0]>.8:
    offsets=sorted([(entry_y-5-aa[1])/u[1],(entry_y+5-aa[1])/u[1]]);beam=beam.difference(box(offsets[0],0,offsets[1],9.3))
   k.profile(beam,aa,u,n,0,.5,'CrerarStone',-.15)
  for j in range(count):
   center=aa+u*(j+.5)*step
   if n[0]>.8 and abs(center[1]-entry_y)<7.0:continue
   for z,hh in [(1.05,3.25),(5.3,3.9)]:k.pane(center,u,n,z,step-.72,hh,divisions=3)
 # Actual wall apertures in a thick stone skin, with a recessed glass core.
 body(p.buffer(-.48,join_style=2),10.3,4.7,'CrerarGlass',windows=False)
 upper_bays=[]
 for aa,bb,u,n,ln in k.walls(p):
  count=max(1,round(ln/9.0));step=ln/count;holes=[]
  for j in range(count):
   cc=(j+.5)*step;ww=min(7.62,step-1.35);holes.append(box(cc-ww/2,.72,cc+ww/2,.72+3.3528))
   k.pane(aa+u*cc,u,n,11.02,ww,3.3528,divisions=max(3,round(ww/1.2)),offset=-.31);upper_bays.append([*(aa+u*cc),ww])
  k.profile(box(0,0,ln,4.7).difference(unary_union(holes)),aa,u,n,10.3,.34,'CrerarStone',-.12)
  # Subtle ashlar joints stop at the actual stone panel fields.
  for j in range(count+1):k.bar(aa+u*j*step+n*.235,u,n,.018,.018,4.7,10.3,'CrerarJoint')
  for z in [10.66,14.65]:k.bar((aa+bb)/2+n*.235,u,n,ln,.02,.018,z,'CrerarJoint')
 k.solid(p,15,.16,'RoofMembrane');k.band(p,15.16,.14,'CrerarStone');k.solid(p.difference(lower),10.3,.22,'CrerarStone')
 # Entry arch is separate from the recessed glazing and remains physically open.
 portal=Polygon([(-4.4,-1),(4.4,-1),(4.4,7.3),(3.0,9.1),(0,9.7),(-3.0,9.1),(-4.4,7.3)])
 k.profile(box(-5.5,0,6.8,15.3).difference(portal),(c+.6,entry_y),(0,1),(1,0),0,.9,'CrerarStone',-.45)
 k.pane((lower.bounds[2],entry_y),(0,1),(1,0),1.12,9.8,8.6,divisions=5)
 landing=box(lower.bounds[2],entry_y-7,c+6,entry_y+7);k.solid(landing,0,1.08,'Paving')
 for j in range(7):k.solid(box(c+6+j*.40,entry_y-5,c+6+(j+1)*.40,entry_y+5),0,1.08*(7-j)/7,'Paving')
 for yy in [entry_y-5.1,entry_y+5.1]:
  k.solid(box(c+.8,yy-.20,c+6.2,yy+.20),0,1.48,'CrerarStone')
  k.rail((c+6.2,yy),(c+8.8,yy),1.12)
 for yy in [entry_y-2.5,entry_y+2.5]:
  # A descending stair rail, attached to the real upper landing and grade.
  start=np.array([c+5.8,yy,2.05]);end=np.array([c+8.8,yy,.96]);ms['CrerarMetal'].append(t.cylinder(start,end,.035,6))
  for f in [0,.5,1]:
   q=start+(end-start)*f;ms['CrerarMetal'].append(t.cylinder((q[0],q[1],max(.02,q[2]-.96)),q,.035,6))
 # Two replaced large rooflights, and a family of small rooflights, follow the
 # architect's renovation plan rather than one unsupported glass roof box.
 rooflights=[box(cx-10,entry_y-7,cx+10,entry_y+7),box(cx-4,cy+9,cx+4,cy+23)]
 for q in rooflights:
  q=q.intersection(p.buffer(-1));k.solid(q,15.16,.26,'CrerarMetal')
  for poly in t.polygons(q):
   ms['CrerarGlass'].extend(t.pitched(poly,15.42,1.0,'y'))
   xa,ya,xb,yb=poly.bounds
   for yy in np.linspace(ya+1,yb-1,6):
    ms['CrerarMetal'].append(t.cylinder((xa,yy,15.46),((xa+xb)/2,yy,16.55),.045,6));ms['CrerarMetal'].append(t.cylinder(((xa+xb)/2,yy,16.55),(xb,yy,15.46),.045,6))
 for yy in [b+11,b+40,b+61,b+78]:
  for xx in [a+8,c-8]:
   q=box(xx-1.1,yy-1.8,xx+1.1,yy+1.8).intersection(p.buffer(-1));k.solid(q,15.18,.18,'CrerarMetal');k.solid(q.buffer(-.12),15.36,.12,'CrerarGlass')
 return {'reference':CRERAR_REFERENCE,'features':CRERAR_FEATURES,'modeling_level':'detailed exterior reconstruction','cantilever_m':3.3528,'atrium_roof_lantern':True,'entry_center':[c+.6,entry_y],'upper_glazed_bays':upper_bays,'large_rooflights':2,'small_rooflights':8,'manual_joinery':k.stats(),'limits':'Mapped outline retained. Published 11 ft overhang, 11 ft tall and up-to-25 ft wide replacement panes inform the model; local heights, entry placement, stone panel joints and rooflight sections are exterior interpretations.'}

def harper(ms,p,h,body,t):
 k=Kit(t,ms);a,b,c,d=p.bounds;cx,cy=p.centroid.coords[0]
 towers=p.intersection(unary_union([box(a-1,b-1,a+15,d+1),box(c-15,b-1,c+1,d+1)]));middle=p.difference(towers)
 body(middle,0,26.2,'QuadStone',windows=False);t.roof_shell(middle,26.2,5.8,t,'RoofClay')
 for q in t.polygons(middle):
  for zz in [5.7,11.8,15.2,25.8]:k.band(q,zz,.23,'QuadTrim',.2)
 # One authored eight-bay rhythm per elevation. Small footprint indents must
 # not restart the window count or erase a bay at a short wall segment.
 for xx in np.linspace(a+15+(c-a-30)/16,c-15-(c-a-30)/16,8):
  section=LineString([(xx,b-1),(xx,d+1)]).intersection(middle)
  if section.is_empty:continue
  for yy,normal in [(section.bounds[1],(0,-1)),(section.bounds[3],(0,1))]:
   center=(xx,yy)
   for zz in [1.6,7.1]:k.pane(center,(1,0),normal,zz,2.2,3.15,glass='WindowGlass',trim='QuadTrim',divisions=2)
   k.pane(center,(1,0),normal,16.0,min(3.8,(c-a-30)/8*.69),8.7,True,'WindowGlass','QuadTrim',3)
 for q in t.polygons(towers):
  body(q,0,38.0,'QuadStone',windows=False);k.solid(q,38,.20,'RoofSlate');k.band(q,37.8,.6,'QuadTrim',.3)
  for aa,bb,u,n,ln in k.walls(q):
   if ln<5:continue
   for frac in [.28,.72]:
    center=aa+u*ln*frac
    for zz in [1.5,6.3,11.1]:k.pane(center,u,n,zz,min(2.3,ln*.21),3.2,glass='WindowGlass',trim='QuadTrim',divisions=2)
    k.pane(center,u,n,26.4,min(3.0,ln*.25),8.7,True,'WindowGlass','QuadTrim',2)
   for j in range(5):k.pane(aa+u*ln*(j+.5)/5,u,n,17.5,min(.75,ln*.11),2.7,True,'WindowGlass','QuadTrim',1)
  for zz in [5.5,10.4,15.9,21.4,25.5,36.8]:k.band(q,zz,.25,'QuadTrim',.22)
  xa,ya,xb,yb=q.bounds
  for xx,yy in [(xa+.7,ya+.7),(xa+.7,yb-.7),(xb-.7,ya+.7),(xb-.7,yb-.7)]:
   inset=q.buffer(-1.1);point=nearest_points(inset if not inset.is_empty else q,Point(xx,yy))[0];xx,yy=point.x,point.y
   pier=box(xx-.57,yy-.57,xx+.57,yy+.57);k.solid(pier,22.2,18.0,'QuadStone');k.solid(pier.buffer(.15),39.65,.28,'QuadTrim');k.solid(pier.buffer(-.12),40.2,.948,'QuadTrim')
  # Low carved crest silhouettes, avoiding castle-like generic battlements.
  for aa,bb,u,n,ln in k.walls(q):
   if ln>8:
    for off in [.23,.5,.77]:k.bar(aa+u*off*ln,u,n,.45,.35,.65,38.2,'QuadTrim')
 section=LineString([(cx,b-1),(cx,d+1)]).intersection(p);center=np.array([cx,section.bounds[1]]);u=np.array([1.,0.]);n=np.array([0.,-1.])
 k.pane(center,u,n,.16,3.6,5.2,True,'DoorWood','QuadTrim',2)
 for j in range(4):k.bar(center+n*(.45+j*.4),u,n,5.4,.4,.16*(4-j),0,'Paving')
 return {'reference':HARPER_REFERENCE,'features':HARPER_FEATURES,'modeling_level':'optimized exterior','central_reading_hall_bays':8,'tower_peak_m':41.148,'manual_joinery':k.stats(),'limits':'Published tower maximum retained. Hall eaves, turrets, window groups and entrance members are proportional exterior estimates; heraldic sculpture is abstracted.'}

NEIGHBOR_IDS={142870317,154656512,88865426,154859380}
def neighbor(ident,p,h,levels,t):
 cfg=t.current_design;k=Kit(t,t.ms);a,b,c,d=p.bounds;cx,cy=p.centroid.coords[0];features=[]
 def body(g,z,hh,mat,lev=1,windows=False):t.body(g,z,hh,mat,lev=lev,windows=windows,arch=False)
 if ident==142870317:
  east=p.intersection(box(a+17,b-1,c+1,d+1));west=p.difference(east);body(east,0,14.0,'QuadStone',3,True);body(west,0,12.6,'CrerarGlass')
  k.ribbon(west,.6,11.5,bay=2.4)
  for z in [4.2,8.4,12.5]:k.band(west,z,.22,'QuadTrim')
  k.solid(east,14,.14,'RoofMembrane');k.solid(west,12.6,.14,'RoofMembrane')
  spine=p.intersection(box(a+14,b+1,a+20,d-1));body(spine,12.6,1.4,'CrerarGlass')
  for q in t.polygons(spine):t.ms['CrerarGlass'].extend(t.pitched(q,14,2.0,'y'))
  k.band(spine,14,.15,'CrerarMetal');h=16.2;levels=3;profile='kersten';features=['Stone Ellis Avenue wing and angled glazed science-quadrangle frontage','Three teaching levels with separate roof heights','Continuous glazed central spine and pitched atrium rooflight','Existing north bridge connection retained']
 elif ident==154656512:
  h=18.8;levels=4;body(p,0,h,'QuadStone',4,True);k.solid(p,h,.14,'RoofMembrane')
  for z in [4.6,9.2,13.8]:k.band(p,z,.18,'QuadTrim')
  inset=p.buffer(-4)
  for fraction in [.18,.39,.61,.82]:
   yy=b+(d-b)*fraction;line=LineString([(a-1,yy),(c+1,yy)]).intersection(inset)
   point=line.representative_point() if not line.is_empty else nearest_points(inset,Point(cx,yy))[0]
   q=box(point.x-2,point.y-3.2,point.x+2,point.y+3.2).intersection(p);body(q,h,3.4,'MedicalSteel');k.solid(q,h+3.4,.14,'MedicalPlant')
  for n,u,cc in [([1,0],[0,1],[c,cy]),([-1,0],[0,-1],[a,cy])]:k.pane(cc,u,n,.16,5.2,7.0,glass='CrerarGlass',divisions=3)
  h+=3.54;profile='searle';features=['Four above-ground laboratory floors, replacing an incorrect Gothic pitched-roof profile','Flat membrane roof and four documented heat-recovery chambers','Two-storey glazed entrances on Ellis Avenue and quadrangle sides','Openings and secondary plant dimensions remain estimates']
 elif ident==88865426:
  h=23.4;levels=6;body(p,0,h,'QuadStone',6,False);k.solid(p,h,.14,'RoofMembrane');shafts=[]
  for side in [a+1,c-5.8]:
   for index,yy in enumerate([b+10,d-16]):
    q=p.intersection(box(side,yy,side+4.8,yy+5.0));shafts.append(q.buffer(.3));body(q,0,29.0,'QuadStone');back=p.intersection(box(side+.8,yy+3,side+5.8,yy+8));body(back,23.4,7.0,'WarmBrick');k.solid(back,30.4,.14,'MedicalPlant')
    for dx in [0,3.6]:body(q.intersection(box(side+dx,yy,side+dx+1.1,yy+5)),29,3.0,'QuadStone')
    if not q.is_empty:k.pane((side+2.4,yy),[1,0],[0,-1],25.1,2.5,3.5,glass='MedicalPlant',divisions=5)
  mask=unary_union(shafts)
  for aa,bb,u,n,ln in k.walls(p):
   count=max(1,int(ln/3.6))
   for j in range(count):
    center=aa+(bb-aa)*(j+.5)/count
    if mask.intersects(Point(center)):continue
    for z in np.arange(.8,23,3.9):k.pane(center,u,n,float(z),.95,2.5,glass='WindowGlass',trim='CrerarMetal',divisions=1)
  for z in [3.9,7.8,11.7,15.6,19.5,23.3]:k.band(p,z,.16,'QuadTrim')
  h=32.0;profile='hinds';features=['Six photo-interpreted window rows and a distinct flat main laboratory roof','Four attached stone service shafts with split heads rising above the main block','Separate red-brick vent housings, dark louvers and continuous slab courses','Tower positions and all unpublished section elevations remain estimates']
 else:
  h=14.8;levels=4;body(p,0,h,'QuadStone',4,True);t.roof_shell(p,h,3.6,t,'RoofSlate');profile='jones'
  for aa,bb,u,n,ln in k.walls(p):
   if n[0]>.8 and ln>10:
    k.pane((aa+bb)/2,u,n,.15,3.2,4.6,True,'DoorWood','QuadTrim',2)
  h+=3.74;features=['Historic stone chemistry ranges replace the incorrect generic modern profile','Connected slate wing roofs, parapet and grouped Gothic entry','Mapped setbacks and existing link to the adjacent chemistry ranges retained']
 return {'profile':profile,'height':h,'levels':levels,'features':features,'reference':cfg['references'][0],'modeling_level':'optimized exterior','optimization_recipe':cfg,'approximation':'Source-informed exterior massing; undocumented dimensions and minor openings remain estimates.'}

def landscape(t):
 # Extend only the short gaps between the designed entry apron and an existing
 # mapped walk. Leave the original Quad lawn and road network authoritative.
 cr=next(f['poly']for f in t.buildings if f['id']==152284260);a,b,c,d=cr.bounds;entry_y=b+23.0;point=Point(c+8.8,entry_y);near=nearest_points(point,t.walkarea)[1]
 link=LineString([point,near]).buffer(2.0,cap_style=2).difference(t.footprints).difference(t.roadarea)
 if point.distance(near)<25:t.env(link,.16,.055,'Paving')
 # Existing mapped walks receive paired edge strips; avoid inventing diagonal
 # cross-Quad paths or filling planted plots with arbitrary paving.
 patch=box(378,887,435,993);walk=t.walkarea.intersection(patch);edges=walk.boundary.buffer(.12).difference(t.footprints).difference(t.roadarea)
 t.env(edges,.18,.035,'Concrete')
 return {'crerar_entry_link_m':round(point.distance(near),2),'existing_quad_walks_refined_m2':round(walk.area,2),'new_cross_quad_routes':0}

def entry_clearance():return box(377,913,390,933)
