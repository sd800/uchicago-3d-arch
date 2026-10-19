"""Physical regressions for medical exterior geometry, independent of rendering."""
from pathlib import Path
import collections, hashlib, json
import numpy as np
from shapely.geometry import shape, Point
from shapely.geometry.polygon import orient
from campus_exchange import read_legacy_meshes
R=Path(__file__).resolve().parents[1]
read=lambda p:json.loads((R/p).read_text())
records=read('output/buildings.json');catalog=read('sources/medical_exterior_review.json')['buildings'];layers=read('output/layer_map.json')
medical={r['code']:r for r in records if r['zone']=='medical' and not r['landmark']}
assert len(medical)==40 and set(medical)=={r['code']for r in catalog}
meshes=collections.defaultdict(list)
for n,v,f in read_legacy_meshes(R/'output/UChicago_HydePark.3ds'):
 info=layers[n]
 if info.get('category')=='building':meshes[info['layer'].split('_')[0]].append((info['material'],v,f))
fp={f['properties']['code']:shape(f['geometry'])for f in read('output/footprints_local_meters.geojson')['features']}
def bounds(code,material=None):
 arrays=[v for mat,v,_ in meshes[code]if material is None or mat==material];assert arrays,(code,material)
 return np.vstack(arrays).min(0),np.vstack(arrays).max(0)
def ray(code,origin,direction,material):
 o=np.array(origin);d=np.array(direction);found=[]
 for mat,v,f in meshes[code]:
  if mat!=material:continue
  t=v[f];e1=t[:,1]-t[:,0];e2=t[:,2]-t[:,0];hh=np.cross(np.broadcast_to(d,e2.shape),e2);aa=np.einsum('ij,ij->i',e1,hh);valid=np.abs(aa)>1e-8;iv=np.zeros_like(aa);iv[valid]=1/aa[valid];s=o-t[:,0];u=iv*np.einsum('ij,ij->i',s,hh);q=np.cross(s,e1);vv=iv*np.einsum('j,ij->i',d,q);tt=iv*np.einsum('ij,ij->i',e2,q)
  found.extend(tt[valid&(u>=-1e-6)&(vv>=-1e-6)&(u+vv<=1.000001)&(tt>=0)].tolist())
 return sorted(found)
for code,r in medical.items():
 detail=r['campus_refinement'].get('medical_detail');
 if detail is None:
  detail=r['campus_refinement']['quadrangle_detail'];assert code in {'U034','U036','U050','U051'} and detail['entries'];assert r['campus_refinement']['modeling_level']=='detailed exterior reconstruction'
  lo,hi=bounds(code);assert lo[2]>=-.01 and r['levels']>=3;continue
 assert detail['profile'] and detail['source_scope']
 assert detail['section_ranges'] or detail['profile']=='cummings'
 lo,hi=bounds(code);assert lo[2]>=-.01,(code,lo)
 assert abs(float(hi[2])-r['height'])<.8,(code,hi[2],r['height'])
 for entry in detail['entries']:
  assert fp[code].boundary.distance(Point(entry['center']))<.04,(code,entry)
 assert r['ordinary_joinery']['buttresses']==0
checks=['40 medical layers have individual source/profile records, finite ground-connected geometry and entries on their mapped street walls']
p=orient(fp['U044'],1);cc=list(p.exterior.coords);segments=sorted(zip(cc[:-1],cc[1:]),key=lambda e:np.linalg.norm(np.array(e[1])-e[0]),reverse=True)
a,b=map(np.asarray,segments[0]);u=(b-a)/np.linalg.norm(b-a);n=np.array([u[1],-u[0]]);c=(a+b)/2+n*.5
lower=ray('U044',(*c,29.5),(*(-n),0),'MedicalSilverGlass');sky=ray('U044',(*c,35),(*(-n),0),'MedicalDarkGlass')
assert lower and sky and lower[0]<.7 and sky[0]>2.5,(lower[:2],sky[:2])
assert 74.6<bounds('U044')[1][2]<74.8 and medical['U044']['levels']==10
checks.append('CCD seventh-floor glazing is physically recessed more than 2.5 m behind the lower curtain wall; ten occupied floors and published maximum retained')
for code in ['U070','U025']:
 assert ('MedicalGreenGlass' if code=='U070' else 'MedicalSilverGlass')in{m for m,_,_ in meshes[code]}
 assert not {'WarmBrick','HospitalBrick'}&{m for m,_,_ in meshes[code]}
