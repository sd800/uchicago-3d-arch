from campus_refinement import landscape as refine_landscape
from campus_optimization import rebuild as rebuild_ordinary, finish as finish_ordinary, facade as optimized_facade, specification
from athletic_fields import layout as athletic_layout, handles as athletic_handles, refine as refine_athletic_fields
from highlight_finish import detailed_joinery
from highlight_reconstruction import rebuild as rebuild_highlight, REFS as REBUILT_HIGHLIGHTS
from types import SimpleNamespace
"""UChicago Hyde Park exterior model. Metric georeferenced public footprints.

Native Rhino solids for massing, closed meshes for roofs/facades/landscape.
Published landmark heights are distinct from estimated local roof/facade geometry.
"""
import pathlib, json, math, csv, struct, xml.etree.ElementTree as ET
import numpy as np
import trimesh
import rhino3dm as rh
from shapely.geometry import Polygon, MultiPolygon, Point, LineString, box, shape, mapping
from shapely.geometry.polygon import orient
from shapely.ops import unary_union, transform
from shapely import affinity, set_precision, constrained_delaunay_triangles
from pyproj import Transformer

ROOT=pathlib.Path(__file__).resolve().parents[1]; OUT=ROOT/'output';OUT.mkdir(exist_ok=True)
TF=Transformer.from_crs(4326,32616,always_xy=True)
LON,LAT=-87.607,41.782;OX,OY=TF.transform(LON,LAT)
def project(x,y,z=None):
    a,b=TF.transform(x,y);return np.asarray(a)-OX,np.asarray(b)-OY
features=json.loads((ROOT/'sources/features_local.json').read_text())
for f in features:f['poly']=shape(f.pop('geometry')).buffer(0)
site=next(f['poly'] for f in features if f['id']==13117436)
midway=next(f['poly'] for f in features if f['id']==19743853)
scope=unary_union([site.buffer(13,join_style=2),midway]).buffer(0)
buildings=json.loads((ROOT/'sources/campus_buildings_local.json').read_text())
connectors=[f for f in buildings if f['tags'].get('building') in ['corridor','bridge']]
for f in connectors:f['poly']=shape(f['geometry']).buffer(0)
buildings=[f for f in buildings if (f['tags'].get('name') or f['tags'].get('addr:housenumber') or f['tags'].get('building') in ['university','dormitory','hospital','school','tower']) and f['tags'].get('building') not in ['corridor','bridge']]
for f in buildings:f['poly']=shape(f.pop('geometry')).buffer(0)
# Parking is a part of the shared 6054 footprint, rather than a duplicate building.
buildings=[f for f in buildings if f['id']!=477223629]
refs=json.loads((ROOT/'sources/architecture_sources.json').read_text())
CITY_URL='https://data.cityofchicago.org/Buildings/Building-Footprints/syp8-uezg'
city={r['bldg_id']:r for r in json.loads((ROOT/'sources/city_buildings.json').read_text())}
cityshapes=[(transform(project,shape(r['the_geom'])),r) for r in city.values()]
MAP_URL='https://maps.uchicago.edu/'
PD_URL='https://gisapps.chicago.gov/gisimages/zoning_pds/PD43.pdf'

COLORS={
 'Limestone':(207,194,166),'LightStone':(225,217,195),'Brick':(144,86,67),
 'Slate':(71,75,79),'Tile':(137,67,47),'Concrete':(197,198,193),'WhitePanel':(225,226,219),
 'Metal':(113,124,128),'Glass':(113,157,174),'DarkGlass':(59,83,91),'Frame':(64,65,64),
 'Ground':(218,218,207),'Road':(81,86,89),'Paving':(195,186,164),'Walk':(215,210,191),
 'Grass':(116,149,96),'Garden':(93,127,83),'Water':(83,144,166),'Track':(159,83,62),
 'Court':(89,132,122),'Marking':(232,228,207),'Leaves':(67,116,75),'Trunk':(119,95,68),
 'RatnerTan':(180,139,93),'RatnerBrown':(100,88,76),'RatnerDrum':(124,68,56),'RatnerRoof':(112,137,141),'RatnerRoofSeam':(88,110,115),'RatnerFascia':(66,83,86),'RatnerSteel':(214,219,210),'RatnerCable':(118,126,121),'RatnerGlass':(111,154,161),'RatnerFrost':(172,184,175),
 'ChapelStone':(185,184,170),'ChapelTrim':(207,204,186),'ChapelRoof':(106,115,118),'ChapelRoofSeam':(119,127,128),'ChapelRecess':(122,124,113),'ChapelDoor':(91,68,48),'ChapelDoorTrim':(119,93,64),'ChapelLead':(83,92,87),'ChapelLouvre':(62,67,64),
 'QuadStone':(185,181,162),'QuadTrim':(214,207,184),'WarmBrick':(139,83,64),'BrownBrick':(115,82,64),'HospitalBrick':(167,117,90),'WindowGlass':(73,99,105),'DoorWood':(86,62,45),'RoofSlate':(85,94,96),'RoofClay':(130,73,55),'RoofMembrane':(151,154,146),'RoofPatina':(111,143,130),
 'FieldTurf':(62,103,71),'FieldStripe':(70,113,77),'CourtApron':(72,101,88),'Infield':(179,129,94),'GoalPost':(219,201,133),
 'Furniture':(72,78,72),'Solar':(50,73,88),'PalevskyBrick':(177,79,48),'PalevskyPurple':(102,88,125),'PalevskyRoof':(145,108,85),
}
model=rh.File3dm();model.ApplicationName='UChicago Hyde Park Public-source Exterior Model'
model.Settings.ModelUnitSystem=rh.UnitSystem.Meters;model.Settings.ModelAbsoluteTolerance=.01
model.Settings.ModelAngleToleranceDegrees=1
anchor=model.Settings.EarthAnchorPoint;anchor.Name='Hyde Park local origin / WGS84'
anchor.EarthBasepointLatitude=LAT;anchor.EarthBasepointLongitude=LON
anchor.ModelBasePoint=rh.Point3d(0,0,0);anchor.ModelNorth=rh.Vector3d(0,1,0);anchor.ModelEast=rh.Vector3d(1,0,0)
model.Settings.EarthAnchorPoint=anchor
mats={};layers={};objects=[];meshdata=[];layer_map={};records=[];native_count=0
for name,c in COLORS.items():
    m=rh.Material();m.Name=name;m.DiffuseColor=(*c,255);m.Shine=0
    if name=='Glass':m.Transparency=.12
    mats[name]=model.Materials.Add(m)
def layer(name,mat):
    r=rh.Layer();r.Name=name;r.Color=(*COLORS[mat],255);layers[name]=model.Layers.Add(r);return layers[name]
