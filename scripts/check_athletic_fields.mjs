/** Probe exported athletic surfaces, dimensions and connectivity, not report counts alone. */
import assert from 'node:assert/strict';
import {readFileSync,writeFileSync} from 'node:fs';
import {BufferGeometry,BufferAttribute,Mesh,MeshBasicMaterial,DoubleSide,Raycaster,Vector3} from 'three';
import {decodeGLB} from './glb_model.js';
import {SURFACE_ORDER} from './surface_rendering.js';
const root=new URL('../',import.meta.url),read=p=>readFileSync(new URL(p,root));
const {doc,accessor}=await decodeGLB(read('output/UChicago_HydePark.glb'));
const groups=new Map, names=new Set(['FieldTurf','FieldStripe','Track','Court','CourtApron','Infield','Marking','GoalPost','Furniture']);
for(const node of doc.nodes){
 if(node.mesh===undefined||node.extras?.category!=='environment')continue;
 const p=doc.meshes[node.mesh].primitives[0],name=doc.materials[p.material].name;
 if(!names.has(name))continue;
 const g=new BufferGeometry();g.setAttribute('position',new BufferAttribute(accessor(p.attributes.POSITION).array,3));g.setIndex(new BufferAttribute(accessor(p.indices).array,1));
 const mesh=new Mesh(g,new MeshBasicMaterial({name,side:DoubleSide}));mesh.updateMatrixWorld(true);
 if(!groups.has(name))groups.set(name,[]);groups.get(name).push(mesh);
}
const hits=(mat,x,y,z=20,direction=[0,0,-1],far=30)=>new Raycaster(new Vector3(x,y,z),new Vector3(...direction),0,far).intersectObjects(groups.get(mat)||[],false);
const checks=[];function check(ok,label){assert.ok(ok,label);checks.push(label);}
const norm=Math.hypot(1,.0105),east=[1/norm,.0105/norm],north=[-east[1],east[0]],at=(x,y)=>[189.55+east[0]*x+north[0]*y,1336.60+east[1]*x+north[1]*y];
for(let i=0;i<=8;i++){
 const [x,y]=at(39.55+i*1.22,9);
 check(hits('Marking',x,y).length>0,`Track lane boundary ${i} is present on the exported east straight`);
 if(i<8){const [a,b]=at(39.55+(i+.5)*1.22,9);check(hits('Track',a,b).length>0&&!hits('Marking',a,b).length,`Lane ${i+1} retains a clear continuous running surface`);}
}
check(hits('Court',97.25,1398.8).length>0,'Northwest regulation court retains its playable surface');
check(hits('Marking',93.25,1405.2).length>0,'Tennis service box line is exported');
check(hits('Court',113,1260.6).length>0,'Southern practice half court is retained');
check(hits('Infield',279.6,1390).length>0,'Northwest baseball clay arc is present');
check(hits('Infield',355,1280).length>0,'Southeast softball clay infield is present');
check(hits('FieldTurf',189,1338).length>0,'Football pitch has its source-specific artificial turf');
check((groups.get('FieldStripe')||[]).length>0,'Alternating turf strips have exported geometry');
for(const [x,y]of [[188.51,1392.98],[189.68,1281.25]]){const contact=hits('GoalPost',x,y);check(contact.length>0&&contact[0].point.z>3.2,'Goalpost crossbar meets its center support at '+y);}
for(const name of ['FieldTurf','FieldStripe','CourtApron','Infield'])check(name in SURFACE_ORDER,`${name} participates in stable ground-surface compositing`);
const r=JSON.parse(read('output/athletic_fields_refinement.json'));
check(r.regulation_tennis_courts===8&&r.practice_half_courts===2,'University court count is retained');
check(Math.abs(r.lane_one_length_m-400)<.1,'Lane-one measurement is approximately 400 m');
check(r.added_triangles<30000,'Outdoor refinement stays below its 30,000-triangle budget');
const result={passed:true,physical_checks:checks.length,checks,added_triangles:r.added_triangles};
writeFileSync(new URL('output/athletic_fields_validation.json',root),JSON.stringify(result,null,2)+'\n');console.log(JSON.stringify(result));
