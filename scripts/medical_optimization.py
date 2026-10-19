"""Source-informed medical-side optimized exteriors.

Owner/architect photographs establish major silhouettes and facade character;
local section dimensions and secondary ranges are explicitly estimated. No
interiors, measured construction accuracy or new unbuilt projects are implied.
"""
import math
import numpy as np
import trimesh
from shapely.geometry import Polygon, Point, LineString, box
from shapely.ops import unary_union
from campus_refinement import oriented, rebuild as retained_rebuild

HISTORIC={'hull_gothic','hull_culver','abbott','billings','lying_in','historic_lab','bobs_roberts'}

def walls(p):
    for ring in [p.exterior,*p.interiors]:
        cc=np.asarray(ring.coords)
        for a,b in zip(cc[:-1],cc[1:]):
            length=np.linalg.norm(b-a)
            if length>2.8:
                u=(b-a)/length;n=np.array([u[1],-u[0]])
                yield a,b,u,n,length


def facade(ms,p,z,h,levels,ctx):
    cfg=ctx.current_design;profile=cfg['medical_profile'];historic=profile in HISTORIC
    count=max(1,int(round(levels)));step=h/count
    style=cfg.get('_medical_facade','punched')
    for a,b,u,n,length in walls(p):
        bay=4.4 if historic else 4.8
        count_bay=max(1,int((length-.6)/bay));spacing=length/count_bay
        for k in range(count):
            wh=min(2.35,step*.56);zz=z+(k+.24)*step
            if style=='clerestory':
                if k:continue
                wh=min(1.1,h*.18);zz=z+h-wh-.6
            if zz+wh>z+h-.20:continue
            for j in range(count_bay):
                c=a+u*(j+.5)*spacing+n*.055;ww=min(2.6,spacing*.65)
                arched=historic and k==count-1 and count>1
                if arched:
                    shape=Polygon([(-ww/2,0),(ww/2,0),(ww/2,wh*.73),(ww*.27,wh*.94),(0,wh),(-ww*.27,wh*.94),(-ww/2,wh*.73)])
                    for poly,mat,depth,offset in [(shape,'MedicalGlass',.07,0),(shape.buffer(.1,join_style=2).difference(shape.buffer(-.02,join_style=2)),'QuadTrim',.12,.08)]:
                        for part in ctx.polygons(poly):
                            m=ctx.extrusion(part,0,depth);v=m.vertices.copy();m.vertices=np.column_stack((c[0]+v[:,0]*u[0]+(v[:,2]+offset)*n[0],c[1]+v[:,0]*u[1]+(v[:,2]+offset)*n[1],zz+v[:,1]));trimesh.repair.fix_normals(m);ms[mat].append(m)
                else:
                    ms['MedicalGlass'].append(oriented(ctx,c,u,n,ww,.09,wh,zz))
                    for x in [-ww/2,ww/2]:ms['QuadTrim'if historic else'MedicalSteel'].append(oriented(ctx,c+u*x+n*.09,u,n,.11,.13,wh+.13,zz-.06))
                    for dz in [0,wh]:ms['QuadTrim'if historic else'MedicalSteel'].append(oriented(ctx,c+n*.1,u,n,ww+.22,.14,.11,zz+dz-.055))
                ms['QuadTrim'if historic else'MedicalSteel'].append(oriented(ctx,c+n*.14,u,n,.085,.12,wh,zz))
                ctx.optimization_facades['window_groups']+=1


def finish(p,h,levels,gothic,ctx,kind=None):
    cfg=ctx.current_design;profile=cfg['medical_profile'];stats=ctx.campus_refinement['medical_detail']
    for q,z,hh,_,_,_ in ctx.construction_facades:
        for zz in [z+.18,z+hh-.22]:
            for part in ctx.polygons(q.boundary.buffer(.08,join_style=2).intersection(q.buffer(.035,join_style=2))):ctx.ms['QuadTrim'if profile in HISTORIC else'MedicalSteel'].append(ctx.extrusion(part,zz,.12))
    return {'window_surrounds':ctx.optimization_facades['window_groups'],'entrances':len(stats['entries']),'buttresses':0,'courses':len(ctx.construction_facades)*2,'level':'optimized exterior','entry_ground_xy':stats['entries'][0]['center']if stats['entries']else None,'unpublished_details':'Medical exterior section heights, secondary openings and canopy dimensions remain estimates.'}


