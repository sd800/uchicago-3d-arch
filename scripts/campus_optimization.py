"""Explicit campus-wide optimized exteriors, between massing and detailed modeling.

Keep individual mapped outlines, do not substitute one decorative style for all
buildings, and do not claim that added joinery alone establishes fidelity.
Unpublished sections and repeated openings remain bounded exterior estimates.
"""
from pathlib import Path
import json, math
import numpy as np
import trimesh
from shapely.geometry import Point, Polygon, LineString, MultiPoint, box
from shapely.ops import unary_union
from shapely import contains_xy
from shapely.affinity import rotate
from campus_refinement import rebuild as retained_rebuild, oriented
import medical_optimization

CATALOG=json.loads((Path(__file__).resolve().parents[1]/'sources/building_optimization.json').read_text())
SPECS={row['osm_id']:row for row in CATALOG['buildings']}
PERIOD={'gothic_lab','gothic_academic','quad_residence','snell','reynolds','great_hall','cobb','kent','ryerson','isac','ida_noyes','burton','lab_school','gothic_gym','chapel','dining_hall'}
HOUSES={'house','historic_house','tudor_club','tudor_residence','mansion','studios'}

def specification(ident):
    return SPECS[ident]


def roof_shell(p, z, rise, ctx, mat='RoofSlate'):
    """Joined planar wing roofs, preserving the mapped perimeter and courts.

    Fit a bounded number of broad rectangular roof ranges. Their hip planes
    meet along exact straight ridges/valleys; keep only the upper envelope at
    intersections. Fine footprint indents never become spurious little ridges.
    Each visible planar patch is a closed solid down to the supported eave.
    """
    def halfplane(bounds, aa, bb, cc):
        # aa*x + bb*y + cc <= 0, clipped with a convex bounding rectangle.
        x0,y0,x1,y1=bounds
        poly=[(x0,y0),(x1,y0),(x1,y1),(x0,y1)];out=[]
        for v,w in zip(poly,poly[1:]+poly[:1]):
            fv=aa*v[0]+bb*v[1]+cc;fw=aa*w[0]+bb*w[1]+cc
            if fv<=1e-8:out.append(v)
            if (fv<0)!=(fw<0):
                t=fv/(fv-fw);out.append((v[0]+(w[0]-v[0])*t,v[1]+(w[1]-v[1])*t))
        return Polygon(out) if len(out)>2 else Polygon()
    def largest_rectangle(poly, step):
        x0,y0,x1,y1=poly.bounds
        nx=max(1,int(math.ceil((x1-x0)/step)));ny=max(1,int(math.ceil((y1-y0)/step)))
        dx=(x1-x0)/nx;dy=(y1-y0)/ny
        xx,yy=np.meshgrid(x0+(np.arange(nx)+.5)*dx,y0+(np.arange(ny)+.5)*dy)
        inside=contains_xy(poly,xx,yy);heights=np.zeros(nx,dtype=int);best=(0,None)
        for row in range(ny):
            heights=np.where(inside[row],heights+1,0);stack=[]
            for col in range(nx+1):
                height=heights[col] if col<nx else 0;start=col
                while stack and stack[-1][1]>height:
                    left,hh=stack.pop();area=(col-left)*hh
                    if area>best[0]:best=(area,(x0+left*dx,y0+(row+1-hh)*dy,x0+col*dx,y0+(row+1)*dy))
                    start=left
                if not stack or stack[-1][1]<height:stack.append((start,height))
        return best[1]
    for q in ctx.polygons(p):
        rr=np.asarray(q.minimum_rotated_rectangle.exterior.coords);edges=rr[1:]-rr[:-1]
        edge=edges[np.argmax(np.linalg.norm(edges,axis=1))];angle=math.degrees(math.atan2(edge[1],edge[0]))
        origin=q.centroid.coords[0];local=rotate(q,-angle,origin=origin);remaining=local
        step=max(.8,min(1.8,math.sqrt(local.area)/50));wings=[]
        for _ in range(14):
            if remaining.is_empty or remaining.area<max(2,local.area*.006):break
            rect=largest_rectangle(remaining,step)
            if rect is None:break
            x0,y0,x1,y1=rect
            if min(x1-x0,y1-y0)<2.0:break
            pad=step*.75;bounds=(x0-pad,y0-pad,x1+pad,y1+pad)
            mask=box(*bounds);wings.append((bounds,local.intersection(mask)))
            remaining=remaining.difference(mask)
        # A thin full-footprint cap closes tiny service projections and all
        # residual slivers without filling courtyards or adding narrow ridges.
        patches=[(local,(0.,0.,0.))];bounds=local.buffer(5).bounds
        for (x0,y0,x1,y1),wing in wings:
            width=min(x1-x0,y1-y0);slope=min(.85,rise/max(width/2,.1))
            planes=[(slope,0.,-slope*x0),(-slope,0.,slope*x1),(0.,slope,-slope*y0),(0.,-slope,slope*y1),(0.,0.,rise)]
            for plane in planes:
                region=wing
                for other in planes:
                    if other==plane:continue
                    region=region.intersection(halfplane(bounds,plane[0]-other[0],plane[1]-other[1],plane[2]-other[2]))
                    if region.is_empty:break
                if not region.is_empty and region.area>.02:patches.append((region,plane))
        # Union coincident planes before comparison: no overlapping horizontal
        # caps or coplanar facets can flicker when orbiting the building.
        grouped={}
        for region,plane in patches:grouped.setdefault(tuple(round(v,7)for v in plane),[]).append(region)
        patches=[(unary_union(regions),plane)for plane,regions in grouped.items()]
        co=math.cos(math.radians(angle));si=math.sin(math.radians(angle));ox,oy=origin
        for i,(region,plane)in enumerate(patches):
            visible=region
            for j,(other,op)in enumerate(patches):
                if i==j or visible.is_empty:continue
                overlap=visible.intersection(other)
                if overlap.is_empty:continue
                higher=halfplane(bounds,plane[0]-op[0],plane[1]-op[1],plane[2]-op[2]+1e-7)
                visible=visible.difference(overlap.intersection(higher))
            for part in ctx.polygons(visible):
                m=ctx.extrusion(part,z,.13);v=m.vertices.copy();top=v[:,2]>z+.065
                v[top,2]+=np.maximum(0,v[top,0]*plane[0]+v[top,1]*plane[1]+plane[2])
                xx=v[:,0]-ox;yy=v[:,1]-oy;v[:,0]=ox+co*xx-si*yy;v[:,1]=oy+si*xx+co*yy;m.vertices=v
                trimesh.repair.fix_normals(m,multibody=True)
                if not m.is_watertight:raise ValueError('Open roof patch: '+str(q.bounds))
                ctx.ms[mat].append(m)


