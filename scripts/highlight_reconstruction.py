"""Individual highlight corrections after the architectural form audit.

Primary owner/architect references are recorded beside each reconstruction.
Source plans remain authoritative; member sizes are photo interpretations.
"""
import math
from rockefeller_chapel import rebuild as rebuild_rockefeller, FEATURES as ROCKEFELLER_FEATURES, REFERENCE as ROCKEFELLER_REFERENCE
import numpy as np
import trimesh
from shapely.geometry import box,Polygon,Point,LineString
from shapely.ops import unary_union
from shapely import segmentize

REFS={150457349:ROCKEFELLER_REFERENCE,125667497:'https://flwright.org/explore/frederick-c-robie-house',152586235:'https://architecture.uchicago.edu/locations/gerald_ratner_athletics_center/',142870150:'https://architecture.uchicago.edu/locations/gordon_center_for_integrative_science/',152284260:'https://www.lib.uchicago.edu/crerar/about-crerar-library/history/',1228219576:'https://architecture.uchicago.edu/locations/tower_group_mitchell_tower_hutchinson_commons_reynolds_club_mandel_hall/'}
FEATURES={
150457349:ROCKEFELLER_FEATURES,125667497:['long Roman-brick living/dining bar','deep low hipped clay eaves with limestone fascia','24 art-glass door bays along the south balcony','upper bedroom mass','central chimney','brick terraces, parapets and urns'],
152586235:['two sports halls and lower round entrance lobby','continuous flattened S-curve metal roofs','inclined glazed end walls','five leaning mast pairs','120 roof-attached stay cables','clerestory bands and standing seams'],
142870150:['separate limestone research wings','tall glazed eastern hinge atrium','open ground-level breezeway','six-storey-height steel colonnade','glazed upper bridge and limestone canopy'],
152284260:['three above-ground library levels','11-foot upper-floor cantilever','vertical narrow concrete window bays','central atrium roof lantern','2018 roof skylights'],
1228219576:['square limestone Gothic tower','true open ground-level cross passage','deep bell-stage arches','four corner turrets','crenellated parapet','paired narrow Gothic lights']}