layer('环境_Environment','Grass')
def polygons(g):
    if g.is_empty:return []
    if isinstance(g,Polygon):
        g=set_precision(g.buffer(0),.005).simplify(.002,preserve_topology=True).buffer(0)
        if not isinstance(g,Polygon):return polygons(g)
        return [orient(g,1)] if g.area>.025 else []
    if hasattr(g,'geoms'):return [p for a in g.geoms for p in polygons(a)]
    return []
def attr(name,lay,mat,info=None):
    a=rh.ObjectAttributes();a.Name=name;a.LayerIndex=layers[lay];a.MaterialIndex=mats[mat]
    a.MaterialSource=rh.ObjectMaterialSource.MaterialFromObject;a.ColorSource=rh.ObjectColorSource.ColorFromObject;a.ObjectColor=(*COLORS[mat],255)
    for k,v in (info or {}).items():a.SetUserString(k,str(v))
    return a
def rhmesh(m):
    r=rh.Mesh()
    for v in m.vertices:r.Vertices.Add(*map(float,v))
    for f in m.faces:r.Faces.AddFace(*map(int,f))
    r.Normals.ComputeNormals();r.Compact();assert r.IsValid
    return r
def extrusion(p,z,h):
    triangles=constrained_delaunay_triangles(p)
    vertices=[];faces=[];index={}
    for tri in triangles.geoms:
        face=[]
        for xy in list(tri.exterior.coords)[:3]:
            if xy not in index:index[xy]=len(vertices);vertices.append(xy)
            face.append(index[xy])
        faces.append(face)
    m=trimesh.creation.extrude_triangulation(np.asarray(vertices),np.asarray(faces),float(h));m.apply_translation([0,0,z])
    m.merge_vertices(digits_vertex=7);m.remove_unreferenced_vertices()
    trimesh.repair.fix_normals(m,multibody=True)
    if not(m.is_watertight and m.is_winding_consistent):
        m=trimesh.creation.extrude_polygon(p,float(h),engine='earcut');m.apply_translation([0,0,z]);trimesh.repair.fix_normals(m,multibody=True)
    if not(m.is_watertight and m.is_winding_consistent):
        cells=[]
        for triangle in constrained_delaunay_triangles(p).geoms:
            coords=np.asarray(triangle.exterior.coords)[:3];cell=trimesh.creation.extrude_triangulation(coords,np.array([[0,1,2]]),float(h));cell.apply_translation([0,0,z]);cells.append(cell)
        m=trimesh.util.concatenate(cells);trimesh.repair.fix_normals(m,multibody=True)
    assert m.is_watertight and m.is_winding_consistent,(p.bounds,h)
    return m
def boxmesh(x,y,z,sx,sy,sz):
    m=trimesh.creation.box(extents=(sx,sy,sz));m.apply_translation((x,y,z+sz/2));return m
def cylinder(a,b,r=.1,sections=8):
    return trimesh.creation.cylinder(radius=r,segment=np.asarray([a,b]),sections=sections)
def native_extrude(p,z,h,name,lay,mat,info):
    global native_count
    c=rh.PolylineCurve([rh.Point3d(float(x),float(y),float(z)) for x,y in p.exterior.coords]);e=rh.Extrusion.Create(c,float(h),True)
    for ring in p.interiors:e.AddInnerProfile(rh.PolylineCurve([rh.Point3d(float(x),float(y),float(z)) for x,y in ring.coords]))
    assert e.IsValid and e.IsSolid
    model.Objects.AddExtrusion(e,attr(name,lay,mat,info));native_count+=1
def push(name,m,mat,lay,native=True,info=None):
    assert len(m.vertices)<65536 and len(m.faces)<65536
    assert m.is_watertight and np.isfinite(m.vertices).all(),name
    objects.append({'name':name,'mesh':m,'mat':mat});meshdata.append((m,mat))
    layer_map[name]={'layer':lay,'category':'environment' if lay=='环境_Environment' else 'building','material':mat}
    if native:model.Objects.AddMesh(rhmesh(m),attr(name,lay,mat,info))
def chunk_meshes(prefix,ms,mat,lay,info=None):
    part=[];nv=nf=0;idx=0
    def flush():
        nonlocal idx
        if part:push(prefix+f'{idx:02d}',trimesh.util.concatenate(part),mat,lay,info=info);idx+=1
    for m in ms:
        if nv+len(m.vertices)>58000 or nf+len(m.faces)>58000:flush();part=[];nv=nf=0
        part.append(m);nv+=len(m.vertices);nf+=len(m.faces)
    flush()
def pitched(p,z,rise,axis=None):
    # Split on the ridge before triangulation, so each half is exactly planar.
    a,b,c,d=p.bounds;axis=axis or ('y' if d-b>c-a else 'x')
    mid=(a+c)/2 if axis=='y' else (b+d)/2;half=(c-a)/2 if axis=='y' else (d-b)/2
    cuts=[box(a-1,b-1,mid,d+1),box(mid,b-1,c+1,d+1)] if axis=='y' else [box(a-1,b-1,c+1,mid),box(a-1,mid,c+1,d+1)]
    ms=[]
    for cut in cuts:
        for q in polygons(p.intersection(cut)):
            m=extrusion(q,z,.12);h=rise*np.maximum(.001,1-abs(m.vertices[:,0 if axis=='y' else 1]-mid)/max(half,.1))
            top=m.vertices[:,2]>z+.06;m.vertices[top,2]+=h[top];ms.append(m)
    return ms
def facade(ms,p,z,h,levels,gothic=False,continuous=False,spacing=3.7):
    if current_design and optimized_facade(ms,p,z,h,levels,gothic,continuous,spacing,SimpleNamespace(**globals())):return
    # Windows are illustrative repeated bays, not measured facade openings.
    for ring in [p.exterior]+list(p.interiors):
        cc=np.asarray(ring.coords)
        for a,b in zip(cc[:-1],cc[1:]):
            v=b-a;length=np.linalg.norm(v)
            if length<3.7:continue
            u=v/length;n=np.array([u[1],-u[0]])
            for k in range(max(1,int(levels))):
                zz=z+(k+.23)*h/max(1,levels);wh=min(h/max(1,levels)*.56,8.5 if gothic else 2.8)
                if zz+wh>z+h-.25:continue
                nwin=max(1,int(length/spacing));ww=min(spacing*.48,2.0)
                if continuous:ww=length/nwin-.16
                for j in range(nwin):
                    c=a+u*((j+.5)*length/nwin)+n*.07
                    pts=[(-ww/2,0),(ww/2,0),(ww/2,wh*.73),(ww*.28,wh*.92),(0,wh),(-ww*.28,wh*.92),(-ww/2,wh*.73)] if gothic else [(-ww/2,0),(ww/2,0),(ww/2,wh),(-ww/2,wh)]
                    wm=trimesh.creation.extrude_polygon(Polygon(pts),.08,engine='earcut')
                    # local window plane X/Z; thickness points away from wall.
                    vv=wm.vertices.copy();wm.vertices=np.column_stack((c[0]+vv[:,0]*u[0]+vv[:,2]*n[0],c[1]+vv[:,0]*u[1]+vv[:,2]*n[1],zz+vv[:,1]))
                    trimesh.repair.fix_normals(wm);ms['DarkGlass' if gothic else 'Glass'].append(wm)
                    # slender mullion and stone sill
                    for off in [0]:
                        aa=(c[0]+off*u[0]+n[0]*.11,c[1]+off*u[1]+n[1]*.11,zz)
                        bb=(aa[0],aa[1],zz+wh);ms['LightStone' if gothic else 'Frame'].append(cylinder(aa,bb,.045,4))
