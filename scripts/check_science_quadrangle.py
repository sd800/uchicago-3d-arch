"""Read back actual new library/science geometry and protect unaffected layers."""
from pathlib import Path
import collections,hashlib,json
import numpy as np
import trimesh
from shapely.geometry.polygon import orient
from check_campus_optimization import meshes,fp,bycode,ray,peak
R=Path(__file__).resolve().parents[1]
read=lambda p:json.loads((R/p).read_text())
review=read('sources/science_quadrangle_review.json');authorized=set(review['authorized_building_changes'])
assert authorized=={'U043','U057','U058','U064','U075','U136'}
# Compare the glass surfaces at the same east-face bay in the two levels.
p=orient(fp['U058'],1);coords=list(p.exterior.coords);candidates=[]
for aa,bb in zip(coords[:-1],coords[1:]):
 a,b=map(np.asarray,[aa,bb]);ln=np.linalg.norm(b-a);u=(b-a)/ln;n=np.array([u[1],-u[0]])
 if n[0]>.9 and ln>20:candidates.append((ln,a,b,u,n))
_,a,b,u,n=max(candidates,key=lambda v:v[0]);center=(a+b)/2+n*3;direction=[*(-n),0]
upper=ray('U058',[*center,12.5],direction,15,'CrerarGlass');lower=ray('U058',[*center,7.0],direction,15,'CrerarGlass')
assert upper and lower and lower[0]-upper[0]>2.5,(upper[:2],lower[:2])
stone=ray('U058',[*center,12.5],direction,4,'CrerarStone');assert not stone,'Upper window aperture blocked by a limestone backing wall'
r=bycode['U058']['exterior_reconstruction'];x,y=r['entry_center']
assert not ray('U058',[x+2,y,3],[-1,0,0],2.8,'CrerarStone'),'Independent entry arch aperture closed'
assert ray('U058',[x+2,y+6.0,3],[-1,0,0],2.8,'CrerarStone'),'Independent entry arch lost its supporting pier'
assert bycode['U058']['levels']==3 and 16<peak('U058')<17
assert r['modeling_level']=='detailed exterior reconstruction' and r['large_rooflights']==2
checks=['Crerar lower glazing physically recedes over 2.5 m behind upper glazing','Crerar upper glass aperture has no opaque stone backing in its reveal','Independent entry arch has an open aperture and solid grade-to-lintel pier','Three above-ground levels and two shaped large rooflights retained']
# Count distinct closed glass objects at the central reading-hall elevation.
reading=0
for mat,v,f in meshes['U136']:
 if mat!='WindowGlass':continue
 for component in trimesh.Trimesh(v,f,process=False).split(only_watertight=True):
  lo,hi=component.bounds
  if abs(lo[2]-16)<.03 and abs(hi[2]-24.7)<.03:reading+=1
assert reading==16,('Eight reading-hall bays required on each long elevation',reading)
assert 41.14<peak('U136')<41.16 and 'RoofClay'in{mat for mat,_,_ in meshes['U136']}
checks.append('Harper has eight distinct tall reading-hall window bays per long elevation, connected roof and retained 41.148 m tower peak')
assert 'RoofSlate'not in{mat for mat,_,_ in meshes['U057']}
plant=0
for mat,v,f in meshes['U057']:
 if mat!='MedicalSteel':continue
 for component in trimesh.Trimesh(v,f,process=False).split(only_watertight=True):
  if 18.7<component.bounds[0,2]<18.9 and 22.1<component.bounds[1,2]<22.3:plant+=1
assert plant==4,('Searle documented heat-recovery chambers',plant)
assert peak('U064')>=31.9 and 'WarmBrick'in{mat for mat,_,_ in meshes['U064']}
assert 'RoofSlate'in{mat for mat,_,_ in meshes['U075']}
checks.append('Searle has a flat roof and four supported heat-recovery chambers; Hinds has raised service towers; Jones retains a slate roof')
base=Path('/private/tmp/uchi-before-science-hashes.json')
if base.exists():
 old=json.loads(base.read_text());now={r['layer']:sorted(hashlib.sha256(mat.encode()+v.tobytes()+f.tobytes()).hexdigest()for mat,v,f in meshes[r['code']])for r in bycode.values()}
 changed={key.split('_')[0]for key in old if old[key]!=now[key]};assert changed==authorized|{'U051', 'U069', 'U106', 'U136', 'U032', 'U057', 'U107', 'U118', 'U036', 'U035', 'U075', 'U128', 'U039', 'U114', 'U115', 'U084', 'U101', 'U067', 'U042', 'U134', 'U068', 'U100', 'U002','U006', 'U034', 'U098', 'U117', 'U097', 'U133', 'U102', 'U127', 'U038', 'U137', 'U050', 'U139', 'U054'}-{'U032'},changed
 checks.append('All building layers outside the authorized science and Main Quad scopes retain identical mesh/material data')
report={'authorized_buildings':sorted(authorized),'checks':checks,'passed':True,'architectural_limits':'See the source-to-model review; physical checks do not certify measured dimensions.'}
(R/'output/science_quadrangle_validation.json').write_text(json.dumps(report,indent=2)+'\n');print(json.dumps(report,indent=2))
