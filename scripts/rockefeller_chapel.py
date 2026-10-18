"""Rockefeller exterior reconstructed against owner and archive photographs.

The mapped plan and published 207-foot tower peak are retained. Local section
levels and tracery/member dimensions are photographic estimates, not a survey.
"""
import math
import numpy as np
import trimesh
from shapely.geometry import Polygon, Point, LineString, box
from shapely.ops import unary_union, transform

REFERENCE='https://www.rockefeller.uchicago.edu/the-spaces/rockefeller-architecture/'
FEATURES=[
 'Single high nave with a continuous north-south slate ridge',
 'Eastern carillon tower and west transverse projection in the mapped positions',
 'Monumental traceried lancet groups instead of repeated classroom-storey windows',
 'Hollow upper bell stage with paired long apertures, upper lights and recessed louvers',
 'Stepped masonry buttresses and supported corner lanterns',
 'South entrance with paired doors, deep arch, great window and gabled sculptural niches',
 'Low southeast covered passage and connected entrance steps',
]

def arch(width,height,head=None):
    """Depressed pointed arch, sampled as smooth cubic shoulders."""
    half=width/2;head=min(height*.32,width*.53)if head is None else head
    spring=height-head
    pts=[(-half,0),(half,0),(half,spring)]
    start=np.array([half,spring]);c1=np.array([half, spring+head*.40]);c2=np.array([width*.26,height-head*.10]);tip=np.array([0,height])
    curve=[]
    for a in np.linspace(0,1,15):
        curve.append((1-a)**3*start+3*(1-a)**2*a*c1+3*(1-a)*a*a*c2+a**3*tip)
    pts.extend(curve[1:]);pts.extend([(-x,y)for x,y in curve[-2::-1]])
    return Polygon(pts)