def crenellations(ms,p,top,corner_height=2.0):
    a,b,c,d=p.bounds
    for x,y in [(a+.45,b+.45),(a+.45,d-.45),(c-.45,b+.45),(c-.45,d-.45)]:
        ms['LightStone'].append(boxmesh(x,y,top,1.0,1.0,corner_height))
    for aa,bb in zip(np.asarray(p.exterior.coords)[:-1],np.asarray(p.exterior.coords)[1:]):
        v=bb-aa;length=np.linalg.norm(v)
        for t in np.arange(1.2,length-1,2.3):
            q=aa+v*t/length;ms['Limestone'].append(boxmesh(*q,top,.8,.8,.8))

gothic_ids={151173251,151173255,153539618,154421807,154421809,154656512,154859382,155201128,155201131,155873096,156044638,156044639,156044642,156044643,156044644,156128079,156128082,156128083,156343655,156343656,156343657,156343662,156343665,157655066,157655067,157655069,157655071,157655073,157655074,157655090,150457341,143457513,191827364,191827365,191827367,191827368,191827370}
specialrefs={150457349:0,1228219576:1,157655069:2,159093828:3,194224828:4,125667497:5,152422729:6,441025431:7,143457513:8,156128082:9,152586235:10,10657061:11,11687839:12,387213841:13,143926554:14,143926548:15,152422458:16,142870150:17,152284260:18}
height_public={150457349:63.0936,1228219576:38.7858,159093828:10.668,156128082:41.148,152422729:51.816,441025431:52.0,387213841:35.6616,142771603:74.676}
level_overrides={150457349:1,194224828:5,152284260:3,142870150:5,143926548:2,152586235:2,10657061:15,11687839:16,143926554:4,152969810:4,153090078:4,153266965:4,152586232:4,442771900:7,1054042388:4,150456352:4,151173253:2,151173255:1,125667497:3}
shortnames={144636078:'Toyota Technological Institute',144063826:'Neubauer Collegium',144063830:'Institute of Politics',144062147:'5728 S. Woodlawn',477223630:'6054 S. Drexel / Campus South Parking',202690810:'Comer Hospital East Wing',143926548:'Edith Abbott Hall / Crown Family School',152586235:'Gerald Ratner Athletics Center',2054806:'Institute for the Study of Ancient Cultures',11687839:'Woodlawn Residential & Dining Commons'}
landmarks=set(specialrefs)
buildings.sort(key=lambda f:(-f['poly'].centroid.y,f['poly'].centroid.x))
for j,f in enumerate(buildings,1):
    i,p,t=f['id'],f['poly'],f['tags'];code=f'U{j:03d}'
    name=shortnames.get(i,t.get('name') or (t.get('addr:housenumber','')+' '+t.get('addr:street','')).strip() or f'Campus ancillary building {i}')
    x,y=p.centroid.x,p.centroid.y;a,b,c,d=p.bounds
    medical=t.get('building')=='hospital' or t.get('university_of_chicago:business_unit_name')=='BSD/UCH' or 'Medical Campus' in name or i in [144636083,145208633]
    zone='medical' if medical else ('north' if y>1035 else ('south' if y<440 else ('east' if x>755 else 'quads')))
    levels=None;floorbasis=''
    cr=city.get(t.get('chicago:building_id',''))
    if not cr:
        nearby=[(q.intersection(p).area,r) for q,r in cityshapes if q.bounds[0]<c and q.bounds[2]>a and q.bounds[1]<d and q.bounds[3]>b]
        if nearby:
            overlap,cr=max(nearby,key=lambda q:q[0]);cr=cr if overlap>p.area*.45 else None
    if i in level_overrides:levels=level_overrides[i];floorbasis='学校/项目资料层数；层高与局部标高估算'
    elif t.get('building:levels'):
        try:levels=float(t['building:levels']);floorbasis='OSM building:levels；层高估算'
        except ValueError:pass
    if levels is None and cr and float(cr.get('stories','0'))>0:levels=float(cr['stories']);floorbasis=f"芝加哥市 Building Footprints stories（记录 {cr['bldg_id']}）；层高估算"
    if levels is None:
        levels=1 if t.get('building') in ['industrial','garage'] or p.area<120 else (3 if p.area<500 else 4)
        floorbasis='未取得可靠层数/高度；按建筑功能与外形估算'
    gothic=i in gothic_ids or i in [1968186,1953426,1228219576,150457349]
    wall='Limestone' if gothic else ('Brick' if t.get('building') in ['house','residential','apartments','dormitory'] else 'LightStone')
    roof='Slate' if gothic else 'Metal'
    fh=3.2 if t.get('building') in ['dormitory','apartments','house','residential','hotel'] else 4.0
    h=max(4.0,levels*fh+.7)+(4.5 if gothic else 0)
    verified=i in height_public;basis=floorbasis;src=CITY_URL if cr else f'https://www.openstreetmap.org/{f["type"]}/{i}'
    if i in height_public:
        h=height_public[i];basis='公开资料最高高度；主体檐口、屋顶分区与立面细节为近似'
        src=refs['buildings'][specialrefs[i]]['sources'][0]['url'] if i in specialrefs else 'https://mchughconcrete.com/projects/university-of-chicago-hospital-center-for-care-discovery/'
    if i==11687839:h=184*.3048;basis='市政府PD43公开2018规划图：西楼184 ft，东/北/南楼94 ft；非竣工测量';src=PD_URL
    if i==152586235:h=30.48;basis='学校体育部桅杆峰值100 ft；另有125 ft构件报道；屋面高度估算';src=refs['buildings'][10]['sources'][0]['url']
    lay=code+'_'+name.replace('/','_').replace(':','_')[:85];layer(lay,wall)
    info={'Building':name,'Code':code,'Units':'meters','FootprintSource':f'https://www.openstreetmap.org/{f["type"]}/{i}','HeightBasis':basis,'GeometryDetail':'Exterior approximation; repeated facade bays are illustrative','GroundDatum':'relative Z=0, flattened terrain'}
    current_design=specification(i);optimization_facades={'window_groups':0}
    if i not in landmarks and not verified:
        basis='Source-informed exterior interpretation; local eave and roof heights are estimates. '+current_design['dimension_status']
        src=current_design['references'][0];info['HeightBasis']=basis;info['GeometryDetail']=current_design['evidence']
    ms={k:[] for k in COLORS};bodyidx=[0];construction_facades=[];detail_record=None;partition='公开平面轮廓、窗带、檐口与屋顶构造简化；窗位、层高及装饰为示意'
    def body(g,z,hh,mat=wall,windows=True,lev=None,arch=gothic,cont=False):
        for q in polygons(g):
            if hh<=.01:continue
            nm=code+f'B{bodyidx[0]:02d}';bodyidx[0]+=1
            native_extrude(q,z,hh,nm,lay,mat,info);push(nm,extrusion(q,z,hh),mat,lay,native=False)
            if windows:
                count=lev if lev is not None else max(1,round(hh/fh));construction_facades.append((q,z,hh,count,arch,cont));facade(ms,q,z,hh,count,arch,cont)
    def flat(g,z,mat=roof):
        for q in polygons(g):ms[mat].append(extrusion(q,z,.12))
    def gable(g,z,rise,axis=None,mat=roof):
        for q in polygons(g):ms[mat].extend(pitched(q,z,rise,axis))
    campus_refinement=rebuild_ordinary(i,p,h,levels,SimpleNamespace(**globals()))
    if campus_refinement:
        h=campus_refinement['height'];levels=campus_refinement['levels'];partition='; '.join(campus_refinement['features'])+'. Public-source exterior interpretation; local dimensions approximate.'
    elif i in REBUILT_HIGHLIGHTS:
        if i==1228219576:p=box(x-9.4488/2,y-10.668/2,x+9.4488/2,y+10.668/2)
        detail_record=rebuild_highlight(ms,p,i,h,body,SimpleNamespace(**globals()))
        partition='; '.join(detail_record['features'])+'. Public-source exterior reconstruction; member dimensions approximate.'
    elif i==157655069:
        # The great dining hall has tall Gothic windows and an open single
        # hall volume, rather than four classroom-storey window rows.
        h=19.8;levels=1;basis='Single great-hall storey and estimated Gothic roof elevations';info['HeightBasis']=basis;body(p,0,14.8,'Limestone',lev=1,arch=True);gable(p,14.8,5.0)
        for q in polygons(p):
            for aa,bb in zip(np.asarray(q.exterior.coords)[:-1],np.asarray(q.exterior.coords)[1:]):
                vv=bb-aa;ln=np.linalg.norm(vv)
                if ln<16:continue
                u=vv/ln;n=np.array([u[1],-u[0]])
                for dd in np.arange(2.2,ln-1.8,6.4):
                    center=aa+u*dd+n*.28;foot=Polygon([center-u*.48-n*.6,center+u*.48-n*.6,center+u*.48+n*.6,center-u*.48+n*.6]);ms['LightStone'].append(extrusion(foot,0,12.8));ms['Slate'].extend(pitched(foot,12.8,.8))
        partition='Single great-hall volume, tall pointed windows, stepped external buttresses and steep slate roof; official Tower Group references inform the form, while members and elevations remain approximate.'
    elif i==1228219576:
        # Use the historical published tower widths centered on the mapped position.
        p=box(x-9.4488/2,y-10.668/2,x+9.4488/2,y+10.668/2)
        body(p,0,h-2,lev=5);flat(p,h-2,'LightStone');crenellations(ms,p,h-2,2)
        partition='钟塔平面按历史官方9.4488×10.668m校准；角塔最高38.7858m；钟窗和城垛示意'
    elif i==156128082:
        towers=p.intersection(unary_union([box(a-1,b-1,a+15,d+1),box(c-15,b-1,c+1,d+1)]));middle=p.difference(towers)
        body(middle,0,24.5,lev=3);gable(middle,24.5,6.5,'x')
        for q in polygons(towers):body(q,0,h-3.5,lev=6);flat(q,h-3.5,'LightStone');crenellations(ms,q,h-3.5,3.5)
        partition='两端哥特式塔楼41.148m有历史官方来源；中央大厅、坡屋顶、小塔和窗位为形态近似'
    elif i==159093828:
        cx=515.7;cy=1102.3;rx=18.5;ry=35.3
        ellipse=affinity.scale(Point(cx,cy).buffer(1,quad_segs=32),rx,ry)
        body(p.difference(ellipse),0,3.2,'LightStone',lev=1);flat(p.difference(ellipse),3.2)
        # Closed thin ellipsoidal shell, with distinct approximate steel grid.
        rings=17;segments=72;verts=[];faces=[]
        for inner in [False,True]:
            for k in range(rings):
                th=(k/(rings-1))*(math.pi/2-.003)
                for l in range(segments):
                    ph=l/segments*2*math.pi;verts.append([cx+(rx-(.1 if inner else 0))*math.cos(th)*math.cos(ph),cy+(ry-(.1 if inner else 0))*math.cos(th)*math.sin(ph),(h-.085-(.12 if inner else 0))*math.sin(th)])
        n=rings*segments
        for off in [0,n]:
            for k in range(rings-1):
                for l in range(segments):
                    aa=off+k*segments+l;bb=off+k*segments+(l+1)%segments;cc=bb+segments;dd=aa+segments;faces.extend([[aa,bb,cc],[aa,cc,dd]])
        for k in [0,rings-1]:
            for l in range(segments):
                aa=k*segments+l;bb=k*segments+(l+1)%segments;faces.extend([[aa,aa+n,bb+n],[aa,bb+n,bb]])
        dome=trimesh.Trimesh(verts,faces);trimesh.repair.fix_normals(dome);push(code+'B99',dome,'Glass',lay,info=info)
        # The published lattice runs parallel to the ellipse axes, at roughly six-foot centers.
        for ax,ay in [(True,False),(False,True)]:
            radius=rx if ax else ry;other=ry if ax else rx
            for offset in np.arange(-radius+1.8288/2,radius,1.8288):
                extent=other*math.sqrt(max(0,1-(offset/radius)**2));pts=[]
                for cross in np.linspace(-extent,extent,32):
                    dx,dy=(offset,cross) if ax else (cross,offset)
                    zz=(h-.0762)*math.sqrt(max(0,1-(dx/rx)**2-(dy/ry)**2))
                    pts.append((cx+dx,cy+dy,zz))
                ms['Metal'].extend(cylinder(aa,bb,.0762,6) for aa,bb in zip(pts[:-1],pts[1:]))
        partition='椭圆玻璃网壳与入口连接体；最高10.668m有官方来源；网格约1.8288m采用官方6ft说明，轴长按地图近似，未将全馆73.152×36.576m直接套用穹顶'
    elif i==152422729:
        tower=p.intersection(box(a-1,b-1,a+27,b+29));low=p.difference(tower)
        body(low,0,10.5,'LightStone',lev=2,arch=False);flat(low,10.5)
        for yy in np.arange(b+30,d-5,10):gable(low.intersection(box(a-1,yy,c+1,yy+7)),10.5,1.8,'x')
        body(tower,0,h,'LightStone',lev=11,arch=False);flat(tower,h-.15)
        ms['Glass'].append(boxmesh(a+2,b+14,12,1,20,32));ms['Glass'].append(boxmesh(a+12,b-.12,28,19,.3,15))
        partition='西南石材塔楼51.816m有来源；低楼工作室、锯齿采光顶与大玻璃窗位置按形态近似'
    elif i==441025431:
        body(p,0,8,'Metal',lev=2,arch=False,cont=True);flat(p,8,'Metal')
        for k in range(4):
            zz=8+k*10.8;hh=(h-zz if k==3 else 10.8);cy0=408+[4,-2,3,0][k];ww=21+[1,-1,2,0][k]
            q=affinity.rotate(box(914-ww/2,cy0-22,914+ww/2,cy0+22),[0,4,-4,0][k],origin=(914,cy0))
            body(q,zz,hh,'Metal',lev=2,arch=False,cont=True);flat(q,zz+hh-.13,'Metal')
        partition='双层底座与4组错位会场塔段；最高52m采用竣工案例；各段宽度、标高与折面简化'
    elif i==10657061:
        regions=[(box(a-1,1394,706,d+1),50.3,15),(box(676,b-1,c+1,1394),37.5,11),(box(a-1,b-1,676,1394),18.5,5)]
        for cut,hh,ll in regions:
            q=p.intersection(cut);body(q,0,hh,'WhitePanel',lev=ll,arch=False);flat(q,hh,'Garden')
        h=50.3;partition='三组白色住宅塔及庭院；5/11/15层有资料，50.3/37.5/18.5m及分界位置估算；窗框重复表达'
    elif i==11687839:
        high=p.intersection(box(a-1,b-1,798,313));rest=p.difference(high)
        body(rest,0,94*.3048,'WhitePanel',lev=7,arch=False);flat(rest,94*.3048)
        body(high,0,h,'WhitePanel',lev=16,arch=False);flat(high,h)
        partition='西楼184ft=56.0832m、其他楼94ft=28.6512m，依据市PD43 2018规划尺寸；层间分缝、机房与分界近似'
    elif i==125667497:
        h=10.5;body(p,0,5.9,'Brick',lev=2,arch=False)
        gable(p.buffer(1.6,join_style=2),5.9,1.15,'x','Tile')
        upper=p.intersection(box(920,b-1,936,d+1));body(upper,6.9,2.4,'Brick',lev=1,arch=False);gable(upper.buffer(.9,join_style=2),9.3,.9,'x','Tile')
        ms['Brick'].append(boxmesh(927,861,5,2.8,3.1,5.5));partition='砖墙、低坡悬挑屋檐、上层卧室与核心烟囱；高度/悬挑近似，未完成HABS测绘复建';basis='公开地图平面及Frank Lloyd Wright Trust外形；高度10.5m估算'
    elif i==152586235:
        body(p,0,10.5,'LightStone',lev=2,arch=False);flat(p,10.5,'Metal')
        for yy,xx in [(1288,452),(1330,456),(1370,453),(1400,445),(1354,392)]:
            tip=(xx-5,yy,30.48);ms['Metal'].append(cylinder((xx,yy,0),tip,.35,10))
            for dx,dy in [(-44,0),(0,24),(0,-24)]:ms['Frame'].append(cylinder(tip,(xx+dx,yy+dy,10.7),.065,5))
        partition='低矮体育馆、5根外部桅杆与斜拉索；桅杆峰顶采用体育部30.48m，屋面10.5m及曲面/倾角近似'
    elif i==152422458:
        library=p.intersection(box(635,b-1,691,363));low=p.difference(library)
        body(low,0,9.2,'LightStone',lev=2,arch=False,cont=True);flat(low,9.2)
        body(library,0,25.5,'LightStone',lev=6,arch=False,cont=True);flat(library,25.5);h=25.5
        partition='6层法学图书馆与低楼教学翼区分，折面幕墙与北侧反射水池示意；整体高度估算'
    elif i==152284260:
        lower=p.buffer(-3.3528,join_style=2);body(lower,0,10.3,'Limestone',lev=2,arch=False);body(p,10.3,4.7,'Limestone',lev=1,arch=False);flat(p,15);h=15
        partition='最高层3.3528m悬挑采用官方描述；3层地上体块与天窗简化，高度15m估算'
    elif i==142771603:
        body(p,0,55,'LightStone',lev=10,arch=False,cont=True);flat(p,55)
        plant=p.buffer(-12,join_style=2).intersection(box(a+8,b+15,c-8,d-15))
        body(plant,55,h-55,'Metal',windows=False);flat(plant,h-.12)
        partition='施工方公开最高245 ft（74.676m）；设计方5.5m层高×10层形成55m主体，退台机房达最高点。机房边界及立面划分近似'
    elif i==387213841:
        body(p,0,29,'LightStone',lev=5,arch=False,cont=True);flat(p,29)
        plant=p.buffer(-5,join_style=2).intersection(box(a-1,b+20,c+1,d-12));body(plant,29,h-29,'Metal',windows=False);flat(plant,h-.12)
        partition='玻璃科研楼、局部屋顶机房；整体35.6616m有结构工程师来源；机房范围与幕墙模数近似'
    elif i==194224828:
        body(p,0,23.5,'Limestone',lev=5,arch=False);flat(p,23.5)
        pent=p.buffer(-12,join_style=2);body(pent,23.5,3.2,'Metal',windows=False);flat(pent,26.7);h=26.7
        partition='保留错位、竖槽与凸窗平面，5个地上层+屋顶机房；全高26.7m及机房范围估算'
    elif i==143926554:
        body(p,0,12.4,'LightStone',lev=3,arch=False);flat(p,12.4,'Garden')
        sky=p.buffer(-10,join_style=2);body(sky,12.4,4.0,'Glass',lev=1,arch=False,cont=True);flat(sky,16.4);h=16.4
        for xx in np.arange(a+2,c-1,4.5):
            for yy in [b+.3,d-.3]:ms['LightStone'].append(cylinder((xx,yy,0),(xx,yy,12.7),.23))
        for yy in np.arange(b+3,d-1,4.5):
            for xx in [a+.3,c-.3]:ms['LightStone'].append(cylinder((xx,yy,0),(xx,yy,12.7),.23))
        for xx in np.arange(a+8,c-8,4):ms['Solar'].append(boxmesh(xx,b+7,12.7,3,4,.17))
        partition='3层柱廊主体+退台第4层、绿屋顶和太阳能板；16.4m、柱位及檐棚示意'
    elif i==143926548:
        h=9.0;body(p,0,h,'Brick',lev=2,arch=False,cont=True);flat(p,h,'Frame');partition='Mies水平砖/钢/玻璃体量；窗带与黑色边框简化，高度9m估算'
    elif i==477223630:
        garage=next(f0['poly'] for f0 in features if f0['id']==477223629);body(p.difference(garage),0,16.7,lev=4,arch=False);body(garage,0,29.5,'Concrete',lev=9,arch=False,cont=True);flat(p.difference(garage),16.7);flat(garage,29.5);h=29.5
        partition='同一建筑分离4层办公翼与9层停车库；16.7/29.5m为层高估算'
    else:
        rise=min(5.5,h*.22) if gothic else 0;bh=h-rise
        body(p,0,bh,lev=max(1,int(levels)),arch=gothic)
        if rise:gable(p,bh,rise)
        else:
            flat(p,h-.13)
            for q in polygons(p.boundary.buffer(.19,join_style=2).intersection(p)):ms[wall].append(extrusion(q,h-.5,.65))
        if i==143457513:
            q=p.intersection(box(a+4,b-1,a+17,d+1));body(q,0,h+7,lev=6);flat(q,h+7);crenellations(ms,q,h+7,1.5);h+=8.5
            partition='旧教堂主体、坡屋顶与西端入口塔、现代连接亭；高度与具体塔位为估算'
    ordinary_stats=None
    if i not in landmarks:
        ordinary_stats=finish_ordinary(p,h,levels,gothic,SimpleNamespace(**globals()),campus_refinement['profile']if campus_refinement else None)
    highlight_stats=None
    if i in landmarks:
        joinery,highlight_stats=detailed_joinery(ms,p,0,h,SimpleNamespace(**globals()),gothic=gothic)
        for kk,(mm,parts)in enumerate(joinery.items()):
            if parts:chunk_meshes(code+f'HD{kk:02d}',parts,mm,lay,info)
    # One mesh per material per building; Rhino layer contains native body solids plus editable detail meshes.
    for k,(mat,parts) in enumerate(ms.items()):
        if parts:chunk_meshes(code+f'D{k:02d}',parts,mat,lay,info)
    for q in polygons(p):
        crv=rh.PolylineCurve([rh.Point3d(float(xx),float(yy),0) for xx,yy in q.exterior.coords]);model.Objects.AddCurve(crv,attr(code+'_PLAN',lay,wall,info))
    bounds=np.vstack([o['mesh'].bounds for o in objects if layer_map[o['name']]['layer']==lay])
    actualh=float(bounds[:,2].max())
    r={'code':code,'name':name,'layer':lay,'osm_id':i,'osm_type':f['type'],'zone':zone,'landmark':i in landmarks,'height':round(actualh,4),'height_status':'published' if verified else ('planning' if i==11687839 else 'estimated'),'levels':levels,'area':round(p.area,2),'width':round(p.bounds[2]-p.bounds[0],2),'depth':round(p.bounds[3]-p.bounds[1],2),'center':[round(x,3),round(y,3)],'basis':basis,'partition':partition,'source':src,'footprint_source':info['FootprintSource'],'campus_refinement':campus_refinement,'exterior_reconstruction':detail_record,'ordinary_joinery':ordinary_stats,'highlight_joinery':highlight_stats,'architecture_reference':refs['buildings'][specialrefs[i]] if i in specialrefs else None,'optimization_2026_10_18':current_design}
    records.append(r)
    f['record']=r