def rebuild(ms,p,ident,h,body,t):
    if ident==150457349:return rebuild_rockefeller(ms,p,h,body,t)
    a,b,c,d=p.bounds;x,y=p.centroid.coords[0]
    def add(g,z,height,mat):
        for q in t.polygons(g):ms[mat].append(t.extrusion(q,z,height))
    def line(aa,bb,z,height,w=.12,mat='Frame'):add(LineString([aa,bb]).buffer(w/2,cap_style=2),z,height,mat)
    def pane(aa,bb,z,height,n,frame='Frame',width=1.4):
        aa,bb,n=np.array(aa),np.array(bb),np.array(n);ln=np.linalg.norm(bb-aa);u=(bb-aa)/ln;nn=n*.10
        add(Polygon([aa+nn,bb+nn,bb+nn*2,aa+nn*2]),z,height,'DarkGlass')
        for zz in [z,z+height]:line(aa+nn*2,bb+nn*2,zz,.07,.09,frame)
        for dd in np.linspace(0,ln,max(2,int(ln/width)+1)):
            cc=aa+u*dd+nn*2;line(cc-u*.035,cc+u*.035,z,height,.09,frame)
    def hipped(q,z,rise,mat='Tile'):
        for pp in t.polygons(q):
            aa,bb,cc,dd=pp.bounds;xm=(aa+cc)/2;ym=(bb+dd)/2;hh=(dd-bb)/2;rl=min(cc-aa,dd-bb)/2
            faces=[[(aa,bb),(cc,bb),(cc-rl,ym),(aa+rl,ym)],[(aa,dd),(aa+rl,ym),(cc-rl,ym),(cc,dd)],[(aa,bb),(aa+rl,ym),(aa,dd)],[(cc,bb),(cc,dd),(cc-rl,ym)]]
            for face in faces:
                for part in t.polygons(pp.intersection(Polygon(face))):
                    mesh=t.extrusion(part,z,.14);v=mesh.vertices;up=v[:,2]>z+.07;delta=np.clip(np.minimum(1-abs(v[:,1]-ym)/max(hh,.1),np.minimum(v[:,0]-aa,cc-v[:,0])/max(rl,.1)),0,1);mesh.vertices[up,2]+=rise*delta[up];trimesh.repair.fix_normals(mesh);ms[mat].append(mesh)
    def coping(q,z,mat='LightStone'):
        add(q.buffer(.08,join_style=2).difference(q.buffer(-.16,join_style=2)),z,.14,mat)
    def panel(profile,c,u,n,zz,thick,mat):
        c,u,n=np.array(c),np.array(u),np.array(n)
        for q in t.polygons(profile):
            m=t.extrusion(q,0,thick);v=m.vertices.copy();m.vertices=np.column_stack([c[0]+u[0]*v[:,0]+n[0]*v[:,2],c[1]+u[1]*v[:,0]+n[1]*v[:,2],zz+v[:,1]]);trimesh.repair.fix_normals(m);ms[mat].append(m)
    if ident==125667497:
        # Main south living/dining range is long and low. The smaller top floor
        # is a bedroom volume, not a third full-footprint rectangular storey.
        living=p.intersection(box(a-1,b-1,935.6,863.0));service=p.difference(living)
        body(living,0,6.65,'Brick',windows=False);body(service,0,5.65,'Brick',windows=False)
        for q,z in [(living,6.65),(service,5.65)]:
            eave=q.buffer(1.65,join_style=2);add(eave,z,.18,'LightStone');hipped(eave,z+.18,.95)
        upper=p.intersection(box(919.2,857.7,932.0,866.5));body(upper,7.4,2.1,'Brick',windows=False);hipped(upper.buffer(1.35,join_style=2),9.5,.78)
        for zz in [.55,2.7,6.20]:
            for q in t.polygons(p):coping(q,zz)
        # Long south balcony, with the documented 24 leaded-glass door groups.
        left,right=914.0,914.0+47*.3048;yy=853.0;step=(right-left)/24
        for k in range(24):
            xx=left+(k+.5)*step;section=p.intersection(LineString([(xx,b-2),(xx,d+2)]));yy=section.bounds[1]-.05;pane((xx-step*.45,yy),(xx+step*.45,yy),3.45,2.53,(0,-1),width=.34)
            # Slender geometric art-glass divisions, repeated at the real bays.
            for zz in [4.0,5.5]:line((xx-step*.40,yy-.23),(xx+step*.40,yy-.23),zz,.035,.04,'Frame')
        balcony=box(907.2,851.25,935.6,853.1);add(balcony,3.03,.22,'LightStone')
        parapet=box(907.2,850.85,935.6,851.30);add(parapet,3.25,.72,'Brick');coping(parapet,3.97)
        for xx in [907.4,935.4]:add(box(xx-.3,851.0,xx+.3,853.1),0,3.24,'Brick')
        for yy0,normal in [(866.55,(0,1)),(857.65,(0,-1))]:
            for xx in np.arange(920.0,931.5,1.4):pane((xx-.46,yy0),(xx+.46,yy0),7.75,1.48,normal,width=.48)
        # Ground-floor and rear/service glazing follows each exposed plan
        # edge. The long south art-glass run above remains its own assembly.
        for q in t.polygons(p):
            for aa,bb in zip(np.asarray(q.exterior.coords)[:-1],np.asarray(q.exterior.coords)[1:]):
                length=np.linalg.norm(bb-aa)
                if length<2.8:continue
                u=(bb-aa)/length;n=np.array([u[1],-u[0]]);count=max(1,int(length/2.0))
                for k in range(count):
                    cc=aa+u*(k+.5)*length/count
                    pane(cc-u*.62,cc+u*.62,.85,1.10,n,width=.62)
                    if not(n[1]<-.65 and 913<cc[0]<929):pane(cc-u*.64,cc+u*.64,3.5,2.05,n,width=.64)
                # Recessed horizontal Roman-brick joints retain the broad
                # masonry planes without a dense applied surface texture.
                for zz in np.arange(.35,6.25,.43):line(aa+n*.025,bb+n*.025,zz,.018,.035,'Limestone')
        chimney=box(923.8,858.4,927.7,861.4);add(chimney,0,10.7,'Brick');coping(chimney,10.7)
        # Terraces and garden walls emphasize Wright's horizontal datum.
        terrace=box(902.8,851.0,909.6,862.2);add(terrace,0,.35,'Paving')
        for aa,bb in [((903.0,850.9),(919.0,850.9)),((902.9,851),(902.9,863))]:
            line(aa,bb,0,1.15,.38,'Brick');line(aa,bb,1.15,.15,.48,'LightStone')
        for xx,yy0 in [(904,852),(933.2,851)]:
            ms['LightStone'].append(t.cylinder((xx,yy0,1.25),(xx,yy0,1.75),.62,16));ms['Limestone'].append(t.cylinder((xx,yy0,1.75),(xx,yy0,1.94),.85,16))
        stats={'south_art_glass_bays':24,'deep_eaves_m':1.65}
    elif ident==152586235:
        halls=[p.intersection(box(a-1,b-1,c+1,1302)),p.intersection(box(a-1,1353,c+1,d+1))];rotunda=p.intersection(Point(439.7,1343).buffer(15.2,quad_segs=40));commons=p.difference(unary_union(halls))
        body(commons.difference(rotunda),0,6.5,'Brick',lev=1,arch=False);body(rotunda,0,8.7,'Brick',windows=False)
        add(commons.difference(rotunda),6.5,.16,'Metal');add(rotunda,8.7,.16,'Metal');coping(rotunda,8.86)
        roof_functions=[]
        for hall in halls:
            aa,bb,cc,dd=hall.bounds;mid=(aa+cc)/2;span=cc-aa
            def rz(xx,yy,mid=mid,span=span):return 11.2+2.0*np.sin((np.asarray(xx)-mid)/span*math.pi*1.35)
            roof_functions.append(rz);body(hall,0,8.8,'Brick',windows=False)
            for xx in np.arange(aa,cc,4):
                for yy in np.arange(bb,dd,5):
                    for q in t.polygons(segmentize(hall.intersection(box(xx,yy,xx+4,yy+5)),2)):
                        m=t.extrusion(q,0,.18);m.vertices[:,2]+=rz(m.vertices[:,0],m.vertices[:,1]);trimesh.repair.fix_normals(m);ms['Metal'].append(m)
            # Sloped glass wall panels connect the low base to each curved eave.
            for face_y,sign in [(bb,-1),(dd,1)]:
                for xx in np.arange(aa+.4,cc-1,2.0):
                    if not hall.buffer(.1).covers(Point(xx,face_y+sign*-.1)):continue
                    top=float(rz(xx,face_y))-.10;profile=Polygon([(xx,0),(xx+1.8,0),(xx+1.8,top),(xx,top)])
                    # Each closed glazing panel slopes outward 0.65 m at its head.
                    q=box(xx,face_y-.045,xx+1.8,face_y+.045);m=t.extrusion(q,0,top);m.vertices[:,1]+=sign*.65*m.vertices[:,2]/top;ms['Glass'].append(m)
                    for edge_x in [xx,xx+1.8]:ms['WhitePanel'].append(t.cylinder((edge_x,face_y,0),(edge_x,face_y+sign*.65,top),.065,6))
                    for zz in np.arange(2,top,2):line((xx,face_y+sign*.65*zz/top),(xx+1.8,face_y+sign*.65*zz/top),zz,.07,.09,'WhitePanel')
            for xx in np.arange(aa+1,cc,2.3):
                points=[(xx,yy,float(rz(xx,yy))+.21)for yy in np.linspace(bb+.2,dd-.2,18)]
                for pa,pb in zip(points[:-1],points[1:]):
                    if hall.covers(Point(*pa[:2]))and hall.covers(Point(*pb[:2])):ms['Frame'].append(t.cylinder(pa,pb,.025,5))
        # Five paired mast frames, 24 stays apiece. Every stay terminates on
        # one of the actual hall roof surfaces instead of an arbitrary Z plane.
        masts=[(444,1271,0),(444,1291,0),(468,1372,1),(468,1404,1),(384,1385,1)]
        for mx,my,idx in masts:
            hall=halls[idx];rz=roof_functions[idx];tip=(mx-3.8,my,30.48)
            for dy in [-1.8,1.8]:ms['WhitePanel'].append(t.cylinder((mx,my+dy,0),tip,.27,10))
            aa,bb,cc,dd=hall.bounds
            for k in range(24):
                fraction=(k%6+.5)/6;side=k//6
                xy=(aa+(cc-aa)*fraction,bb+.4)if side==0 else(aa+(cc-aa)*fraction,dd-.4)if side==1 else(aa+.4,bb+(dd-bb)*fraction)if side==2 else(cc-.4,bb+(dd-bb)*fraction)
                q=hall.exterior.interpolate(hall.exterior.project(Point(*xy)));end=(q.x,q.y,float(rz(q.x,q.y))+.20);ms['Frame'].append(t.cylinder(tip,end,.035,5))
        for aa,bb,u,n in [((439,1329),(454,1338),np.array([1,0]),(1,0))]:pane(aa,bb,.15,3.7,n)
        stats={'curve_roofs':2,'mast_frames':5,'roof_attached_stays':120}
    elif ident==142870150:
        west=p.intersection(box(a-1,b-1,322,d+1));east=p.intersection(box(393,b-1,c+1,d+1));north=p.difference(unary_union([west,east]));atrium=east.intersection(box(393,967,c+1,1000));labs=east.difference(atrium)
        body(west,0,25.6,'Limestone',lev=5,arch=False);body(labs,0,25.6,'Limestone',lev=5,arch=False)
        body(north,5.4,20.2,'Limestone',lev=4,arch=False);body(atrium,0,26.4,'DarkGlass',windows=False)
        for q in [west,labs,north]:add(q,25.6,.16,'Metal');coping(q,25.76)
        add(atrium,26.4,.18,'Metal')
        for q in t.polygons(atrium):
            for aa,bb in zip(np.asarray(q.exterior.coords)[:-1],np.asarray(q.exterior.coords)[1:]):
                u=bb-aa;ln=np.linalg.norm(u)
                if ln<5:continue
                u/=ln;n=np.array([u[1],-u[0]]);pane(aa,bb,.2,25.7,n,width=2.3)
                for zz in np.arange(4.5,26,4.2):line(aa+n*.23,bb+n*.23,zz,.13,.15,'LightStone')
        # High round steel columns stand in front of the open breezeway and
        # support the upper canopy, separate from the ordinary window mullions.
        for xx in np.linspace(330,390,9):ms['Metal'].append(t.cylinder((xx,997.7,0),(xx,997.7,25.8),.29,12))
        add(box(325,996.2,396,1000.3),25.8,.48,'LightStone');add(north,.0,.16,'Paving')
        stats={'open_breezeway_clearance_m':5.4,'high_steel_colonnade':True,'glazed_hinge_atrium':True}
    elif ident==152284260:
        lower=p.buffer(-3.3528,join_style=2);body(lower,0,10.3,'Limestone',lev=2,arch=False);body(p,10.3,4.7,'Limestone',lev=1,arch=False);add(p,15,.16,'Metal');coping(p,15.16)
        # Central three-storey atrium lantern and the remodel's narrow roof lights.
        lantern=box(x-3.5,929,x+3.5,964).intersection(p);body(lantern,15.16,1.2,'Glass',windows=False);add(lantern,16.36,.10,'Glass');coping(lantern,16.46,'Metal')
        for xx in np.arange(a+7,c-4,5.4):
            q=box(xx-.8,970,xx+.8,981).intersection(p.buffer(-1));add(q,15.18,.13,'Glass')
        for yy in np.arange(b+4,d-3,4.8):
            for xx,sign in [(a-.03,-1),(c+.03,1)]:
                pane((xx,yy-.7),(xx,yy+.7),10.85,3.4,(sign,0),frame='Concrete',width=.7)
        stats={'cantilever_m':3.3528,'atrium_roof_lantern':True}
    elif ident==1228219576:
        # p already calibrated to the published historic square dimensions.
        cx,cy=p.centroid.coords[0];w=c-a;depth=d-b
        passage=unary_union([box(cx-1.65,b-1,cx+1.65,d+1),box(a-1,cy-1.65,c+1,cy+1.65)])
        body(p.difference(passage),0,5.3,'Limestone',windows=False);body(p,5.3,18.7,'Limestone',lev=3,arch=True)
        # Arched heads above the open cross passage connect the four piers.
        for n,u,center,width in [(np.array([0,1]),np.array([1,0]),[cx,d-.45],3.3),(np.array([0,-1]),np.array([-1,0]),[cx,b+.45],3.3),(np.array([1,0]),np.array([0,-1]),[c-.45,cy],3.3),(np.array([-1,0]),np.array([0,1]),[a+.45,cy],3.3)]:
            void=unary_union([box(-width/2,-1,width/2,3.4),Point(0,3.4).buffer(width/2,quad_segs=18)]);panel(box(-width/2,0,width/2,5.3).difference(void),center,u,n,0,.45,'Limestone')
        for n,u,center,width in [(np.array([0,1]),np.array([1,0]),[cx,d-.6],w),(np.array([0,-1]),np.array([-1,0]),[cx,b+.6],w),(np.array([1,0]),np.array([0,-1]),[c-.6,cy],depth),(np.array([-1,0]),np.array([0,1]),[a+.6,cy],depth)]:
            holes=[]
            for xx in [-width*.20,width*.20]:
                ww=width*.19;top=h-27.0;holes.append(unary_union([box(xx-ww/2,1,xx+ww/2,top-ww/2),Point(xx,top-ww/2).buffer(ww/2,quad_segs=16)]))
            panel(box(-width/2,0,width/2,h-26).difference(unary_union(holes)),center,u,n,24,.60,'Limestone')
        add(p,h-2,.15,'LightStone');t.crenellations(ms,p,h-1.85,1.85)
        for dx in [-1,1]:
            for dy in [-1,1]:
                turret=box(cx+dx*w*.41-.55,cy+dy*depth*.41-.55,cx+dx*w*.41+.55,cy+dy*depth*.41+.55);add(turret,h-9.0,9.0,'LightStone')
        stats={'open_cross_passage':True,'corner_turrets':4}
    return {'reference':REFS[ident],'features':FEATURES[ident],**stats}