def facade(ms,p,z,h,levels,gothic,continuous,spacing,ctx):
    cfg=ctx.current_design
    if not cfg or cfg['family']=='protected_highlight':return False
    if cfg.get('medical_profile'):
        medical_optimization.facade(ms,p,z,h,levels,ctx);return True
    family=cfg['family'];period=family in PERIOD or (family=='retained'and cfg.get('retained_profile')in['museum'])
    hall=family in ['sports_hall','dining_hall','great_hall','gothic_gym','chapel','high_bay']
    # Existing individually modeled laboratory ranges retain their actual local
    # storeys; window size never derives from the whole building maximum.
    count=max(1,int(round(levels)));floor=h/count
    if family=='steam_plant':count=1;floor=h
    bay=cfg['bay_m'];glass='WindowGlass';trim='QuadTrim'if period else'Frame'
    stats=ctx.optimization_facades
    for ring in [p.exterior,*p.interiors]:
        cc=np.asarray(ring.coords)
        for aa,bb in zip(cc[:-1],cc[1:]):
            length=np.linalg.norm(bb-aa)
            if length<2.9:continue
            u=(bb-aa)/length;n=np.array([u[1],-u[0]])
            if family in ['archive','service']:
                if length<6:continue
                centers=[aa+u*length*.5];ww=min(4.8,length*.45)
            else:
                bays=max(1,int((length-.8)/bay));step=length/bays
                centers=[aa+u*(j+.5)*step for j in range(bays)]
                ww=min(step*.66,2.9 if period else 3.0)
                if continuous:ww=max(.9,step-.24)
            for k in range(count):
                wh=min(floor*.51,2.45) if not hall else min(h*.60,6.3)
                zz=z+(k+.23)*floor if not hall else z+h*.28
                if family=='steam_plant':wh=h*.62;zz=z+h*.19
                if zz+wh>z+h-.25:continue
                if family in ['service','archive']:
                    wh=min(1.2,wh);zz=z+h*.60
                    if k:continue
                for center in centers:
                    c=center+n*.035
                    pointed=family in ['great_hall','chapel','dining_hall','gothic_gym']
                    shape=[(-ww/2,0),(ww/2,0),(ww/2,wh*.72),(ww*.28,wh*.91),(0,wh),(-ww*.28,wh*.91),(-ww/2,wh*.72)]if pointed else[(-ww/2,0),(ww/2,0),(ww/2,wh),(-ww/2,wh)]
                    pane=ctx.extrusion(Polygon(shape),0,.075);v=pane.vertices.copy();pane.vertices=np.column_stack((c[0]+v[:,0]*u[0]+v[:,2]*n[0],c[1]+v[:,0]*u[1]+v[:,2]*n[1],zz+v[:,1]));trimesh.repair.fix_normals(pane);ms[glass].append(pane)
                    if pointed:
                        profile=Polygon(shape).buffer(.10,join_style=2).difference(Polygon(shape).buffer(-.025,join_style=2))
                        for part in ctx.polygons(profile):
                            frame=ctx.extrusion(part,0,.12);v=frame.vertices.copy();frame.vertices=np.column_stack((c[0]+v[:,0]*u[0]+(.08+v[:,2])*n[0],c[1]+v[:,0]*u[1]+(.08+v[:,2])*n[1],zz+v[:,1]));trimesh.repair.fix_normals(frame);ms[trim].append(frame)
                    else:
                        for off in [-ww/2,ww/2]:ms[trim].append(oriented(ctx,c+u*off+n*.10,u,n,.12,.15,wh+.16,zz-.08))
                        for off in [0,wh]:ms[trim].append(oriented(ctx,c+n*.11,u,n,ww+.24,.15,.14,zz+off-.07))
                    # Paired upper lights, rather than a Gothic point on every office window.
                    if ww>1.5:ms[trim].append(oriented(ctx,c+n*.13,u,n,.08,.10,wh,zz))
                    if family=='steam_plant':
                        for split in [.34,.67]:ms['QuadTrim'].append(oriented(ctx,c+n*.14,u,n,ww,.12,.12,zz+wh*split))
                    if period and ww>2.15:
                        ms[trim].append(oriented(ctx,c+n*.14,u,n,ww,.10,.07,zz+wh*.65))
                    stats['window_groups']+=1
    return True