print('Buildings',len(records),'native solids',native_count,flush=True)

# Map elevated connections to the closest connected building rather than inventing extra buildings.
bridge_records=[]
# Connector windows keep their established shared design, independent of the
# final ordinary building recipe (which otherwise leaks into this later pass).
current_design=None
for k,f in enumerate(connectors):
    p=f['poly'];t=f['tags'];parent=min(buildings,key=lambda b:(b['poly'].distance(p),-b['poly'].intersection(p.buffer(.4)).area))
    lay=parent['record']['layer'];code=parent['record']['code']
    try:z=float(t.get('min_height',float(t.get('level','1'))*4.8))
    except ValueError:z=4.8
    hh=3.8;details={mat:[] for mat in COLORS}
    info={'Building':parent['record']['name'],'Source':f'https://www.openstreetmap.org/way/{f["id"]}','GeometryDetail':'Mapped raised connector; clearance and roof height are estimated','Units':'meters'}
    for qn,q in enumerate(polygons(p)):
        nm=f'{code}C{k:02d}{qn:01d}';native_extrude(q,z,hh,nm,lay,'LightStone',info);push(nm,extrusion(q,z,hh),'LightStone',lay,native=False)
        facade(details,q,z,hh,1,False,True)
    for n,(mat,parts) in enumerate(details.items()):
        if parts:chunk_meshes(f'{code}K{k:X}{n:X}',parts,mat,lay,info)
    bridge_records.append({'osm_id':f['id'],'parent_code':code,'clearance_m':z,'depth_m':hh,'basis':'Mapped footprint; vertical dimensions estimated'})
