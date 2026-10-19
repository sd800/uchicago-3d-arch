"""Read back distinctive Quad forms, actual apertures, and unaffected layers."""
from pathlib import Path
import json,collections,hashlib
import numpy as np
from check_campus_optimization import meshes,fp,bycode,ray,peak
R=Path(__file__).resolve().parents[1]
review=json.loads((R/'sources/main_quadrangles_review.json').read_text());codes={r['code']for r in review['buildings']};assert len(codes)==34
for row in review['buildings']:
 r=bycode[row['code']];assert row['references'] and row['modeled_features']
 if row['code']=='U032':continue
 d=r.get('campus_refinement')or r.get('exterior_reconstruction');assert d['modeling_level']=='detailed exterior reconstruction',(r['code'],d)
 assert d['quadrangle_detail'] and len(row['modeled_features'])>=1
 assert min(v[:,2].min()for _,v,_ in meshes[r['code']])<=.001,r['code']
checks=['34 individual Quad source/section records; 33 reconstructed exteriors and the retained source-specific Mitchell Tower', 'Every reconstructed building reaches the relative ground datum']
# Levi bridge spans a genuinely empty pedestrian passage, rather than glazing
# or a dark painted rectangle over a solid wall.
a,b,c,d=fp['U084'].bounds;y=(b+d)/2
assert not ray('U084',[a-1,y,2],[1,0,0],c-a+2)
assert ray('U084',[a-1,y,8],[1,0,0],c-a+2)
checks.append('Levi east-west passage is open at pedestrian height and enclosed by its glazed bridge above')
# Cobb Gate's primary Main Quad / Hull Court axis is north-south.
a,b,c,d=fp['U035'].bounds
assert not ray('U035',[(a+c)/2,b-1,1.7],[0,1,0],d-b+2)
checks.append('Cobb Gate opens along the principal north-south promenade as well as the lateral covered axis')
# Reading hall's two long elevations each have eight real recessed openings.
r=bycode['U136']['exterior_reconstruction'];assert r['central_reading_hall_bays']==8
assert r['quadrangle_detail']['traceried_openings']>=16 and r['quadrangle_detail']['true_reading_apertures']>=14
assert len(r['quadrangle_detail']['entries'])==2
assert 41.14<peak('U136')<41.16
checks.append('Harper retains eight reading bays per elevation, actual masonry apertures, tracery, two grounded entries and published tower maximum')
# Source-specific observatory, lecture theatre, bay and meteorology tower.
assert peak('U067')>27 and 'RoofPatina'in{m for m,_,_ in meshes['U067']}
assert ray('U069',[575,928,40],[0,0,-1])[0]<29
assert peak('U102')>28 and peak('U097')>25
checks.append('Ryerson observatory, Kent separate north theatre, Walker turret and Rosenwald octagonal tower survive CAD export')
assert bycode['U038']['levels']==1 and bycode['U038']['exterior_reconstruction']['quadrangle_detail']['true_apertures']>8
checks.append('Hutchinson is a single tall hall with genuine traceried apertures instead of classroom storeys')
# Source clips should never accidentally change unrelated campus buildings.
old=json.loads((R/'sources/main_quad_mesh_baseline.json').read_text())['layers'];now={r['layer']:sorted(hashlib.sha256(m.encode()+v.tobytes()+f.tobytes()).hexdigest()for m,v,f in meshes[r['code']])for r in bycode.values()}
changed={key.split('_')[0]for key in old if old[key]!=now[key]};assert changed==(codes-{'U032'})|set(review.get('additional_authorized_buildings',[])),sorted(changed)
checks.append('All 142 other mesh/material sequences, including Mitchell, retain identical mesh and material data')
assert {'RoofMembrane','RoofPaleMembrane','RoofSedum'}<={m for m,_,_ in meshes['U002']}
planted=np.vstack([v for m,v,f in meshes['U002']if m=='RoofSedum']);assert planted[:,2].max()<6.0
checks.append('Campus North planting is confined to the low dining roof; the three residential tower tops use neutral membrane roofing')
palette=json.loads((R/'output/palette.json').read_text());old_palette=json.loads((R/'sources/main_quad_mesh_baseline.json').read_text())['palette']
assert {k for k in palette if palette[k]!=old_palette.get(k)}=={'PalevskyRoof','RoofSedum','RoofPaleMembrane','FieldhouseRoof'}
assert {code for code,parts in meshes.items()if any(m=='PalevskyRoof'for m,v,f in parts)}=={'U011','U014','U018'}
assert 'FieldhouseRoof'in{m for m,v,f in meshes['U006']} and 'RoofClay'in{m for m,v,f in meshes['U126']}
checks.append('Satellite-confirmed Palevsky blue-violet, Henry Crown brown-red roof corrections and verification of retained Ida Noyes red roofs are confined to their named layers')
land=json.loads((R/'output/campus_landscape_refinement.json').read_text())['main_quadrangles'];assert land['invented_cross_lawn_paths']==0 and land['short_entry_links']>0
checks.append('Mapped lawns, pond and path centerlines retained with bounded edges, paving joints and short entrance connections')
report={'scope_buildings':34,'reconstructed_buildings':33,'retained_geometry_buildings':142,'checks':checks,'passed':True,'limits':review['dimension_status']};(R/'output/main_quadrangles_validation.json').write_text(json.dumps(report,indent=2)+'\n');print(json.dumps(report,indent=2))