def finish(p,h,levels,gothic,ctx,kind=None):
    cfg=ctx.current_design;ms=ctx.ms;family=cfg['family']
    if cfg.get('medical_profile'):return medical_optimization.finish(p,h,levels,gothic,ctx,kind)
    # Each actual wall range gets a supported plinth/cornice; no rods extend
    # beyond local eaves, and no arbitrary roof boxes are added.
    courses=0
    for q,z,hh,storeys,arched,continuous in ctx.construction_facades:
        for level in [z+.20,z+hh-.20]:
            edge=q.boundary.buffer(.10,join_style=2).intersection(q.buffer(.055,join_style=2))
            for part in ctx.polygons(edge):ms['QuadTrim'if family in PERIOD else'Metal'].append(ctx.extrusion(part,level,.14));courses+=1
    target={'north':[0,1],'south':[0,-1],'east':[1,0],'west':[-1,0],'southeast':[1,-1]}[cfg['entry']]
    candidates=[]
    for q in ctx.polygons(p):
        cc=np.asarray(q.exterior.coords)
        for aa,bb in zip(cc[:-1],cc[1:]):
            ln=np.linalg.norm(bb-aa)
            if ln<4:continue
            u=(bb-aa)/ln;n=np.array([u[1],-u[0]]);c=(aa+bb)/2
            candidates.append((np.dot(n,target),min(ln,18),c,u,n))
    portal=None
    if candidates and family not in ['garage','greenhouse','gate','field_gate']:
        _,length,c,u,n=max(candidates,key=lambda item:(round(item[0],1),item[1]));width=min(3.6,length*.4)
        if family in HOUSES:width=min(1.45,width)
        doorway=c+n*.10;portal=[*c]
        ms['DoorWood'if family in PERIOD|HOUSES else'WindowGlass'].append(oriented(ctx,doorway,u,n,width,.13,2.6,.12))
        for off in [-width/2-.12,width/2+.12]:ms['QuadTrim'if family in PERIOD else'LightStone'].append(oriented(ctx,c+u*off+n*.16,u,n,.22,.28,2.95,.06))
        ms['QuadTrim'if family in PERIOD else'LightStone'].append(oriented(ctx,c+n*.16,u,n,width+.45,.28,.25,2.82))
        # Stone threshold and two shallow treads meet at the actual facade plane.
        for depth,z in [(1.5,.03),(.95,.09),(.4,.15)]:ms['Concrete'].append(oriented(ctx,c+n*depth/2,u,n,width+.8,depth,.06,z))
    return {'window_surrounds':ctx.optimization_facades['window_groups'],'entrances':int(portal is not None),'buttresses':0,'courses':courses,'entry_ground_xy':portal,'level':'optimized exterior','unpublished_details':'Repeated facade modules and local entrance dimensions are estimates.'}


