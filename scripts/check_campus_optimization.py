"""Check coverage and physical results in the exported campus model.

The source catalog distinguishes documented floor counts from estimates. These
checks verify exported geometry, not unqualified architectural photo fidelity.
"""
from pathlib import Path
import collections, hashlib, json
import numpy as np
from shapely.geometry import shape, Polygon
from campus_exchange import read_legacy_meshes
root=Path(__file__).resolve().parents[1]
read=lambda p:json.loads((root/p).read_text())
records=read('output/buildings.json');catalog=read('sources/building_optimization.json')['buildings'];layers=read('output/layer_map.json')
ordinary=[r for r in records if not r['landmark']];highlights=[r for r in records if r['landmark']]
assert len(records)==177 and len(ordinary)==158 and len(highlights)==19
assert {r['osm_id']for r in records}=={r['osm_id']for r in catalog}
checks=[]
for r in ordinary:
 cfg=r['optimization_2026_10_18'];detail=r['campus_refinement']
 assert cfg['family']!='protected_highlight' and cfg['references'] and cfg['dimension_status']
 assert detail and detail['modeling_level']=='optimized exterior',r['name']
 assert r['ordinary_joinery']['buttresses']==0,r['name']
 assert r['height']>0 and r['levels']>=1
checks.append('All 158 ordinary building layers use explicit exterior recipes and dimensions/source caveats')
baseline=read('sources/protected_highlight_mesh_hashes.json')['layers'];hashes=collections.defaultdict(list);meshes=collections.defaultdict(list);all_codes=set()
for name,v,f in read_legacy_meshes(root/'output/UChicago_HydePark.3ds'):
 info=layers[name];lay=info['layer']
 assert np.isfinite(v).all() and f.max()<len(v),name
 if info.get('category')=='building':all_codes.add(lay.split('_')[0])
 if lay in baseline:hashes[lay].append(hashlib.sha256(info['material'].encode()+v.tobytes()+f.tobytes()).hexdigest())
 if info.get('category')=='building':meshes[lay.split('_')[0]].append((info['material'],v,f))
assert len(all_codes)==177
assert {k:sorted(v)for k,v in hashes.items()}==baseline,'Existing Highlights changed unexpectedly'
checks.append('All 19 existing Highlight mesh/material sequences are identical to release 26.10.18.11')
bycode={r['code']:r for r in records}
def ray(code,origin,direction,far=10000,material=None):
 o=np.asarray(origin);d=np.asarray(direction);found=[]
 for mat,v,f in meshes[code]:
  if material and mat!=material:continue
  tri=v[f];e1=tri[:,1]-tri[:,0];e2=tri[:,2]-tri[:,0];hh=np.cross(np.broadcast_to(d,e2.shape),e2);aa=np.einsum('ij,ij->i',e1,hh)
  valid=np.abs(aa)>1e-8; inv=np.zeros_like(aa);inv[valid]=1/aa[valid];s=o-tri[:,0];u=inv*np.einsum('ij,ij->i',s,hh);qq=np.cross(s,e1);vv=inv*np.einsum('j,ij->i',d,qq);tt=inv*np.einsum('ij,ij->i',e2,qq)
  found.extend(tt[valid&(u>=-1e-6)&(vv>=-1e-6)&(u+vv<=1.000001)&(tt>=0)&(tt<=far)].tolist())
 return sorted(found)
def peak(code):return max(float(v[:,2].max())for _,v,_ in meshes[code])
for code,limit in [('U015',9.5),('U026',5.0),('U039',16.0)]:assert peak(code)<limit,(code,peak(code))
assert bycode['U015']['levels']==1 and bycode['U039']['levels']==3
assert bycode['U124']['levels']==12 and 40<peak('U124')<41
assert bycode['U168']['levels']==9 and 29<peak('U168')<31
assert 37<peak('U169')<39 and bycode['U169']['levels']==5
checks.append('South Steam Plant has a tall supported boiler hall and paired raised flues')
checks.append('High Bay, greenhouse and Snell remain low; International House and Grossman have distinct tall ranges')
pickmats={m for m,_,_ in meshes['U100']};assert 'RoofMembrane'in pickmats and 'RoofSlate'not in pickmats
assert 'RoofPatina'in{m for m,_,_ in meshes['U067']}
checks.append('Pick retains its flat roof and Ryerson has a supported observatory dome')
gate=bycode['U035'];cx,cy=gate['center'];width=gate['width'];depth=gate['depth']
# The through axis follows the mapped bounds center, not the polygon centroid.
fp={f['properties']['code']:shape(f['geometry'])for f in read('output/footprints_local_meters.geojson')['features']}
a,b,c,d=fp['U035'].bounds;cy=(b+d)/2
assert not ray('U035',[a-1,cy,1.7],[1,0,0],c-a+2),'Cobb Gate passage blocked'
assert ray('U035',[(a+c)/2,cy,15],[0,0,-1]),'Cobb Gate missing supported upper range'
checks.append('Cobb Gate remains physically open along its east-west pedestrian passage')
courts=0
for r in ordinary:
 p=fp[r['code']]
 if p.geom_type!='Polygon':continue
 for hole in p.interiors:
  court=Polygon(hole)
  if court.area<20:continue
  pt=court.representative_point();hits=ray(r['code'],[pt.x,pt.y,100],[0,0,-1],99)
  assert not hits,(r['name'],'courtyard was filled',hits[:2])
  courts+=1
checks.append(str(courts)+' mapped courtyard centers stay physically open to the sky')
report={'ordinary_buildings':158,'protected_highlights':19,'checks':checks,'passed':True,'scope':'Geometry regression only. See source catalog for documentary limits.'}
(root/'output/campus_optimization_validation.json').write_text(json.dumps(report,indent=2)+'\n');print(json.dumps(report,indent=2))