(OUT/'elevated_connections.json').write_text(json.dumps(bridge_records,indent=2))

# Landscape uses mapped boundaries and circulation; small features share the environment layer.
xml=ET.parse(ROOT/'sources/osm_map.osm').getroot();nodes={};ntags={}
for n in xml.findall('node'):
    ii=int(n.get('id'));xx,yy=project(float(n.get('lon')),float(n.get('lat')));nodes[ii]=(float(xx),float(yy));ntags[ii]={t.get('k'):t.get('v') for t in n.findall('tag')}
ways=[]
for w in xml.findall('way'):
    cs=[nodes[int(n.get('ref'))] for n in w.findall('nd') if int(n.get('ref')) in nodes]
    if len(cs)>1:ways.append({'id':int(w.get('id')),'coords':cs,'tags':{t.get('k'):t.get('v') for t in w.findall('tag')}})
footprints=unary_union([f['poly'] for f in buildings]);eg={k:[] for k in COLORS};road_records=[]
def env(g,z,hh,mat):
    for q in polygons(set_precision(g.buffer(0),.002).buffer(0)):
        q=q.simplify(.04,preserve_topology=True)
        if q.area>.06:eg[mat].append(extrusion(q,z,hh))
env(scope,-1.0,1.0,'Ground')
road=[];walk=[]
widths={'primary':17,'secondary':13,'tertiary':11,'residential':9,'unclassified':8,'service':5,'footway':2.1,'path':2.0,'pedestrian':4.5,'cycleway':2.2}
for w in ways:
    t=w['tags'];hw=t.get('highway')
    if hw not in widths:continue
    line=LineString(w['coords'])
    if not line.intersects(scope):continue
    try:width=float(t.get('width','').replace(' m',''))
    except ValueError:width=widths[hw]
    g=line.buffer(width/2,cap_style=2,join_style=2).intersection(scope).difference(footprints)
    (walk if hw in ['footway','path','pedestrian','cycleway'] else road).append(g)
    road_records.append({'osm_id':w['id'],'name':t.get('name',hw),'width_m':width,'basis':'OSM width' if 'width' in t else '示意宽度；未实测'})