def rebuild(ident,p,h,levels,ctx):
    cfg=SPECS[ident]
    if cfg['family']=='protected_highlight':return None
    if cfg.get('medical_profile'):return medical_optimization.rebuild(ident,p,h,levels,ctx)
    kind=cfg['family'];ms=ctx.ms;a,b,c,d=p.bounds;cx,cy=p.centroid.coords[0]
    e=cfg['eave_m'];rise=cfg['roof_rise_m'];wall=cfg['wall'];roof=cfg['roof'];features=[]
    def add(g,z,hh,mat=wall,lev=None,windows=True):
        if g.is_empty or hh<=0:return
        ctx.body(g,z,hh,mat,windows=windows,lev=lev if lev is not None else cfg['storeys'],arch=False)
    def cap(g,z,mat=roof):
        for q in ctx.polygons(g):ms[mat].append(ctx.extrusion(q,z,.13))
    def parapet(g,z,mat=wall,hh=.5):
        for q in ctx.polygons(g):
            for strip in ctx.polygons(q.difference(q.buffer(-.25,join_style=2))):ms[mat].append(ctx.extrusion(strip,z,hh))
    def pitch(g,z,rr=rise,mat=roof,axis=None):
        for q in ctx.polygons(g):
            rect=q.minimum_rotated_rectangle
            if not q.interiors and q.area/max(rect.area,1)>.87:
                ms[mat].extend(ctx.pitched(q,z,rr,axis))
            else:roof_shell(q,z-.04,rr,ctx,mat)
    def gables(g,z,front,count=3,rr=3.3):
        # Source-supported principal facade gables: each starts on its wall eave.
        candidates=[]
        for q in ctx.polygons(g):
            cc=np.asarray(q.exterior.coords)
            for aa,bb in zip(cc[:-1],cc[1:]):
                ln=np.linalg.norm(bb-aa)
                if ln<8:continue
                u=(bb-aa)/ln;n=np.array([u[1],-u[0]])
                target={'east':[1,0],'west':[-1,0],'north':[0,1],'south':[0,-1]}[front]
                candidates.append((np.dot(n,target),ln,aa,bb,u,n))
        if not candidates:return
        _,length,aa,bb,u,n=max(candidates,key=lambda x:(round(x[0],1),x[1]))
        count=min(count,max(1,int(length/14)))
        for t in ([.5]if count==1 else np.linspace(.15,.85,count)):
            center=aa+(bb-aa)*t;ww=min(8.0,length/(count+.8));height=min(rr,ww*.52);profile=Polygon([(-ww/2,0),(ww/2,0),(0,height)])
            m=ctx.extrusion(profile,0,.32);v=m.vertices.copy();m.vertices=np.column_stack([center[0]+u[0]*v[:,0]+n[0]*(v[:,2]-.15),center[1]+u[1]*v[:,0]+n[1]*(v[:,2]-.15),z+v[:,1]]);trimesh.repair.fix_normals(m);ms[wall].append(m)
    def garage(g,storeys,hh):
        step=hh/storeys
        for k in range(storeys+1):add(g,k*step,.26,'Concrete',windows=False)
        # Open decks, connected columns and actual floor slabs replace glass window grids.
        for q in ctx.polygons(g):
            cc=np.asarray(q.exterior.coords)
            for aa,bb in zip(cc[:-1],cc[1:]):
                ln=np.linalg.norm(bb-aa)
                if ln<3:continue
                u=(bb-aa)/ln;n=np.array([u[1],-u[0]])
                for t in np.linspace(.02,.98,max(2,int(ln/6.5)+1)):
                    ms['Concrete'].append(oriented(ctx,aa+(bb-aa)*t-n*.25,u,n,.65,.65,hh,0))
                for k in range(storeys):ms['Concrete'].append(oriented(ctx,(aa+bb)/2-n*.12,u,n,ln,.25,.82,k*step+.24))
        core=g.intersection(box(a+.8,b+.8,min(c-1,a+8),min(d-1,b+11)));add(core,0,hh+.9,'LightStone',windows=False)
    if kind=='retained':
        result=retained_rebuild(ident,p,h,levels,ctx)
        assert result,ident
        result['features'].append('Recessed grouped glazing, supported local wall courses and ground-connected entrance')
        result.update(optimization_recipe=cfg,modeling_level='optimized exterior',coverage='Individual profile retained and refined')
        return result
    elif kind in ['garage','garage_office']:
        if kind=='garage':garage(p,cfg['storeys'],e);h=e+.9
        else:
            gp=next(f['poly']for f in ctx.features if f['id']==477223629);garage(gp,9,29.5);other=p.difference(gp);add(other,0,16.7,lev=4);cap(other,16.7);h=30.4
        features=['Open parking decks with connected floor slabs and columns','Solid stair core and low safety parapets; no false glass window grid']
    elif kind=='greenhouse':
        add(p,0,.55,'Concrete',windows=False)
        width=(d-b)/3
        for k in range(3):
            q=p.intersection(box(a-1,b+k*width,c+1,b+(k+1)*width))
            add(q,.55,2.45,'Glass',windows=False);pitch(q,3.0,1.7,'Glass','x')
            for xx in np.arange(a+1,c-1,4):
                ms['Frame'].append(ctx.cylinder((xx,b+k*width,3.05),(xx,b+(k+.5)*width,4.73),.055,6));ms['Frame'].append(ctx.cylinder((xx,b+(k+.5)*width,4.73),(xx,b+(k+1)*width,3.05),.055,6))
        h=4.83;features=['Low three-range glasshouse','Glazed gable roofs and connected metal ribs; no fictitious three-storey academic block']
    elif kind=='high_bay':
        add(p,0,e,'Concrete',lev=1);cap(p,e,'RoofMembrane')
        for yy in np.linspace(b+5,d-7,4):
            q=p.intersection(box(a+.7,yy,c-.7,yy+4.8))
            for part in ctx.polygons(q):
                m=ctx.extrusion(part,e+.1,.12);v=m.vertices;top=v[:,2]>e+.16;v[top,2]+=(v[top,1]-yy)/4.8*rise;ms['RoofMembrane'].append(m)
                glass=part.intersection(box(a,yy+4.62,c,yy+4.8));add(glass,e+.10,rise,'Glass',windows=False)
        h=e+rise+.22;features=['One tall experimental storey with two high bays','Repeated north-light sawtooth clerestories and pale membrane roof','Precast wall panels divided by vertical glass slots']
    elif kind=='international':
        high=p.intersection(box(a-1,b+19,c+1,d+1));low=p.difference(high)
        add(low,0,10.7,'QuadStone',lev=3);pitch(low,10.7,3.4,'RoofClay')
        add(high,0,30.4,'QuadStone',lev=9);cap(high,30.4,'RoofMembrane');parapet(high,30.4,'QuadStone')
        tower=high.intersection(box(a+4,d-22,a+23,d-1));add(tower,30.4,9.2,'QuadStone',lev=3);cap(tower,39.6,'RoofMembrane');parapet(tower,39.6,'QuadTrim',.6)
        h=40.2;features=['Nine-storey north residential bar and lower three-storey south wings','Separate twelve-storey west tower, limestone-toned walls and open mapped court','Low clay roofs distinguish the south arrival from the tall block']
    elif kind=='grossman':
        north=p.intersection(box(a-1,b+(d-b)*.55,c+1,d+1));south=p.difference(north)
        corners=p.intersection(unary_union([box(a-1,d-23,a+23,d+1),box(c-23,b-1,c+1,b+25)]))
        add(north.difference(corners),0,22.8,'WarmBrick',lev=7);cap(north.difference(corners),22.8)
        add(south.difference(corners),0,16.6,'WarmBrick',lev=5);cap(south.difference(corners),16.6)
        add(corners,0,29.4,'LightStone',lev=9);cap(corners,29.4);parapet(corners,29.4,'LightStone')
        h=29.9;features=['Stepped five/seven/nine-storey residential ranges','Buff masonry corner towers and brick courtyard wings','Mapped open courtyards, separate roof levels and recessed punched window groups']
    elif kind=='burton':
        towers=p.intersection(unary_union([box(a+16,d-15,a+27,d+1),box(c-27,d-15,c-16,d+1)]));rest=p.difference(towers)
        add(rest,0,e,lev=4);pitch(rest,e);add(towers,0,22.4,lev=6);cap(towers,22.4,'RoofMembrane');parapet(towers,22.4,'QuadTrim',.8);h=23.2
        features=['Four-storey court wings separated from six-storey north entrance towers','Connected steep wing roofs, grouped masonry windows and preserved court openings']
    elif kind=='dcam':
        add(p,0,8.0,'LightStone',lev=2)
        upper=p.buffer(-.50,join_style=2);add(upper,8,e-8,'LightStone',lev=4);cap(upper,e);parapet(upper,e)
        atrium=upper.intersection(box(c-14,cy-14,c+1,cy+14));add(atrium,8,e-8+3.2,'DarkGlass',lev=4);cap(atrium,e+3.2,'Metal')
        apron=box(c-1,cy-13,c+5,cy+13);ms['Metal'].append(ctx.extrusion(apron,3.7,.20))
        for y in [cy-11,cy+11]:ms['Metal'].append(ctx.cylinder((c+3.8,y,.05),(c+3.8,y,3.7),.15,8))
        h=e+3.35;features=['Six-storey precast medical block','Masonry base, lighter upper glazing and raised east entrance atrium','Connected street canopy with supporting columns']
    elif kind=='ccd':
        add(p,0,55,'LightStone',lev=10);cap(p,55,'RoofMembrane')
        plant=p.buffer(-12,join_style=2).intersection(box(a+8,b+15,c-8,d-15));add(plant,55,74.676-55,'Metal',windows=False);cap(plant,74.546,'Metal');h=74.676
        features=['Retained ten-storey medical body and published 245-foot maximum','Distinct occupied block and setback roof plant','Recessed horizontal glazing groups retain the 5.5 m floor module']
    elif kind=='comer':
        base=p.intersection(box(a-1,b-1,c+1,b+(d-b)*.24));upper=p.difference(base)
        add(base,0,8.2,'LightStone',lev=2);cap(base,8.2);add(upper,0,e,'HospitalBrick',lev=7);cap(upper,e);parapet(upper,e,'HospitalBrick')
        features=['Seven-storey brick and precast patient block','Lower arrival wing and legible grouped patient-room openings'];h=e+.5
    elif kind=='ryerson':
        tower=p.intersection(box(cx-5.2,b-1,cx+5.2,b+12));rest=p.difference(tower)
        add(rest,0,e,lev=4);cap(rest,e);parapet(rest,e,'QuadTrim',.7)
        add(tower,0,23.5,lev=5);cap(tower,23.5,'RoofMembrane');parapet(tower,23.5,'QuadTrim',1.0)
        center=tower.representative_point();base=Point(center.x,center.y).buffer(2.8,quad_segs=12);add(base,23.6,1.2,'Metal',windows=False)
        # Closed hemispherical shell, physically supported by its cylindrical drum.
        m=trimesh.creation.icosphere(subdivisions=2,radius=2.8);m.vertices[:,2]=np.maximum(m.vertices[:,2],0);m.merge_vertices();m.remove_unreferenced_vertices();m=m.convex_hull;m.apply_translation((center.x,center.y,24.8));ms['RoofPatina'].append(m)
        h=27.7;features=['Flat observation deck with masonry parapet','Raised front stair/observatory tower','Supported drum and small green-grey observatory dome']
    elif kind=='kent':
        lecture=p.intersection(Point(a+13,b+19).buffer(13.8,quad_segs=2));rest=p.difference(lecture)
        add(rest,0,e,lev=3);pitch(rest,e);add(lecture,0,8.9,lev=1);pitch(lecture,8.9,4.7)
        h=e+rise+.15;features=['Low octagonal lecture range distinct from taller laboratory wings','Connected slate hip/valley roofs and three-storey limestone bays']
    elif kind=='gate':
        mid=(b+d)/2;opening=box(a-2,mid-1.8,c+2,mid+1.8);legs=p.difference(opening)
        add(legs,0,4.8,lev=1,windows=False);add(p,4.8,e-4.8,lev=1);pitch(p,e)
        profile=Polygon([(-1.8,3.0),(-1.8,4.8),(1.8,4.8),(1.8,3.0),(0,4.5)])
        m=ctx.extrusion(profile,0,c-a);v=m.vertices.copy();m.vertices=np.column_stack((a+v[:,2],mid+v[:,0],v[:,1]));trimesh.repair.fix_normals(m);ms[wall].append(m)
        h=e+rise+.13;features=['Physically open pointed east-west gate passage','Supported upper rooms and pitched roof; no solid block across the pedestrian route']
    elif kind=='steam_plant':
        add(p,0,e,'WarmBrick',lev=5);cap(p,e,'RoofMembrane');parapet(p,e,'WarmBrick',.8)
        for zz in [1.1,e*.32,e-.8]:
            for strip in ctx.polygons(p.boundary.buffer(.11,join_style=2).intersection(p.buffer(.04,join_style=2))):ms['QuadTrim'].append(ctx.extrusion(strip,zz,.20))
        # Two visible flues in the university's built photograph. Their local
        # diameters/heights are proportional exterior estimates, not surveys.
        for fraction,hh in [(.31,14.5),(.67,17.0)]:
            x=a+(c-a)*fraction;y=b+(d-b)*.64
            if not p.buffer(-2).contains(Point(x,y)):x,y=p.representative_point().coords[0];x+=(fraction-.5)*8
            base=Point(x,y).buffer(2.1,quad_segs=2);add(base,e-.15,1.6,'WarmBrick',windows=False)
            ms['Metal'].append(ctx.cylinder((x,y,e+1.1),(x,y,e+hh),1.15,12))
            for zz in [e+1.1,e+hh-1.0]:ms['Metal'].append(ctx.cylinder((x,y,zz),(x,y,zz+.28),1.30,12))
        h=e+17.0;features=['Five-storey-high brick boiler hall with tall divided industrial windows','Supported paired roof flues and horizontal stone courses','Source-specific utility silhouette; flue positions and dimensions are estimated from built photographs']
    elif kind=='studios':
        north=p.intersection(box(a-1,d-16,c+1,d+1));low=p.difference(north)
        add(north,0,6.8,'WarmBrick',lev=2);pitch(north,6.8,3.4)
        add(low,0,5.0,'WarmBrick',lev=1);pitch(low,5.0,3.0)
        h=10.4;features=['Separate house and low studio/barn ranges','Connected pitched roofs and tall studio lights; not a four-storey office block']
    else:
        if kind in ['great_hall','dining_hall','chapel','sports_hall','gothic_gym']:
            add(p,0,e,lev=1);pitch(p,e,mat=roof,axis='x'if kind=='chapel'else None)
            features=['Single tall hall rather than stacked classroom window rows','Separate wall/eave/ridge heights and connected steep roof']
        elif kind=='pick':
            add(p,0,e,'Concrete',lev=4);cap(p,e);parapet(p,e,'Concrete',.8)
            features=['Brutalist concrete massing with recessed rectangular vertical bays','Retained stepped footprint and flat parapet roof; removed invented Gothic roof']
        else:
            add(p,0,e,lev=cfg['storeys'])
            if rise:pitch(p,e)
            else:cap(p,e);parapet(p,e)
            features=['Individual mapped wings, setbacks and courtyard voids','Grouped recessed facade bays with supported lintels, sills and thin mullions',cfg['roof_form']]
        h=e+rise+.25 if rise else e+.5
        if kind in ['cobb','lab_school','isac','snell','reynolds','ida_noyes','tudor_club','mansion']:
            gables(p,e,cfg['entry']if cfg['entry']in['north','south','east','west']else'east',5 if kind=='cobb'else 3,min(rise,4.0))
            features.append('Principal entrance-side gables articulated independently of the roof plane')
        if kind in ['hospital','historic_hospital','hospital_low','modern_academic','modern_annex','laboratory','brick_academic','apartment']:
            # At real facade ranges only: slab rhythm remains attached to its wall.
            for k in range(1,cfg['storeys']):
                if kind=='historic_hospital'and k%2:continue
                z=k*e/cfg['storeys']
                for q in ctx.polygons(p.boundary.buffer(.07,join_style=2).intersection(p.buffer(.02,join_style=2))):ms['QuadTrim'if kind=='historic_hospital'else'Concrete'].append(ctx.extrusion(q,z,.10))
        if kind=='archive':features=['Brick archive/stack volume with limited high windows','Broad closed wall areas and shallow supported flat-roof parapet']
    result={'profile':kind,'height':h,'levels':cfg['storeys'],'features':features,'reference':cfg['references'][0],'modeling_level':'optimized exterior','optimization_recipe':cfg,'approximation':cfg['evidence']}
    return result
