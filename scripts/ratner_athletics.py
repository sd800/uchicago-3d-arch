"""Ratner: source-compared optimized exterior, not a measured structural model.

As-built university photographs establish the separated halls, west service
wing, east glazing and circular arrival drum. AISC's March/April 2004 case
studies establish three-member primary masts and 9 fore/6 backstay groups.
Mapped plan and the existing documented 100-foot peak are retained. All local
section coordinates and connection sizes remain exterior interpretations.
"""
import math
import numpy as np
import trimesh
from shapely.geometry import box, Point, Polygon, LineString
from shapely.ops import unary_union
from shapely import segmentize

REFERENCE='https://architecture.uchicago.edu/locations/gerald_ratner_athletics_center/'
FEATURES=[
 'separate south gymnasium, narrower northeast pool hall and low west service/fitness wing',
 'continuous flattened S-profile standing-seam roofs with closed clerestory returns',
 'east-facing sloping curtain walls and warm masonry end walls',
 'five three-member tapered primary masts, fifteen secondary masts and layered fore/back stays',
 'curved brick entrance drum with rising parapet, recessed skylight, glazed doors and connected curved steps'
]

def rebuild(ms,p,h,body,t):
    def add(q,z,hh,mat):
        for part in t.polygons(q):
            if hh>.004:ms[mat].append(t.extrusion(part,z,hh))
    def bar(a,b,r=.06,mat='RatnerSteel',sides=8):
        if np.linalg.norm(np.asarray(b)-a)>.008:ms[mat].append(t.cylinder(a,b,r,sides))
    def deform(q,low,high,mat,resolution=.65):
        # Closed variable-height prism; subdividing the plan also subdivides
        # the curved top, so envelope, clerestory and roof share one profile.
        for part in t.polygons(q):
            # Subdivide after polygon cleanup; its collinear simplifier must
            # not erase the stations needed to follow a curved roof section.
            part=segmentize(part,resolution)
            m=t.extrusion(part,0,1);v=m.vertices.copy();up=v[:,2]>.5
            v[:,2]=np.where(up,high(v[:,0],v[:,1]),low(v[:,0],v[:,1]))
            m.vertices=v;trimesh.repair.fix_normals(m,multibody=True)
            assert m.is_watertight and m.is_winding_consistent
            ms[mat].append(m)
    def constant(z):return lambda x,y:np.zeros_like(np.asarray(x))+z
    def outline_roof(q,z):
        add(q,z,.18,'RatnerRoof')
        add(q.buffer(.10,join_style=2).difference(q.buffer(-.14,join_style=2)),z+.18,.15,'RatnerFascia')
    def glass_edge(a,b,z0,z1,normal,spacing=1.8):
        a,b,n=np.array(a),np.array(b),np.array(normal);u=b-a;length=np.linalg.norm(u)
        if length<.35:return
        u/=length;a=a+n*.045;b=b+n*.045
        strip=Polygon([a,b,b+n*.065,a+n*.065]);add(strip,z0,z1-z0,'RatnerGlass')
        for zz in [z0,z1]:bar((*a,zz),(*b,zz),.055,'RatnerSteel')
        for distance in np.linspace(0,length,max(2,int(length/spacing)+1)):
            c=a+u*distance;bar((*c,z0),(*c,z1),.045,'RatnerSteel',6)
        for zz in np.arange(z0+1.6,z1-.2,1.6):bar((*a,zz),(*b,zz),.032,'RatnerSteel',6)

    # The mapped northern footprint also contains low western changing/
    # service rooms. Its entire width must not receive the pool's high roof.
    gym=p.intersection(box(379,1259,445,1302.55))
    pool=p.intersection(box(429.2,1352.90,467,1421.0))
    halls=[gym,pool]
    rotunda=p.intersection(Point(439.1,1343.0).buffer(14.55,quad_segs=40))
    commons=p.difference(unary_union(halls+[rotunda]))
    body(commons,0,7.15,'RatnerBrown',windows=False)
    outline_roof(commons,7.15)
    # Ordinary office openings are restrained and attached to actual exposed
    # edges. Tall corner glazing belongs to the west-facing fitness frontage.
    for part in t.polygons(commons):
        points=np.asarray(part.exterior.coords)
        for a,b in zip(points[:-1],points[1:]):
            direction=b-a;ln=np.linalg.norm(direction)
            if ln<2.5:continue
            u=direction/ln;n=np.array([u[1],-u[0]])
            if p.covers(Point(*((a+b)/2+n*.45))):continue
            if n[0]<-.7 and 1306<(a[1]+b[1])/2<1354:
                center=(a+b)/2;half=min(ln*.4,4.7)
                glass_edge(center-u*half,center+u*half,.45,6.95,n,1.25)
            else:
                for distance in np.arange(1.4,ln-1.0,3.7):
                    c=a+u*distance
                    for z in [1.15,4.45]:glass_edge(c-u*.43,c+u*.43,z,z+1.35,n,1)
            for z in [.25,3.7]:
                c=a+n*.035;d=b+n*.035;bar((*c,z),(*d,z),.055,'RatnerTan',6)

    roofs=[];wall_probes=[];roof_probes=[]
    for index,hall in enumerate(halls):
        aa,bb,cc,dd=hall.bounds;span=cc-aa
        def rz(x,y,aa=aa,span=span,index=index):
            s=np.clip((np.asarray(x)-aa)/span,0,1)
            return 10.65+2.25*np.sin(math.pi*(s-.16)/.98)+.85*s+(0 if index else .30)
        roofs.append(rz)
        body(hall,0,.24,'Concrete',windows=False)
        roof=hall.buffer(.65,join_style=2)
        # Tiles share exact heights; the complete surface has no horizontal
        # patch of brick projecting through its sheet or open eave gap.
        for x in np.arange(aa-1,cc+1,1.6):
            deform(roof.intersection(box(x,bb-2,x+1.6,dd+2)),lambda x,y:rz(x,y)-.28,rz,'RatnerRoof',resolution=6.0)
        for part in t.polygons(hall):
            coords=np.asarray(part.exterior.coords)
            for a,b in zip(coords[:-1],coords[1:]):
                u=b-a;ln=np.linalg.norm(u)
                if ln<.20:continue
                u/=ln;n=np.array([u[1],-u[0]])
                wall=Polygon([a,b,b-n*.32,a-n*.32])
                east=n[0]>.8
                end=abs(n[1])>.8
                if east:
                    add(wall,0,.55,'RatnerTan')
                    previous_glass=len(ms['RatnerGlass'])
                    deform(wall,constant(.55),lambda x,y:rz(x,y)-.38,'RatnerGlass')
                    # The tall east-facing wall slopes outward toward its
                    # head. A shared deformation keeps the glazing closed.
                    for glass in ms['RatnerGlass'][previous_glass:]:
                        v=glass.vertices.copy();v[:,:2]+=np.outer(v[:,2]/14.0,n*.52);glass.vertices=v
                    for dist in np.arange(.4,ln,2.45):
                        c=a+u*dist;top=float(rz(*c))-.36
                        bar((*c,.5),(*(c+n*.52*top/14),top),.065,'RatnerSteel')
                    for z in np.arange(2.1,min(float(rz(*a)),float(rz(*b)))-.55,1.6):
                        bar((*(a+n*.52*z/14),z),(*(b+n*.52*z/14),z),.035,'RatnerSteel',6)
                    # Discrete exterior truss bays, not a forest of freestanding
                    # vertical rods: each ends on the plinth and the eave.
                    for dist in np.arange(5,ln-4,7.62):
                        c=a+u*dist;z=float(rz(*c))-.4
                        left=c-u*3.4;right=c+u*3.4
                        if z<4:continue
                        mid=c+n*.40
                        bar((*(left+n*.06),.65),(*mid,z*.52),.045,'RatnerSteel',6)
                        bar((*(right+n*.06),.65),(*mid,z*.52),.045,'RatnerSteel',6)
                        bar((*mid,z*.52),(*(left+n*.52),z-.15),.045,'RatnerSteel',6)
                        bar((*mid,z*.52),(*(right+n*.52),z-.15),.045,'RatnerSteel',6)
                else:
                    # Brick ends rise with the roof; the upper glazing band
                    # is a true continuous clerestory, not glass on solid wall.
                    deform(wall,constant(.22),lambda x,y:rz(x,y)-1.38,'RatnerTan')
                    deform(wall,lambda x,y:rz(x,y)-1.38,lambda x,y:rz(x,y)-.38,'RatnerGlass' if end else 'RatnerFrost')
                    for distance in np.arange(.7,ln,2.25):
                        c=a+u*distance;top=float(rz(*c))-.36
                        bar((*(c+n*.04),top-1.05),(*(c+n*.04),top),.045,'RatnerSteel',6)
                    # Broad actual masonry is kept calm at campus distances.
                    for z in [1.0,3.3,5.6,7.9]:
                        if z<min(float(rz(*a)),float(rz(*b)))-1.5:
                            bar((*(a+n*.025),z),(*(b+n*.025),z),.026,'RatnerBrown',5)
                # Profile-following fascia and clerestory sill.
                samples=np.linspace(0,ln,max(2,int(ln/.8)+1))
                for d0,d1 in zip(samples[:-1],samples[1:]):
                    c=a+u*d0+n*.10;d=a+u*d1+n*.10
                    bar((*c,float(rz(*c))-.26),(*d,float(rz(*d))-.26),.105,'RatnerFascia')
                    if not east:bar((*c,float(rz(*c))-1.40),(*d,float(rz(*d))-1.40),.055,'RatnerFascia',6)
                if ln>8:
                    c=(a+b)/2
                    wall_probes.append({'xy':c.round(4).tolist(),'normal':n.round(6).tolist(),'z':round(float(rz(*c))-.72,4),'material':'RatnerGlass' if end or east else 'RatnerFrost'})
        # Standing seams are sparse enough for a campus model and follow
        # the curved span, rather than drawing crossed lines over the roof.
        for yy in np.arange(bb+.7,dd,1.8):
            xs=np.linspace(aa-.55,cc+.55,27)
            for x0,x1 in zip(xs[:-1],xs[1:]):
                if roof.covers(Point((x0+x1)/2,yy)):
                    bar((x0,yy,float(rz(x0,yy))+.025),(x1,yy,float(rz(x1,yy))+.025),.023,'RatnerRoofSeam',5)
        roof_probes.append({'xy':[(aa+cc)/2,(bb+dd)/2],'z':float(rz((aa+cc)/2,(bb+dd)/2))})

    # Five primary masts on the western/back lines, two for the gym and
    # three for the narrower pool hall. Three tubes, not two generic sticks.
    primary=[];secondary=[];cables=[]
    for index,centers in [(0,[1270.0,1292.86]),(1,[1363.6,1386.46,1409.32])]:
        hall=halls[index];rz=roofs[index];aa,bb,cc,dd=hall.bounds
        mx=aa+4.2
        for my in centers:
            top=np.array([mx-math.tan(math.radians(10))*h,my,h])
            feet=[np.array([mx-1.05,my-1.0,.15]),np.array([mx+1.05,my-1.0,.15]),np.array([mx,my+1.1,.15])]
            # Terminate three tubes in a narrow triangular crown. Horizontal
            # ties brace this taper at several levels without a solid cone.
            tips=[top+np.array([dx,dy,0])for dx,dy in [(-.10,-.08),(.10,-.08),(0,.10)]]
            for foot,tip in zip(feet,tips):
                add(Point(*foot[:2]).buffer(.46,quad_segs=8),0,.18,'Concrete');bar(foot,tip,.2286,'RatnerSteel',10)
            for z in [6.5,13.2,20.5,26.2]:
                f=z/h;points=[foot+(tip-foot)*f for foot,tip in zip(feet,tips)]
                for pa,pb in zip(points,points[1:]+points[:1]):bar(pa,pb,.13,'RatnerSteel')
            girder_ys=[my-7.62,my,my+7.62]
            anchor_x=aa+.65
            for yy in [my-7.62,my+7.62]:
                top_z=float(rz(anchor_x,yy))+.3
                bar((anchor_x,yy,.15),(anchor_x,yy,top_z),.105,'RatnerSteel')
            for level,fraction in [(h-.20,.84),(h-7.62,.56),(h-15.24,.29)]:
                start=np.array([mx-math.tan(math.radians(10))*level,my,level])
                for yy in girder_ys:
                    xx=aa+(cc-aa)*fraction;end=np.array([xx,yy,float(rz(xx,yy))+.15])
                    bar(start,end,.038,'RatnerCable',6);cables.append({'start':start.tolist(),'end':end.tolist(),'hall':index,'kind':'fore'})
                    add(Point(xx,yy).buffer(.17,quad_segs=5),float(rz(xx,yy)),.19,'RatnerSteel')
                for yy in [my-7.62,my+7.62]:
                    end=np.array([anchor_x,yy,float(rz(anchor_x,yy))+.30])
                    bar(start,end,.034,'RatnerCable',6);cables.append({'start':start.tolist(),'end':end.tolist(),'hall':index,'kind':'back'})
            primary.append({'hall':index,'feet':[foot.tolist()for foot in feet],'tips':[tip.tolist()for tip in tips]})
            # Secondary masts oppose the primary group at each actual girder
            # line; one span stay and two bow backstays give 45 secondary ties.
            for yy in girder_ys:
                xx=cc-1.0;z=float(rz(xx,yy));base=np.array([xx,yy,z]);tip=np.array([xx-.65,yy,z+3.5])
                bar(base,tip,.16,'RatnerSteel',10)
                targets=[(aa+(cc-aa)*.72,yy),(cc-.5,yy-3.0),(cc-.5,yy+3.0)]
                for ax,ay in targets:
                    ay=float(np.clip(ay,bb+.35,dd-.35))
                    end=np.array([ax,ay,float(rz(ax,ay))+.12])
                    bar(tip,end,.029,'RatnerCable',6);cables.append({'start':tip.tolist(),'end':end.tolist(),'hall':index,'kind':'secondary'})
                secondary.append({'base':base.tolist(),'tip':tip.tolist()})

    # Circular entrance: roof/skylight sits inside a rising brick parapet.
    # The exposed east side has glazed doors under a curved canopy, matching
    # the built photographs instead of a uniformly capped brick cylinder.
    center=np.array([439.1,1343.0]);radius=14.55
    def drum_top(x,y):return 10.0+1.85*np.clip((np.asarray(y)-1343.0)/radius,-1,1)
    body(rotunda,0,.35,'RatnerDrum',windows=False)
    ring=rotunda.difference(rotunda.buffer(-.42))
    deform(ring,constant(3.05),drum_top,'RatnerDrum')
    deform(ring,drum_top,lambda x,y:drum_top(x,y)+.15,'RatnerFascia')
    inner=rotunda.buffer(-.6)
    add(inner,7.65,.16,'RatnerRoof')
    skylight=Point(*center).buffer(4.7,quad_segs=28).intersection(inner)
    add(skylight,7.85,.22,'RatnerGlass')
    add(skylight.buffer(.11).difference(skylight.buffer(-.15)),8.07,.10,'RatnerSteel')
    for part in t.polygons(rotunda):
        coords=np.asarray(part.exterior.coords)
        for a,b in zip(coords[:-1],coords[1:]):
            u=b-a;ln=np.linalg.norm(u)
            if ln<.04:continue
            u/=ln;n=np.array([u[1],-u[0]]);c=(a+b)/2
            if p.covers(Point(*(c+n*.55))):continue
            q=Polygon([a,b,b-n*.32,a-n*.32])
            if n[0]>.65:
                add(q,.35,2.70,'RatnerGlass')
                if int((c[1]-1328)*2)%3==0:bar((*a,.35),(*a,3.05),.055,'RatnerSteel')
            else:
                add(q,.35,2.70,'RatnerDrum')
                # One small upper-lobby punched light per physical brick bay.
                if 1.0<ln<2.5:glass_edge(c-u*.25,c+u*.25,4.25,5.05,n,.6)
    east_half=box(center[0]+3,1327,center[0]+20,1358)
    canopy=rotunda.buffer(1.45).difference(rotunda.buffer(-.5)).intersection(east_half)
    add(canopy,3.13,.22,'RatnerRoof');add(canopy.boundary.buffer(.06),3.35,.08,'RatnerFascia')
    # All three treads meet the door landing and surrounding zero datum.
    landing=rotunda.buffer(1.45).difference(rotunda).intersection(east_half)
    add(landing,0,.35,'Paving')
    for extra,height in [(2.15,.2333),(2.85,.1167)]:
        tread=rotunda.buffer(extra).difference(rotunda.buffer(extra-.7)).intersection(east_half)
        add(tread,0,height,'Paving')
    for yy in [1338.0,1347.5]:
        xx=math.sqrt(radius**2-(yy-center[1])**2)+center[0]
        for x,z in [(xx+.4,.35),(xx+2.55,.1167)]:bar((x,yy,z),(x,yy,z+1.0),.032,'RatnerSteel',6)
        bar((xx+.4,yy,1.35),(xx+2.55,yy,1.1167),.034,'RatnerSteel',6)
    return {'reference':REFERENCE,'features':FEATURES,'modeling_level':'optimized exterior','bespoke_joinery':True,
      'curve_roofs':2,'mast_frames':5,'primary_members':15,'secondary_masts':15,
      'roof_attached_stays':len(cables),'primary_fore_stays':45,'primary_back_stays':30,'secondary_stays':45,
      'primary_masts':primary,'secondary_mast_records':secondary,'cable_connections':cables,
      'hall_bounds':[list(q.bounds)for q in halls],'roof_probes':roof_probes,'wall_probes':wall_probes,
      'entry_landing_m':.35,'local_dimensions':'Photo interpretation; no claim of measured structural connection geometry.'}