def rebuild(ms,p,h,body,t):
    # The two long mapped nave walls provide the local axes, rather than
    # imposing north-up rectangles on the slightly rotated georeferenced plan.
    origin=np.array([832.30,680.20]);north=np.array([-.012855,.999917]);north/=np.linalg.norm(north);east=np.array([north[1],-north[0]])
    def local(g):
        return transform(lambda x,y,z=None:((np.asarray(x)-origin[0])*east[0]+(np.asarray(y)-origin[1])*east[1],(np.asarray(x)-origin[0])*north[0]+(np.asarray(y)-origin[1])*north[1]),g)
    def world(g):
        return transform(lambda x,y,z=None:(origin[0]+np.asarray(x)*east[0]+np.asarray(y)*north[0],origin[1]+np.asarray(x)*east[1]+np.asarray(y)*north[1]),g)
    def xy(c):return origin+east*c[0]+north*c[1]
    def direction(u):return east*u[0]+north*u[1]
    plan=local(p)
    tower_source=next(f['poly']for f in t.features if f['id']==1449933351)
    tower=local(tower_source);ta,tb,tc,td=tower.bounds;tx=(ta+tc)/2;ty=(tb+td)/2
    # Small irregularities in the mapped tower corners remain in the lower
    # shaft. The upper belfry has straight, aligned wall planes.
    upper=box(ta+.10,tb+.10,tc-.10,td-.10);ua,ub,uc,ud=upper.bounds
    nave=plan.intersection(box(-10.35,-.3,10.15,80)).difference(tower)
    transept=plan.intersection(box(-20,41.7,-10.2,57.0))
    annex=plan.difference(unary_union([nave,tower,transept]))
    eave=26.35;rise=6.55
    stats={'great_window_groups':0,'bell_wall_apertures':0,'stepped_buttresses':0,'principal_entrances':0,'nave_eave_m':eave,'nave_ridge_m':eave+rise+.18,'tower_peak_m':h}
    def add(g,z,height,mat='ChapelStone'):
        if g.is_empty or height<=0:return
        for q in t.polygons(world(g)):ms[mat].append(t.extrusion(q,z,height))
    def solid(g,z,height,mat='ChapelStone'):
        if not g.is_empty:body(world(g),z,height,mat,windows=False)
    def panel(g,c,u,n,z,depth=.12,mat='ChapelTrim',offset=0):
        cc=xy(c);uu=direction(u);nn=direction(n)
        for q in t.polygons(g):
            m=t.extrusion(q,0,depth);v=m.vertices.copy();m.vertices=np.column_stack([cc[0]+uu[0]*v[:,0]+nn[0]*(v[:,2]+offset),cc[1]+uu[1]*v[:,0]+nn[1]*(v[:,2]+offset),z+v[:,1]])
            trimesh.repair.fix_normals(m,multibody=True);ms[mat].append(m)
    def bead(points,c,u,n,z,r=.055,mat='ChapelTrim',offset=.30):
        cc=xy(c);uu=direction(u);nn=direction(n)
        vertices=[(*list(cc+uu*x+nn*offset),z+y)for x,y in points]
        for a,b in zip(vertices[:-1],vertices[1:]):
            if np.linalg.norm(np.asarray(b)-a)>.005:ms[mat].append(t.cylinder(a,b,r,6))
    def louver(c,u,n,offset,z,width,head=False):
        # Sloped weather/acoustic baffles hide the bright opposite opening
        # while keeping an open air path; their ends sit in the bell reveals.
        cc=xy(c);uu=direction(u);nn=direction(n)
        m=t.extrusion(box(offset-width/2,0,offset+width/2,.11),0,.85)
        v=m.vertices.copy();m.vertices=np.column_stack([cc[0]+uu[0]*v[:,0]+nn[0]*(v[:,2]-.96),cc[1]+uu[1]*v[:,0]+nn[1]*(v[:,2]-.96),z+v[:,1]+(.85-v[:,2])*.65]);trimesh.repair.fix_normals(m);ms['ChapelLouvre'].append(m)
        if not head:panel(box(offset-width/2,z+.08,offset+width/2,z+.13),c,u,n,0,.12,'ChapelRoofSeam',-.13)
    def pointed_window(c,u,n,z,w,hh,lights=3,head=None,frame=.24,leaded=False):
        opening=arch(w,hh,head);inner=opening.buffer(-.055,join_style=2)
        # Dark aperture, a deep outer surround and a subordinate inner reveal.
        panel(opening,c,u,n,z,.055,'DarkGlass',.025)
        for width,offset,depth,material in [(frame,.08,.23,'ChapelTrim'),(.075,.32,.10,'ChapelStone')]:
            ring=opening.buffer(width,join_style=2).difference(opening.buffer(-.025,join_style=2));panel(ring,c,u,n,z,depth,material,offset)
        spring=hh-(min(hh*.32,w*.53)if head is None else head)
        step=w/lights
        for k in range(1,lights):
            x=-w/2+step*k;rib=box(x-.065,0,x+.065,spring+.18).intersection(opening);panel(rib,c,u,n,z,.12,'ChapelTrim',.32)
        # Individual subsidiary pointed lights meet the actual springing line.
        subtop=spring+.45
        for k in range(lights):
            mid=-w/2+step*(k+.5);small=arch(step-.13,subtop,head=min(step*.60,subtop*.25))
            small=transform(lambda x,y,z=None:(np.asarray(x)+mid,y),small)
            ring=small.buffer(.045,join_style=2).difference(small.buffer(-.025,join_style=2)).intersection(inner)
            panel(ring,c,u,n,z,.09,'ChapelTrim',.34)
        # The circular/foiled upper tracery is subordinate to the large arch.
        rosette_radius=min(w*.145,(hh-spring)*.35)
        center=(0,spring+(hh-spring)*.49)
        foil=unary_union([Point(center[0]+dx*rosette_radius*.60,center[1]+dy*rosette_radius*.60).buffer(rosette_radius*.64,quad_segs=12)for dx,dy in [(0,1),(1,0),(0,-1),(-1,0)]])
        ring=foil.buffer(.08).difference(foil.buffer(-.025)).intersection(inner);panel(ring,c,u,n,z,.11,'ChapelTrim',.35)
        for sign in [-1,1]:
            leaf=Point(sign*w*.29,spring+(hh-spring)*.28).buffer(rosette_radius*.48,quad_segs=12)
            panel(leaf.buffer(.07).difference(leaf.buffer(-.02)).intersection(inner),c,u,n,z,.10,'ChapelTrim',.35)
        # Lead joints have a much lighter hierarchy than the masonry mullions.
        if leaded:
            grid=[]
            for zz in np.arange(.5,spring,.7):grid.append(box(-w/2,zz-.012,w/2,zz+.012))
            for xx in np.arange(-w/2+.32,w/2,.38):grid.append(box(xx-.009,0,xx+.009,spring))
            panel(unary_union(grid).intersection(inner),c,u,n,z,.018,'ChapelLead',.10)
        stats['great_window_groups']+=1
    def portal(c,u,n,base,w=4.1,hh=6.3):
        outer=arch(w,hh,head=1.85)
        panel(outer,c,u,n,base,.065,'ChapelRecess',.025)
        for d in [0,.18,.36]:
            ring=outer.buffer(.22+d*.35,join_style=2).difference(outer.buffer(.035+d*.35,join_style=2));panel(ring,c,u,n,base,.14,'ChapelTrim',.08+d)
        for sign in [-1,1]:
            leaf=box(sign*w*.235-w*.205,0,sign*w*.235+w*.205,3.35);panel(leaf,c,u,n,base,.08,'ChapelDoor',.20)
            for zz in [.55,1.45,2.35]:panel(box(leaf.bounds[0]+.12,zz,leaf.bounds[2]-.12,zz+.045),c,u,n,base,.035,'ChapelDoorTrim',.29)
            head=arch(w*.43,1.8,head=.7);head=transform(lambda x,y,z=None:(np.asarray(x)+sign*w*.235,np.asarray(y)+3.35),head)
            panel(head,c,u,n,base,.065,'DarkGlass',.18);panel(head.buffer(.095).difference(head.buffer(-.025)),c,u,n,base,.12,'ChapelTrim',.29)
        panel(box(-.075,0,.075,5.2),c,u,n,base,.18,'ChapelTrim',.32)
        panel(box(-w/2-.6,-.10,w/2+.6,.08),c,u,n,base,.78,'ChapelTrim',.05)
        stats['principal_entrances']+=1
    def roof(g,walltop,roofrise,axis='y',width=20.0,center=0):
        a,b,c,d=g.bounds
        cuts=[box(a-1,b-1,center,d+1),box(center,b-1,c+1,d+1)]if axis=='y'else[box(a-1,b-1,c+1,center),box(a-1,center,c+1,d+1)]
        for cut in cuts:
            for q in t.polygons(g.intersection(cut)):
                m=t.extrusion(q,walltop-.015,.04);v=m.vertices.copy();coord=v[:,0 if axis=='y'else 1];delta=roofrise*np.maximum(0,1-abs(coord-center)/(width/2));v[v[:,2]>walltop,2]+=delta[v[:,2]>walltop];m.vertices=v;trimesh.repair.fix_normals(m);ms['ChapelStone'].append(to_world_mesh(m))
                skin=t.extrusion(q,walltop+.027,.16);coord=skin.vertices[:,0 if axis=='y'else 1];skin.vertices[:,2]+=roofrise*np.maximum(0,1-abs(coord-center)/(width/2));trimesh.repair.fix_normals(skin);ms['ChapelRoof'].append(to_world_mesh(skin))
        # Longitudinal roof seams and ridge follow the actual sloping surface.
        def z(x,y):return walltop+.20+roofrise*max(0,1-abs((x if axis=='y'else y)-center)/(width/2))
        for xx in np.arange(a+1,c,.95)if axis=='y'else[]:
            section=g.intersection(LineString([(xx,b),(xx,d)]))
            for line in ([section]if section.geom_type=='LineString'else getattr(section,'geoms',[])):
                if line.geom_type!='LineString' or line.length<2:continue
                ends=list(line.coords);aa,bb=ends[0],ends[-1];ms['ChapelRoofSeam'].append(t.cylinder((*xy(aa),z(*aa)),(*xy(bb),z(*bb)),.024,5))
    def to_world_mesh(m):
        v=m.vertices.copy();m.vertices=np.column_stack([origin[0]+v[:,0]*east[0]+v[:,1]*north[0],origin[1]+v[:,0]*east[1]+v[:,1]*north[1],v[:,2]]);return m
    def buttress(x,y,sign,top=eave):
        profile=Polygon([(-.18,0),(2.6,0),(2.6,1.2),(2.2,1.5),(2.2,7.1),(1.55,8.0),(1.55,15.3),(.82,16.2),(.82,top-.9),(.48,top-.4),(.48,top+.15),(-.18,top+.15)])
        panel(profile,(x,y-.70),(sign,0),(0,1),0,1.4,'ChapelTrim')
        for zz,deep in [(1.1,2.62),(7.1,2.22),(15.3,1.57)]:
            panel(box(-.2,zz,deep,zz+.14),(x,y-.78),(sign,0),(0,1),0,1.56,'ChapelTrim')
        stats['stepped_buttresses']+=1
    def lantern(x,y,base,peak,size=1.6):
        foot=Point(x,y).buffer(size/2,quad_segs=2)
        add(foot,base,peak-base-1.6,'ChapelTrim')
        add(foot.buffer(.12,join_style=2),peak-1.68,.16,'ChapelTrim')
        # Short tapered cap is a supported roof, not a detached facade rod.
        cap=t.extrusion(foot,peak-1.52,.04);v=cap.vertices.copy();top=v[:,2]>peak-1.5;v[top,:2]=np.array([x,y])+(v[top,:2]-np.array([x,y]))*.035;v[top,2]=peak;cap.vertices=v;trimesh.repair.fix_normals(cap);ms['ChapelTrim'].append(to_world_mesh(cap))
        for n,u in [((1,0),(0,1)),((-1,0),(0,-1)),((0,1),(-1,0)),((0,-1),(1,0))]:
            center=(x+n[0]*size*.42,y+n[1]*size*.42)
            for off in [-.22,.22]:
                hole=arch(.27,1.20,head=.20);hole=transform(lambda x,y,z=None:(np.asarray(x)+off,y),hole)
                panel(hole,center,u,n,peak-3.3,.045,'ChapelRecess',.02)
    # Main hall: the transept roof extends into the nave up to the shared
    # diagonal valleys. Separate roof skins must not stop at the nave wall.
    valley_x=10*(5.1/rise-1)
    crossing=Polygon([(-22,42.0),(-10,42.0),(valley_x,49.2),(-10,56.4),(-22,56.4)])
    west_roof=unary_union([nave,transept]).intersection(crossing)
    solid(nave,0,eave);roof(nave.difference(crossing),eave,rise)
    solid(transept,0,eave);roof(west_roof,eave,5.1,'x',14.4,49.2)
    solid(tower,0,38.4)
    def wall_x(y,sign,shape0=nave):
        section=shape0.intersection(LineString([(-30,y),(30,y)]))
        return section.bounds[0 if sign<0 else 2]+sign*.018
    def wall_y(x,sign):
        section=nave.intersection(LineString([(x,-2),(x,82)]))
        return section.bounds[1 if sign<0 else 3]+sign*.018
    # Plinths make the masonry meet its grade and entrance platforms.
    add(plan.boundary.buffer(.17,join_style=2).intersection(plan.buffer(.05)),.12,.65,'ChapelTrim')
    # Actual side nave bays: three monumental windows south of the transept,
    # then the narrower chancel bays north of it.
    for sign in [-1,1]:
        for yy in [10.2,23.2,36.2]:pointed_window((wall_x(yy,sign),yy),(0,1),(sign,0),6.65,6.75,17.15,3,head=3.45)
        for yy in [3.7,16.7,29.7]:buttress(wall_x(yy,sign),yy,sign)
    # Chancel wall is narrower on the east as recorded by the plan.
    for yy in [63.2,73.1]:
        pointed_window((wall_x(yy,-1),yy),(0,1),(-1,0),7.1,5.0,16.3,3,head=2.9)
        pointed_window((wall_x(yy,1),yy),(0,-1),(1,0),7.1,4.9,16.3,3,head=2.9)
    for yy in [58.0,68.2,78.2]:buttress(wall_x(yy,-1),yy,-1)
    # South great window, paired door portal, and the projecting weathered hood.
    pointed_window((-.1,-.05),(1,0),(0,-1),9.0,8.6,14.8,4,head=3.8,frame=.35,leaded=True)
    portal((-.1,-.12),(1,0),(0,-1),.70,5.9,6.7)
    hood=arch(9.65,16.1,4.0);panel(hood.buffer(.18).difference(hood.buffer(-.08)),(-.1,-.12),(1,0),(0,-1),8.45,.46,'ChapelStone',.45)
    panel(box(-5.35,7.0,5.35,7.45),(-.1,-.12),(1,0),(0,-1),0,.80,'ChapelTrim',.18)
    # Recessed gable niches and tracery courses abstract the sculpture in its
    # source-supported locations; individual figures are not asserted replicas.
    for xx in np.arange(-8,8.1,2):
        zz=eave+rise*(1-abs(xx)/10)-2.15;profile=arch(.75,1.45,.30)
        panel(profile,(xx,-.15),(1,0),(0,-1),zz,.06,'ChapelRecess',.15)
        panel(profile.buffer(.13).difference(profile.buffer(-.02)),(xx,-.15),(1,0),(0,-1),zz,.19,'ChapelTrim',.22)
        bead([(-.20,0),(-.16,.30),(0,.62),(.16,.30),(.20,0)],(xx,-.15),(1,0),(0,-1),zz+.23,.13,'ChapelStone',.37)
    # Sloped parapet copings return into the supported corner lanterns.
    for aa,bb in [((-10.0,eave+.30),(0,eave+rise+.50)),((0,eave+rise+.50),(10.0,eave+.30))]:
        bead([aa,bb],(0,-.22),(1,0),(0,-1),0,.15,'ChapelTrim',.12)
    for xx in [-9.25,9.05]:
        buttress(xx,0.0,-1 if xx<0 else 1,28.7);lantern(xx,.32,27.9,35.30,1.60)
    for xx in [-9.4,4.5]:lantern(xx,78.2,25.9,33.8,1.30)
    # North chancel gable and west transept retain their individual tall lights.
    pointed_window((-2.3,wall_y(-2.3,1)),(-1,0),(0,1),8.2,7.4,15.0,3,head=3.2)
    pointed_window((wall_x(49.2,-1,transept),49.2),(0,-1),(-1,0),7.8,8.3,16.0,4,head=3.3)
    portal((wall_x(49.2,-1,transept),49.2),(0,-1),(-1,0),.40,3.5,5.7)
    # The covered low passage southeast of the front is open through its arch.
    for q in t.polygons(annex):
        a,b,c,d=q.bounds
        if b<12 and c>10:
            width=c-a;cx=(a+c)/2;opening=arch(max(1.4,width-2.0),4.5,1.3)
            piers=q.difference(box(a+1,b-1,c-1,d+1));solid(piers,0,6.15)
            for yy,normal,u in [(b,(0,-1),(1,0)),(d,(0,1),(-1,0))]:panel(box(-width/2,0,width/2,6.2).difference(opening),(cx,yy),u,normal,0,.45,'ChapelStone',-.40)
            add(q,6.15,.20,'ChapelTrim');add(q.buffer(-.25),6.35,.12,'ChapelRoof')
        else:solid(q,0,8.6);roof(q,8.6,1.6,width=max(1,c-a),center=(a+c)/2)
    # Belfry is a hollow wall assembly. Long lower pairs and a short upper
    # register replace the incorrect repeated rows of generic office windows.
    faces=[((tx,ub+.8),(1,0),(0,-1),uc-ua),((uc-.8,ty),(0,1),(1,0),ud-ub),((tx,ud-.8),(-1,0),(0,1),uc-ua),((ua+.8,ty),(0,-1),(-1,0),ud-ub)]
    for center,u,n,width in faces:
        apertures=[]
        for off in [-2.55,2.55]:
            opening=arch(2.25,13.9,2.4);opening=transform(lambda x,y,z=None:(np.asarray(x)+off,np.asarray(y)+.6),opening);apertures.append(opening)
            upperlight=arch(2.55,4.2,.65);upperlight=transform(lambda x,y,z=None:(np.asarray(x)+off,np.asarray(y)+16.25),upperlight);apertures.append(upperlight)
            # Reveals follow the true void; louver blades sit behind its face.
            for shape0 in [opening,upperlight]:panel(shape0.buffer(.14).difference(shape0),center,u,n,38.4,.15,'ChapelTrim',.80)
            for zz in np.arange(1.3,12.5,.78):
                louver(center,u,n,off,38.4+zz,2.08)
            for zz in [16.45,17.15,17.85,18.55,19.25]:louver(center,u,n,off,38.4+zz,2.20,True)
            for zz in [16.8,17.6,18.4,19.2]:panel(box(off-1.15,zz,off+1.15,zz+.09).intersection(upperlight),center,u,n,38.4,.20,'ChapelTrim',.10)
            panel(box(off-.055,16.3,off+.055,20.3).intersection(upperlight),center,u,n,38.4,.20,'ChapelTrim',.10)
            stats['bell_wall_apertures']+=2
        panel(box(-width/2,0,width/2,22.0).difference(unary_union(apertures)),center,u,n,38.4,.8,'ChapelStone')
        # Upper parapet uses the characteristic chevron band rather than
        # alternating castle merlons around a flat office-block roof.
        for j in range(5):
            xx=-width*.34+j*width*.17;bead([(xx-.8,60.5),(xx,61.35),(xx+.8,60.5)],center,u,n,0,.08,'ChapelTrim',.86)
    add(upper,60.4,.16,'ChapelTrim')
    parapet=upper.difference(upper.buffer(-.75,join_style=2))
    add(parapet,60.4,1.35,'ChapelStone');add(parapet.buffer(.08,join_style=2),61.75,.12,'ChapelTrim')
    # Recessed, shallow hipped roof at the tower's crown.
    roofpad=upper.buffer(-1.3,join_style=2)
    for q in t.polygons(roofpad):
        aa,bb,cc,dd=q.bounds;xm=(aa+cc)/2;ym=(bb+dd)/2
        # Four triangular hips meet a very short central ridge.
        verts=np.array([[aa,bb,60.56],[cc,bb,60.56],[cc,dd,60.56],[aa,dd,60.56],[xm,ym,61.55],[aa,bb,60.48],[cc,bb,60.48],[cc,dd,60.48],[aa,dd,60.48]])
        ff=[[0,1,4],[1,2,4],[2,3,4],[3,0,4],[5,7,6],[5,8,7],[0,5,6],[0,6,1],[1,6,7],[1,7,2],[2,7,8],[2,8,3],[3,8,5],[3,5,0]]
        m=trimesh.Trimesh(verts,ff);trimesh.repair.fix_normals(m);ms['ChapelRoof'].append(to_world_mesh(m))
    # Full-height attached corner piers articulate the shaft and support the
    # four rounded/octagonal crown turrets at exactly the published maximum.
    for xx in [ta+.65,tc-.65]:
        for yy in [tb+.65,td-.65]:
            for z,top,width in [(0,20.1,2.5),(20.1,43.3,2.05),(43.3,54.5,1.65),(54.5,60.55,1.45)]:add(box(xx-width/2,yy-width/2,xx+width/2,yy+width/2),z,top-z,'ChapelTrim')
            crown=Point(xx,yy).buffer(1.05,quad_segs=2);add(crown,60.5,h-60.5-.20,'ChapelTrim');add(crown.buffer(.12,join_style=2),h-.20,.20,'ChapelStone')
            for n,u in [((1,0),(0,1)),((-1,0),(0,-1)),((0,1),(-1,0)),((0,-1),(1,0))]:
                panel(arch(.42,.88,.20),(xx+n[0]*.96,yy+n[1]*.96),u,n,61.0,.04,'ChapelRecess',.01)
    # Tower's eastern entrance and monumental lower window.
    pointed_window((tc+.04,ty),(0,1),(1,0),8.0,5.8,16.0,3,head=3.1)
    portal((tc+.04,ty),(0,1),(1,0),.45,4.1,6.0)
    # Narrow stair slits are confined to source-plausible solid shaft zones.
    for yy in [tb+.10,td-.10]:
        for xx in [tx-3.9,tx+3.9]:panel(arch(.48,2.2,.3),(xx,yy),(1,0),(0,-1 if yy<ty else 1),32.2,.06,'ChapelRecess',.06)
    # The south stairs terminate at the portal's threshold and its full landing.
    add(box(-6.2,-1.75,6.0,-.15),0,.70,'ChapelTrim')
    for k in range(8):add(box(-5.6,-5.35+k*.45,5.4,-4.90+k*.45),0,(k+1)*.0875,'ChapelTrim')
    for xx in [-5.8,5.6]:
        add(box(xx-.18,-5.35,xx+.18,-1.75),0,.32,'ChapelStone')
        a=(*xy((xx,-5.15)),.97);b=(*xy((xx,-1.82)),1.57);ms['Frame'].append(t.cylinder(a,b,.038,8))
        for f in [0,.5,1]:
            y=-5.15+3.33*f;z=.97+.60*f;ms['Frame'].append(t.cylinder((*xy((xx,y)),(min(7,max(0,int((y+5.35)/.45)))+1)*.0875-.02),(*xy((xx,y)),z),.03,8))
    stats['reference']=REFERENCE;stats['features']=FEATURES;stats['local_frame']={'origin':origin.tolist(),'east':east.tolist(),'north':north.tolist()};stats['tower_local_bounds']=list(tower.bounds)
    stats['dimension_status']='Published tower maximum; mapped footprint; photo-estimated section levels, bays, tracery and ornaments. Relief figures remain abstracted.'
    return stats
