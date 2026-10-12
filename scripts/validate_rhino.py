"""Read back the Rhino deliverable and check layers, solids and finite geometry."""
import pathlib,json,collections,math
import rhino3dm as rh
root=pathlib.Path(__file__).resolve().parents[1]
m=rh.File3dm.Read(str(root/'output/UChicago_HydePark_Layered.3dm'))
assert m is not None and m.Settings.ModelUnitSystem==rh.UnitSystem.Meters
assert len(m.Layers)==178
counts=collections.Counter(o.Attributes.LayerIndex for o in m.Objects)
assert set(counts)==set(range(len(m.Layers)))
solids=meshes=curves=0
for o in m.Objects:
 g=o.Geometry
 assert g.IsValid,o.Attributes.Name
 if isinstance(g,rh.Extrusion):
  assert g.IsSolid,o.Attributes.Name
  solids+=1
 elif isinstance(g,rh.Mesh):
  assert g.IsClosed,o.Attributes.Name
  for v in g.Vertices:assert all(math.isfinite(x) for x in [v.X,v.Y,v.Z])
  meshes+=1
 elif isinstance(g,rh.Curve):curves+=1
info={'format':'Rhino 3DM v7','units':'meters','layers':len(m.Layers),'nonempty_layers':len(counts),'objects':len(m.Objects),'closed_native_solids':solids,'closed_mesh_objects':meshes,'plan_curves':curves,'all_geometry_valid':True,'named_views':[v.Name for v in m.NamedViews]}
(root/'output/rhino_validation.json').write_text(json.dumps(info,ensure_ascii=False,indent=2))
print(json.dumps(info,ensure_ascii=False,indent=2))