roadarea=unary_union(road).buffer(0);walkarea=unary_union(walk).difference(roadarea).buffer(0)
env(roadarea,.025,.055,'Road');env(walkarea,.055,.065,'Walk')
kerb=roadarea.buffer(1.8,join_style=2).difference(roadarea).difference(footprints).intersection(scope).buffer(0);env(kerb,.065,.07,'Walk')
green=[];gardens=[];sport=[];tracks=[];parking=[];water=[]
for f in features:
    p,t=f['poly'],f['tags']
    if not p.intersects(scope):continue
    g=p.intersection(scope,grid_size=.02).buffer(0)
    for mask in [footprints,roadarea,walkarea,kerb]:g=g.difference(mask,grid_size=.02).buffer(0)
    if t.get('leisure')=='pitch':sport.append((g,t))
    elif t.get('leisure')=='track':tracks.append(g)
    elif t.get('natural')=='water':water.append(g)
    elif t.get('amenity')=='parking':parking.append(g)
    elif t.get('leisure')=='garden':gardens.append(g)
    elif t.get('leisure')=='park' or t.get('landuse') in ['grass','recreation_ground']:green.append(g)
for f in buildings:
    for q in polygons(f['poly']):
        for ring in q.interiors:green.append(Polygon(ring).buffer(-2))