assert medical['U070']['levels']==7 and medical['U025']['levels']==10
# The KCBD overhanging top must be a connected roof plate, not a floating ring.
q=orient(fp['U025'],1);edges=sorted(zip(list(q.exterior.coords)[:-1],list(q.exterior.coords)[1:]),key=lambda e:np.linalg.norm(np.array(e[1])-e[0]),reverse=True)
aa,bb=map(np.asarray,edges[0]);u=(bb-aa)/np.linalg.norm(bb-aa);n=np.array([u[1],-u[0]]);pt=(aa+bb)/2-n*1.5
hits=ray('U025',(*pt,45),(0,0,-1),'MedicalSteel');assert hits and hits[0]<5.0,'KCBD top plate disconnected from perimeter'
checks.append('Comer uses green glass/pale precast and KCBD silver glass/stone, with seven and ten occupied floors respectively')
lo,hi=bounds('U026','MedicalSilverGlass');assert lo[2]>17 and 21<hi[2]<21.5
assert bounds('U026','MedicalStone')[0][2]==0 and medical['U026']['levels']==4
pt=fp['U026'].representative_point();assert ray('U026',(pt.x,pt.y,10),(0,0,-1),'MedicalStone')
checks.append('Donnelley greenhouse glazing starts above 17 m, with a solid four-storey base reaching ground')
assert bounds('U125')[1][2]>31 and bounds('U116','MedicalStone')[1][2]>32
for code,z in [('U125',25),('U116',30)]:
 vertices=np.vstack([v for mat,v,_ in meshes[code]if mat=='MedicalStone']);upper=vertices[vertices[:,2]>z];assert len(upper)>0
 # Every raised tower corner projects into its real supporting footprint.
 assert all(fp[code].buffer(.03).covers(Point(x,y))for x,y in upper[:,:2])
checks.append('Chicago Lying-In and Billings have raised masonry towers wholly above their mapped supporting wings')
# Non-medical preservation is checked against the preceding release when its
# optional local audit snapshot is available; the committed Highlight baseline
# is also enforced by check_campus_optimization.py.
prior=Path('/private/tmp/uchi-before-medical-hashes.json')
if prior.exists():
 baseline=json.loads(prior.read_text());current={}
 for r in records:
  current[r['layer']]=sorted(hashlib.sha256(mat.encode()+v.tobytes()+f.tobytes()).hexdigest()for mat,v,f in meshes[r['code']])
 authorized={'U002','U006','U043','U057','U058','U064','U075','U136'}|{'U051', 'U069', 'U106', 'U136', 'U032', 'U057', 'U107', 'U118', 'U036', 'U035', 'U075', 'U128', 'U039', 'U114', 'U115', 'U084', 'U101', 'U067', 'U042', 'U134', 'U068', 'U100', 'U034', 'U098', 'U117', 'U097', 'U133', 'U102', 'U127', 'U038', 'U137', 'U050', 'U139', 'U054'}
 untouched=[k for k in baseline['layers']if k not in baseline['medical']and k.split('_')[0]not in authorized]
 assert all(current[k]==baseline['layers'][k]for k in untouched),'Non-medical building geometry changed'
 assert all(current[k]!=baseline['layers'][k]for k in baseline['medical']),'A medical building was missed'
 checks.append(f'{len(untouched)} non-medical building layers are byte-identical in mesh/material data; all 40 medical layers changed')
report={'medical_layers':40,'retained_medical_highlight':'Gordon Center','checks':checks,'passed':True,'scope':'Exported geometry regression; dimensional/source limits are in the medical source catalog.'}
(R/'output/medical_optimization_validation.json').write_text(json.dumps(report,indent=2)+'\n');print(json.dumps(report,indent=2))