def rebuild(ident,p,h,levels,ctx):
    cfg=ctx.current_design;profile=cfg['medical_profile'];ms=ctx.ms;a,b,c,d=p.bounds;cx,cy=p.centroid.coords[0]
    top=cfg['eave_m'];storeys=cfg['storeys'];features=[];entries=[];ranges=[]
    def add(g,z,hh,mat='MedicalStone',lev=1,windows=True,style='punched'):
        if hh<=.01:return
        cfg['_medical_facade']=style
        ctx.body(g,z,hh,mat,lev=lev,windows=windows,arch=False)
        cfg.pop('_medical_facade',None)
        if not g.is_empty:ranges.append({'z':z,'top':z+hh,'material':mat,'area':g.area})
    def solid(g,z,hh,mat):
        for q in ctx.polygons(g):ms[mat].append(ctx.extrusion(q,z,hh))
    def cap(g,z,mat='RoofMembrane'):solid(g,z,.14,mat)
    def edge(g,z,hh=.35,mat='MedicalStone',thick=.2):
        for q in ctx.polygons(g):solid(q.buffer(.20,join_style=2).difference(q.buffer(-thick,join_style=2)),z,hh,mat)
    def ribbon(g,z,wh,glass='MedicalGlass',spacing=3.2):
        for q in ctx.polygons(g):
            for aa,bb,u,n,ln in walls(q):
                width=ln-.45
                if width<2:continue
                center=(aa+bb)/2+n*.065
                ms[glass].append(oriented(ctx,center,u,n,width,.11,wh,z))
                for zz in [z,z+wh]:ms['MedicalSteel'].append(oriented(ctx,center+n*.07,u,n,width,.12,.09,zz-.045))
                cells=max(1,int(width/spacing))
                for j in range(1,cells):ms['MedicalSteel'].append(oriented(ctx,center+u*(j/cells-.5)*width+n*.08,u,n,.08,.13,wh,z))
    def glazed(g,z,hh,glass='MedicalGlass',floors=1):
        add(g,z,hh,glass,windows=False);ribbon(g,z+.10,hh-.20,glass)
        for zz in np.linspace(z,z+hh,floors+1):edge(g,float(zz),.10,'MedicalSteel',.10)
    def roof(g,z,rr):
        ctx.roof_shell(g,z,rr,ctx,'RoofSlate')
    def pickwall(direction,at=None):
        target={'north':[0,1],'south':[0,-1],'east':[1,0],'west':[-1,0]}[direction]
        candidates=[]
        for q in ctx.polygons(p):
            for aa,bb,u,n,ln in walls(q):
                if ln<4:continue
                cc=(aa+bb)/2;score=np.dot(n,target)
                if at is not None:score-=np.linalg.norm(cc-np.array(at))*.015
                candidates.append((round(score,1),min(ln,22),cc,u,n,ln))
        return max(candidates,key=lambda v:v[:2])if candidates else None
    def entry(direction=cfg['entry'],width=5.2,canopy=True,at=None,landing=.12):
        found=pickwall(direction,at)
        if found is None:return
        _,_,cc,u,n,ln=found;width=min(width,ln*.75)
        # Vertical glazing and threshold meet the actual mapped street wall.
        ms['MedicalGlass'].append(oriented(ctx,cc+n*.11,u,n,width,.14,3.0,landing))
        for x in [-width/2,width/2]:ms['MedicalSteel'].append(oriented(ctx,cc+u*x+n*.2,u,n,.13,.18,3.1,landing))
        ms['MedicalSteel'].append(oriented(ctx,cc+n*.21,u,n,.1,.15,3.0,landing))
        for depth,zz in [(2.2,.02),(1.3,.07),(.5,.12)]:ms['Paving'].append(oriented(ctx,cc+n*depth/2,u,n,width+1,depth,.06,zz))
        if canopy:
            depth=3.5
            ms['MedicalSteel'].append(oriented(ctx,cc+n*depth/2,u,n,width+1.8,depth,.19,3.45))
            for sign in [-1,1]:ms['MedicalSteel'].append(oriented(ctx,cc+u*sign*(width/2+.5)+n*(depth-.35),u,n,.15,.15,3.45,.02))
        entries.append({'center':cc.tolist(),'direction':direction,'canopy':canopy,'grade':0.0})
    def panel_grid(g,height,bay=9.6):
        for q in ctx.polygons(g):
            for aa,bb,u,n,ln in walls(q):
                for j in range(1,max(1,int(ln/bay))):
                    cc=aa+(bb-aa)*j/max(1,int(ln/bay))+n*.12
                    ms['MedicalSteel'].append(oriented(ctx,cc,u,n,.09,.12,height,.10))
    if profile=='ccd':
        # The seventh level is an actual recessed envelope, not a painted stripe.
        lower=33.0;sky=5.5;upper=55.0-(lower+sky);inset=p.buffer(-2.6,join_style=2)
        add(p,0,lower,'MedicalStone',windows=False)
        for k in range(6):ribbon(p,k*5.5+1.05,2.45,'MedicalSilverGlass',3.2)
        glazed(inset,lower,sky,'MedicalDarkGlass',1)
        for q in ctx.polygons(p):
            for aa,bb,u,n,ln in walls(q):
                for t in np.arange(3,ln-1,9.6):ms['MedicalSteel'].append(oriented(ctx,aa+u*t-n*.22,u,n,.24,.34,sky,lower))
        add(p,lower+sky,upper,'MedicalStone',windows=False)
        for k in range(3):ribbon(p,lower+sky+k*5.5+.95,2.75,'MedicalSilverGlass',3.2)
        cap(p,55.0);edge(p,55.0,.55,'MedicalSteel')
        # Broad integrated dark plant plinth, with two discrete tall exhaust/core
        # heads from the built photographs. Retain the documented maximum.
        plant=p.buffer(-6,join_style=2);add(plant,55.0,10.2,'MedicalPlant',windows=False);cap(plant,65.2,'MedicalPlant')
        for fraction in [.30,.70]:
            x=a+(c-a)*fraction;head=p.intersection(box(x-4,b+8,x+4,d-8));add(head,65.2,74.676-65.2,'MedicalSteel',windows=False);cap(head,74.536,'MedicalSteel')
        panel_grid(p,55.0,9.6);entry('south',9.0,True);h=74.676
        features=['Ten occupied floors with 5.5 m section module and continuous horizontal glazing','Genuinely inset seventh-floor Sky Lobby separating treatment and patient blocks','Integrated dark rooftop plant with two narrow raised heads, retaining published maximum','Grounded main entrance canopy; mapped bridge links remain separate']
    elif profile=='dcam':
        add(p,0,9.0,'MedicalStone',lev=2)
        upper=p.buffer(-.38,join_style=2);add(upper,9,17.8,'MedicalStone',windows=False);cap(upper,26.8)
        # Tall grouped curtain bays stop below the massive precast roof frame.
        for q in ctx.polygons(upper):
            for aa,bb,u,n,ln in walls(q):
                if ln<10:continue
                groups=max(1,int(ln/14));step=ln/groups
                for j in range(groups):
                    cc=aa+u*(j+.5)*step+n*.07;ww=min(7.4,step*.60)
                    ms['MedicalDarkGlass'].append(oriented(ctx,cc,u,n,ww,.12,15.2,10.0))
                    for split in [-.36,-.12,.12,.36]:ms['QuadTrim'].append(oriented(ctx,cc+u*ww*split+n*.13,u,n,.13,.16,15.2,10.0))
                    for zz in [13.9,17.8,21.7]:ms['MedicalSteel'].append(oriented(ctx,cc+n*.14,u,n,ww,.14,.11,zz))
        # Raised precast end piers and open-looking roof frames are attached to
        # the occupied block, unlike detached facade rods.
        towers=p.intersection(unary_union([box(c-12,b-1,c+1,b+23),box(c-12,d-24,c+1,d+1)]))
        add(towers,26.8,2.6,'MedicalStone',windows=False);edge(upper,26.8,.55,'MedicalStone',.45)
        entry('east',11.0,True,at=(c,cy));h=29.4
        features=['Six-storey precast envelope, massive lower floors and tall grouped upper glazing','Attached raised corner piers and a continuous roof frame','Maryland Avenue glazed entrance and wide supported canopy','Mapped concave street corners and raised connectors retained']
    elif profile in ['comer','comer_east']:
        if profile=='comer':
            add(p,0,7.2,'MedicalStone',windows=False);ribbon(p,.7,5.9,'MedicalGreenGlass')
            main=p.buffer(-.28,join_style=2);add(main,7.2,22.3,'MedicalGreenGlass',windows=False)
            for zz in np.linspace(7.2,29.5,7):edge(main,float(zz),.18,'MedicalStone',.23)
            ribbon(main,7.35,21.9,'MedicalGreenGlass',2.9)
            for zz in np.linspace(7.2,29.5,7):edge(main,float(zz),.12,'MedicalSteel',.12)
            # Limestone vertical stair/service blades are solidly connected.
            for fraction in [.22,.71]:
                blade=p.intersection(box(a+(c-a)*fraction-2,b-1,a+(c-a)*fraction+2,d+1));add(blade,0,30.8,'MedicalStone',windows=False)
            cap(main,29.5);entry('north',8.0,True);h=30.8;storeys=7
            features=['Seven-storey green-tinted glazed hospital with pale precast base','Layered curtain-wall floor bands and attached limestone vertical service blades','Two-storey transparent north entrance and supported arrival canopy','Replaces the incorrect all-brick classroom-block character']
        else:
            add(p,0,8,'MedicalStone',lev=2);upper=p.buffer(-.45,join_style=2);add(upper,8,17.5,'MedicalStone',lev=4,windows=False)
            for zz in [9.2,13.1,17.0,20.9]:ribbon(upper,zz,1.8,'MedicalGreenGlass',3.8)
            cap(upper,25.5);entry('north',5.4,False);h=25.65
            features=['Lower pale clinical base and differentiated upper patient-room range','Green-tinted glazing relates to the adjoining Comer hospital','Connected eaves, entrance threshold and preserved side links']
    elif profile=='knapp_discovery':
        add(p,0,7.6,'MedicalStone',lev=2);upper=p.buffer(-.65,join_style=2)
        add(upper,7.6,29.0,'MedicalSilverGlass',windows=False);ribbon(upper,7.7,28.8,'MedicalSilverGlass',2.2)
        for zz in np.linspace(7.6,36.6,9):edge(upper,float(zz),.18,'MedicalSteel',.20)
        stair=p.intersection(box(c-6,b+(d-b)*.28,c-.1,b+(d-b)*.47));glazed(stair,0,36.8,'MedicalGreenGlass',10)
        plant=upper.buffer(-2,join_style=2);add(plant,36.6,3.5,'MedicalPlant',windows=False);cap(upper.buffer(.6,join_style=2),40.1,'MedicalSteel')
        entry('east',5.2,True);h=40.26;storeys=10
        features=['Ten-storey glass laboratory range above a limestone two-storey base','Narrow vertical green-glass stair accent and continuous silver floor bands','Setback dark screened service roof and thin overhanging metal coping']
    elif profile in ['bslc','knapp_research','roof_greenhouse']:
        if profile=='roof_greenhouse':
            add(p,0,17.2,'MedicalStone',lev=4);cap(p,17.2)
            width=(d-b)/3
            for k in range(3):
                q=p.intersection(box(a,b+k*width,c,b+(k+1)*width));glazed(q,17.34,2.15,'MedicalSilverGlass',1)
                for poly in ctx.polygons(q):ms['MedicalSilverGlass'].extend(ctx.pitched(poly,19.49,1.7,'x'))
                for xx in np.arange(a+1,c-1,4):
                    for yy in [b+k*width,b+(k+1)*width]:ms['MedicalSteel'].append(ctx.cylinder((xx,yy,19.50),(xx,b+(k+.5)*width,21.31),.055,6))
            h=21.31;storeys=4
            features=['Rooftop research greenhouse raised above a supported four-storey base','Three joined glass roof ranges align with the Donnelley/Knapp complex','Mapped greenhouse outline and ground-connected support retained; no floating greenhouse']
        else:
            height=17.2 if profile=='bslc'else 20.8;storeys=4 if profile=='bslc'else 5
            add(p,0,height,'MedicalStone',lev=storeys);cap(p,height)
            # South entrance-side glazing tower/atrium and attached pale piers.
            strip=p.intersection(box(a+(c-a)*.36,b-1,a+(c-a)*.64,b+5.0));glazed(strip,.15,height-.25,'MedicalDarkGlass',storeys)
            for fraction in [.34,.66]:
                pier=p.intersection(box(a+(c-a)*fraction-.55,b-1,a+(c-a)*fraction+.55,b+5.2));add(pier,0,height+.5,'MedicalStone',windows=False)
            entry('south',5.2,True);h=height+.5
            features=['Separate teaching/research mass with grouped stone window bays','Attached tall glazed entrance bay with continuous structural piers','Roof grade coordinated with the adjoining elevated greenhouse']
    elif profile=='cummings':
        result=retained_rebuild(ident,p,h,levels,ctx);h=result['height'];storeys=result['levels'];entry('west',4.5,True)
        features=result['features']+['Medical-campus facade rhythm and grounded entrance checked; no detached vent rods']
    elif profile in ['billings','lying_in','abbott','historic_lab','hull_gothic','hull_culver','bobs_roberts']:
        height=cfg['eave_m'];base=p
        add(base,0,height,'MedicalStone',lev=cfg['storeys']);cap(base,height);edge(base,height,.6,'MedicalStone')
        if profile=='lying_in':
            roof(base,height,3.6)
            tower=p.intersection(box(cx-7.2,b+39,cx+7.2,b+56));add(tower,height,15.4,'MedicalStone',lev=3);cap(tower,height+15.4);edge(tower,height+15.4,.7,'QuadTrim',.38)
            for q in ctx.polygons(tower):
                for aa,bb,u,n,ln in walls(q):
                    for x in [-ln*.30,0,ln*.30]:ms['MedicalDarkGlass'].append(oriented(ctx,(aa+bb)/2+u*x+n*.1,u,n,min(1.15,ln*.18),.12,4.8,height+7.4))
            # Low front cloister: physically open arches, supported upper lintel.
            side=pickwall('south');_,_,cc,u,n,ln=side;width=min(30,ln-1)
            zz=3.3;depth=2.3
            ms['QuadTrim'].append(oriented(ctx,cc+n*depth/2,u,n,width,depth,.28,zz))
            for off in np.linspace(-width/2,width/2,max(3,int(width/3.6)+1)):ms['MedicalStone'].append(oriented(ctx,cc+u*off+n*(depth-.25),u,n,.40,.45,zz,0))
            for q in ctx.polygons(tower):
                ta,tb,tc,td=q.bounds
                for xx,yy in [(ta+.8,tb+.8),(ta+.8,td-.8),(tc-.8,tb+.8),(tc-.8,td-.8)]:
                    if q.contains(Point(xx,yy)):ms['QuadTrim'].append(ctx.cylinder((xx,yy,height+14),(xx,yy,height+17),.25,6))
            entry('south',4.5,False);h=height+17.0
            features=['Lower historic maternity-hospital wings and connected slate roofs','Central raised stone tower with deep vertical lights and restrained corner pinnacles','Grounded south cloister columns, continuous lintel and entrance threshold','Preserved mapped inner court and west-side outline']
        elif profile=='billings':
            tower_masks=[]
            for xx in [a+16,c-14]:tower_masks.append(p.intersection(box(xx,b-1,xx+14,b+19)))
            towers=unary_union(tower_masks);add(towers,height,8.5,'MedicalStone',lev=2);cap(towers,height+8.5);edge(towers,height+8.5,.55,'QuadTrim')
            # Tall masonry tracery surround groups on the south-facing main range.
            for q in ctx.polygons(p):
                for aa,bb,u,n,ln in walls(q):
                    if n[1]>-.8 or ln<12:continue
                    for off in np.arange(3,ln-2,4.6):
                        cc=aa+u*off+n*.15;ms['QuadTrim'].append(oriented(ctx,cc,u,n,.16,.25,height-6,5.7))
            entry('south',5.8,False);h=height+9.05
            features=['Six-storey historic stone court ranges and two raised south-front tower masses','Tall grouped upper lights, continuous masonry mullions and low parapet roof','Open original courtyards; differentiated towers replace the flat generic hospital roof']
        elif profile=='abbott':
            tower=p.intersection(box(cx-7,d-12,cx+7,d+1));add(tower,height,2.3,'MedicalStone',windows=False);cap(tower,height+2.3)
            entry('north',5.2,False);h=height+2.44
            features=['Historic five-storey stone laboratory facade, independent of GCIS behind','Grouped rectangular lower windows and pointed upper lights','Raised north entrance bay and connected parapet cap']
        else:
            if profile in ['hull_gothic','hull_culver']:roof(p,height,3.6)
            if profile=='bobs_roberts':
                upper=p.buffer(-2,join_style=2);add(upper,height,.7,'MedicalStone',windows=False);cap(upper,height+.7)
            entry(cfg['entry'],3.8,False);h=height+(3.73 if profile in ['hull_gothic','hull_culver']else .84)
            features=['Individual mapped historic research/hospital footprint and open court recesses','Stone facade with paired lower lights and pointed upper grouping','Local parapet/roof and street-facing entrance connected to their supports']
    elif profile=='goldblatt_entry':
        add(p,0,top,'MedicalStone',lev=2);cap(p,top);edge(p,top,.35,'MedicalStone')
        found=pickwall(cfg['entry']);_,_,cc,u,n,ln=found;ww=min(7.8,ln*.65)
        # A deep glazed portal and attached pale side piers replace a generic
        # punched-wall door. The raised landing and side ramp both meet grade.
        ms['MedicalDarkGlass'].append(oriented(ctx,cc+n*.12,u,n,ww,.14,5.0,.45))
        for sign in [-1,1]:ms['MedicalStone'].append(oriented(ctx,cc+u*sign*(ww/2+.25)+n*.45,u,n,.5,1.1,5.6,.0))
        ms['MedicalStone'].append(oriented(ctx,cc+n*.45,u,n,ww+1,1.1,.42,5.45))
        ms['Paving'].append(oriented(ctx,cc+n*1.4,u,n,ww+1,2.8,.46,0))
        for k in range(3):ms['Paving'].append(oriented(ctx,cc+n*(2.8+k*.4),u,n,ww*.65,.4,.15*(3-k),0))
        ramp_center=cc+u*(ww/2+2.8)+n*1.3
        ramp=oriented(ctx,ramp_center,u,n,5.4,2.4,.12,0);v=ramp.vertices.copy();top_vertices=v[:,2]>.06;v[top_vertices,2]=.255+(v[top_vertices,:2]-ramp_center)@u*.45/5.4;v[~top_vertices,2]=0;ramp.vertices=v;ms['Paving'].append(ramp)
        for side in [-1,1]:
            for pos in [-2.6,0,2.6]:
                point=ramp_center+u*pos+n*side*1.1;z=.225+pos*.45/5.4
                ms['Furniture'].append(ctx.cylinder((*point,z),(*point,z+.93),.035,6))
            p1=ramp_center-u*2.6+n*side*1.1;p2=ramp_center+u*2.6+n*side*1.1
            ms['Furniture'].append(ctx.cylinder((*p1,.94),(*p2,1.38),.035,6))
        entries.append({'center':cc.tolist(),'direction':cfg['entry'],'canopy':False,'grade':0.0});h=top+.35
        features=['Low stone entrance pavilion with deep framed glazed portal','Connected raised arrival landing, three steps and a side ramp with handrails','Mapped footprint and adjoining hospital links retained']
    elif profile in ['garage','materials']:
        count=cfg['storeys'];height=cfg['eave_m'];step=height/count
        for k in range(count+1):add(p,k*step,.24,'Concrete',windows=False)
        for q in ctx.polygons(p):
            for aa,bb,u,n,ln in walls(q):
                for tt in np.linspace(.02,.98,max(2,int(ln/6.2)+1)):
                    ms['MedicalStone'].append(oriented(ctx,aa+(bb-aa)*tt-n*.22,u,n,.65,.70,height,0))
                for k in range(count):ms['MedicalStone'].append(oriented(ctx,(aa+bb)/2-n*.15,u,n,ln,.28,.82,k*step+.22))
        # Corner stair core, decks and safety edges remain fully grounded.
        core=p.intersection(box(c-7,b,c,b+11));add(core,0,height+.8,'MedicalStone',windows=False);cap(core,height+.8)
        if profile=='materials':
            loading=p.intersection(box(a,b,c,b+18));add(loading,0,4.5,'MedicalStone',windows=False);ribbon(loading,.7,2.6,'MedicalDarkGlass',5)
        h=height+.94;features=['Open parking deck slabs, attached columns and continuous safety parapets','Legible corner stair core and grounded ramp/entry frontage','Materials/receiving ground floor remains enclosed where mapped']
    else:
        # Explicit individual satellite recipes below keep their mapped form;
        # local setbacks are estimated and do not invent extra storeys/towers.
        height=cfg['eave_m'];floor=height/max(1,storeys)
        brick=profile in ['brick_school','bobs_roberts'];mat='WarmBrick'if brick else'MedicalStone'
        if profile in ['service','service_lab','imaging']:
            add(p,0,height,mat,lev=storeys,style='clerestory');cap(p,height);edge(p,height,.35,mat)
            entry(cfg['entry'],4.8,profile=='imaging');h=height+.35
            features=['Low research/support volume with limited clerestory openings','Thin attached parapet and ground-connected service entrance','Individual mapped setbacks retained without generic rooftop boxes']
        elif profile in ['peck','rubloff','gilman','research_court','research_slab','wyler','mitchell']:
            lower=min(7.8,height*.31);upper=p.buffer(-.45,join_style=2)
            add(p,0,lower,mat,lev=2);add(upper,lower,height-lower,mat,windows=False);cap(upper,height);edge(upper,height,.4,mat)
            rows=max(1,storeys-2);step=(height-lower)/rows
            for k in range(rows):ribbon(upper,lower+k*step+.55,step*.55,'MedicalSilverGlass',3.7)
            if profile=='mitchell':
                # Maryland-facing two-storey glazed arrival and deep overhang.
                arrival=p.intersection(box(a,b+5,a+13,d-5));glazed(arrival,.2,7.7,'MedicalDarkGlass',2);entry('west',9.0,True)
            else:entry(cfg['entry'],6.0 if profile=='rubloff'else 4.5,profile in ['wyler','rubloff'])
            if profile in ['rubloff','research_court']:
                end=p.intersection(box(c-7,b,c,d));add(end,height,1.5,mat,windows=False);cap(end,height+1.5)
            h=height+(1.64 if profile in ['rubloff','research_court']else .4)
            features=['Separate clinical base and upper ward/laboratory ranges','Continuous recessed window ribbons follow the local floors','Individual mapped courts and stepped end bays retained','Maryland arrival is differentiated from the research/service side']
        else:
            add(p,0,height,mat,lev=storeys);cap(p,height);edge(p,height,.35,mat)
            if profile=='wellness':
                glazed(p.intersection(box(a,b,c,b+5)),.18,3.9,'MedicalGreenGlass',1)
            entry(cfg['entry'],4.5,profile in ['wellness','low_laboratory']);h=height+.35
            features=['Individual teaching/research footprint with differentiated glazed entry range','Connected local roof/parapet and supported entrance canopy','Facade grouping and ground frontage refined without raising an undifferentiated block']
    detail={'profile':profile,'entries':entries,'section_ranges':ranges,'source_scope':cfg['medical_evidence'],'dimensions':'Unpublished local sections and small members remain proportional exterior estimates.'}
    return {'profile':profile,'height':h,'levels':storeys,'features':features,'reference':cfg['medical_reference'],'modeling_level':'optimized exterior','optimization_recipe':cfg,'approximation':cfg['medical_evidence'],'medical_detail':detail}