sports=unary_union([g for g,t in sport]);trackarea=unary_union(tracks).difference(sports)
athletic_plan=athletic_layout(SimpleNamespace(**globals()))
trackarea=trackarea.difference(athletic_plan['original'].buffer(3)).union(athletic_plan['track'])
greenarea=unary_union(green).difference(sports).difference(trackarea).difference(unary_union(parking))
gardenarea=unary_union(gardens).difference(greenarea)
env(greenarea,.10,.07,'Grass');env(gardenarea,.12,.08,'Garden');env(trackarea,.105,.045,'Track')
env(unary_union(parking),.085,.035,'Road');env(unary_union(water),.12,.02,'Water')
from parking_detail import parking_detail
parking_paint=parking_detail(ROOT,scope,footprints,unary_union(green+gardens).difference(unary_union(parking)))
env(parking_paint,.137,.014,'Marking')
for g,t in sport:
    if athletic_handles(g,t):continue
    mat='Court' if t.get('sport')=='tennis' else 'Grass';env(g,.13,.035,mat)
    for q in polygons(g):
        env(q.boundary.buffer(.065).intersection(q),.167,.012,'Marking')
        aa,bb,cc,dd=q.bounds
        if 'soccer' in t.get('sport',''):
            env(LineString([((aa+cc)/2,bb),((aa+cc)/2,dd)]).buffer(.05).intersection(q),.167,.012,'Marking')
            env(Point(q.centroid).buffer(9).boundary.buffer(.06).intersection(q),.167,.012,'Marking')
        if t.get('sport')=='tennis':
            yc=(bb+dd)/2;eg['Furniture'].append(boxmesh((aa+cc)/2,yc,.17,cc-aa,.08,1.0))
# MainQuad lawns are cut by real mapped paths; add conservative edges along footpaths.
env(walkarea.boundary.buffer(.09).difference(footprints).intersection(scope),.12,.015,'Paving')
# Law School reflecting pool: public architectural feature, approximate outline.
pool=box(624,375,680,397).difference(footprints).difference(walkarea)
env(pool,.15,.04,'Water');env(pool.buffer(1.0).difference(pool).difference(footprints),.14,.12,'Paving')
# Benches along selected paths, campus lights, and mapped/illustrative trees.
for xx in np.arange(542,713,28):
    for yy in [789,885]:
        pp=Point(xx,yy)
        if not footprints.buffer(2).contains(pp):eg['Furniture'].append(boxmesh(xx,yy,.35,2.0,.55,.15))
trees=[];mapped_trees=0
safe_green=unary_union([greenarea,gardenarea]).difference(footprints.buffer(3)).buffer(-2)
def tree_point(xx,yy):
    if athletic_plan['tree_exclusion'].covers(Point(xx,yy)):return False
    if scope.contains(Point(xx,yy)) and not footprints.buffer(3).contains(Point(xx,yy)) and not roadarea.buffer(1).contains(Point(xx,yy)) and all((xx-a)**2+(yy-b)**2>45 for a,b in trees):trees.append((xx,yy));return True
for ii,t in ntags.items():
    if t.get('natural')=='tree' and tree_point(*nodes[ii]):mapped_trees+=1
for w in ways:
    if w['tags'].get('natural')=='tree_row':
        line=LineString(w['coords'])
        if not line.intersects(scope):continue
        for ds in np.arange(3,line.length,12):
            q=line.interpolate(ds)
            if safe_green.buffer(1).contains(q):tree_point(q.x,q.y)
rng=np.random.default_rng(17043)
for xx in np.arange(90,1480,19):
    for yy in np.arange(170,1435,19):
        tx,ty=xx+rng.uniform(-5,5),yy+rng.uniform(-5,5);p0=Point(tx,ty)
        # Keep central quad and sport lawns open, plant chiefly their edges.
        openlawn=box(537,797,724,880).contains(p0) or sports.buffer(4).contains(p0)
        if safe_green.contains(p0) and not openlawn and (p0.distance(safe_green.boundary)<15 or 440<ty<635):tree_point(tx,ty)
for xx,yy in trees:
    hh=rng.uniform(7,10);rad=rng.uniform(2.8,4.3)
    eg['Trunk'].append(cylinder((xx,yy,.1),(xx,yy,hh*.63),.2,6))
    m=trimesh.creation.icosphere(subdivisions=1);m.apply_scale((rad,rad,hh*.41));m.apply_translation((xx,yy,hh*.65));eg['Leaves'].append(m)
for yy in np.arange(450,635,35):
    for xx in [486,752,886]:
        if not roadarea.contains(Point(xx,yy)) and scope.contains(Point(xx,yy)):
            eg['Furniture'].append(cylinder((xx,yy,.1),(xx,yy,4.3),.07,6));eg['LightStone'].append(boxmesh(xx,yy,4.3,.35,.35,.28))
# Dashed lane lines are illustrative; positions derive from public centerlines.
for w in ways:
    if w['tags'].get('highway') not in ['tertiary','secondary','primary','residential'] or not w['tags'].get('name'):continue
    line=LineString(w['coords'])
    if not line.intersects(scope):continue
    for ds in np.arange(2,line.length-3,12):
        seg=LineString([line.interpolate(ds),line.interpolate(ds+3)])
        env(seg.buffer(.06,cap_style=2).intersection(roadarea),.082,.012,'Marking')
athletic_refinement=refine_athletic_fields(SimpleNamespace(**globals()),athletic_plan)
(OUT/'athletic_fields_refinement.json').write_text(json.dumps(athletic_refinement,indent=2)+'\n')
landscape_refinement=refine_landscape(SimpleNamespace(**globals()))
(OUT/'campus_landscape_refinement.json').write_text(json.dumps(landscape_refinement,indent=2))
for k,(mat,parts) in enumerate(eg.items()):
    if parts:chunk_meshes(f'E{k:02d}',parts,mat,'环境_Environment',{'Landscape':'Mapped boundaries and centerlines; approximate tree planting, surface levels, road widths','Units':'meters'})

for name,location,direction in [('校园鸟瞰',(1700,-600,1400),(-950,1450,-1380)),('主四合院',(1180,340,440),(-570,520,-420)),('总平面',(760,800,2400),(0,0,-1))]:
    vv=rh.ViewInfo();vv.Name=name;vv.Viewport.SetCameraLocation(rh.Point3d(*location));vv.Viewport.SetCameraDirection(rh.Vector3d(*direction));vv.Viewport.SetCameraUp(rh.Vector3d(0,1,0) if name=='总平面' else rh.Vector3d(0,0,1));vv.Viewport.TargetPoint=rh.Point3d(730,800,15);vv.Viewport.ChangeToParallelProjection(True);vv.Viewport.SetFrustum(-800,800,-700,700,1,6000);model.NamedViews.Add(vv)
model.Strings['ModelNotes']='Hyde Park exterior approximation. Unit meters. Each mapped building is a separate layer; all outdoor geometry is on 环境_Environment. Heights: published / planning / estimated. Repeated windows, roofs, landscaping and flattened ground are illustrative. Not an official university BIM or survey.'
assert model.Write(str(OUT/'UChicago_HydePark_Layered.3dm'),7)
from campus_exchange import export_scene
export_scene(ROOT,objects,COLORS,layer_map,records)
def chunk(tag,data=b''):return struct.pack('<HI',tag,len(data)+6)+data
def zs(s):return s.encode('ascii')+b'\0'
def rgb(c):return chunk(0x0011,bytes(c))
mb=b''
for name,co in COLORS.items():mb+=chunk(0xAFFF,chunk(0xA000,zs(name))+chunk(0xA010,rgb(tuple(int(v*.5) for v in co)))+chunk(0xA020,rgb(co))+chunk(0xA030,rgb((10,10,10))))
ob=b''
for o in objects:
    m=o['mesh'];v=np.asarray(m.vertices,dtype='<f4');ff=np.column_stack((m.faces,np.full(len(m.faces),7))).astype('<u2')
    fc=struct.pack('<H',len(ff))+ff.tobytes()+chunk(0x4130,zs(o['mat'])+struct.pack('<H',len(ff))+np.arange(len(ff),dtype='<u2').tobytes())+chunk(0x4150,np.zeros(len(ff),dtype='<u4').tobytes())
    ob+=chunk(0x4000,zs(o['name'])+chunk(0x4100,chunk(0x4110,struct.pack('<H',len(v))+v.tobytes())+chunk(0x4120,fc)))
(OUT/'UChicago_HydePark.3ds').write_bytes(chunk(0x4D4D,chunk(0x0002,struct.pack('<I',3))+chunk(0x3D3D,chunk(0x3D3E,struct.pack('<I',3))+chunk(0x0100,struct.pack('<f',1))+mb+ob)))
(OUT/'layer_map.json').write_text(json.dumps(layer_map,ensure_ascii=False,indent=2))
(OUT/'palette.json').write_text(json.dumps(COLORS))
(OUT/'buildings.json').write_text(json.dumps(records,ensure_ascii=False,indent=2))
with (OUT/'building_dimensions_and_sources.csv').open('w',encoding='utf-8-sig',newline='') as fd:
    keys=[k for k in records[0] if k!='architecture_reference'];wr=csv.DictWriter(fd,fieldnames=keys,extrasaction='ignore');wr.writeheader();wr.writerows(records)
with (OUT/'road_widths_and_sources.csv').open('w',encoding='utf-8-sig',newline='') as fd:
    wr=csv.DictWriter(fd,fieldnames=list(road_records[0]));wr.writeheader();wr.writerows(road_records)
(OUT/'footprints_local_meters.geojson').write_text(json.dumps({'type':'FeatureCollection','coordinate_system':{'epsg':32616,'origin_easting':OX,'origin_northing':OY,'origin_wgs84':[LON,LAT],'unit':'m','note':'Local projected meters, not RFC7946 longitude/latitude'},'features':[{'type':'Feature','properties':f['record'],'geometry':mapping(f['poly'])} for f in buildings]},ensure_ascii=False))
av=[];af=[];co=[];off=0
for m,mat in meshdata:av.append(m.vertices);af.append(m.faces+off);co.extend([COLORS[mat]]*len(m.faces));off+=len(m.vertices)
np.savez_compressed(OUT/'preview_mesh_data.npz',vertices=np.vstack(av),faces=np.vstack(af),colors=np.asarray(co,dtype=np.uint8))
summary={'buildings':len(records),'layers':len(model.Layers),'environment_layer':'环境_Environment','native_closed_solids':native_count,'objects_3ds':len(objects),'vertices':off,'triangles':sum(len(m.faces) for m,_ in meshdata),'trees':len(trees),'mapped_tree_points':mapped_trees,'landmarks':sum(r['landmark'] for r in records),'published_height_buildings':sum(r['height_status']=='published' for r in records),'planning_height_buildings':sum(r['height_status']=='planning' for r in records),'estimated_height_buildings':sum(r['height_status']=='estimated' for r in records),'unit':'meters','crs':'EPSG:32616 local offsets','origin_wgs84':[LON,LAT],'origin_utm':[OX,OY],'bounds':scope.bounds,'terrain':'Flattened relative Z=0; no surveyed terrain','campus_ordinary_buildings_refined':sum(bool(r.get('ordinary_joinery'))for r in records),'individual_campus_profiles':sum(bool(r.get('campus_refinement'))for r in records),'accuracy':'Public footprints, selective published heights, approximate exterior details. Not survey-certified.'}
(OUT/'model_summary.json').write_text(json.dumps(summary,ensure_ascii=False,indent=2));print(json.dumps(summary,ensure_ascii=False,indent=2))
