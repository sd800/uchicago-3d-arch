import * as THREE from 'three';
import {OrbitControls} from 'three/addons/controls/OrbitControls.js';
import {TDSLoader} from 'three/addons/loaders/TDSLoader.js';
import {initialLanguage} from './locale.js';

const data=JSON.parse(document.getElementById('campus-data').textContent);
const $=id=>document.getElementById(id), records=data.records;
const en=Object.fromEntries([...document.querySelectorAll('[data-i18n]')].map(el=>[el.dataset.i18n,el.textContent]));
Object.assign(en,{layers:'Building layers',mobileLayers:'Buildings',search:'Search building or ID',empty:'No matching buildings',exploreTitle:'Explore the campus',exploreSub:'Choose a building to see dimensions, geometry notes and sources.',intro:'Individual building layers, a separate landscape layer, and 19 architectural highlights. The model combines mapped footprints with published and estimated heights.',published:'Published height',planning:'Planning drawing',estimated:'Estimated height',highest:'Model peak',area:'Mapped footprint',width:'East–west extent',depth:'North–south extent',focus:'Locate',isolate:'Isolate',clear:'Deselect',sourceHeight:'Height source',sourceMap:'Footprint source',precision:'Public map extents are approximate. Roof and facade details are simplified; no survey accuracy is claimed.',basisLabel:'Height basis: ',error:'Interactive rendering is unavailable. A static preview is shown. Use a WebGL 2 browser with graphics acceleration enabled. Dimensions and the 3DS download are still available.',static:'Static preview · WebGL unavailable',lost:'Graphics context interrupted. Reopen the HTML to restore the model.',hide:'Hide ',show:'Show ',status:'visible · meters · public-source exterior model',languageLabel:'Switch to Chinese',prevLabel:'Previous landmark',nextLabel:'Next landmark',cutLabel:'Height of horizontal slice',modelLabel:'Interactive University of Chicago campus model',searchLabel:'Search buildings',sidebarLabel:'Building layers and dimensions',tourLabel:'Choose a landmark',snapshotTitle:'UChicago Campus in 3D'});
const zh={title:'芝加哥大学 · 三维校园',subtitle:'海德公园校区模型',offline:'离线可用',download:'下载 3DS',save:'保存视图',eyebrow:'HYDE PARK · 校园空间图集',closeSidebar:'收起',visible:'显示建筑',unit:'模型单位',environment:'环境景观',details:'建筑外部细节',labels:'地标名称',shadows:'日照阴影',layers:'建筑图层',mobileLayers:'建筑',showAll:'全部显示',all:'全部',landmarks:'标志建筑',quads:'主四合院',north:'北校区',south:'南校区',east:'东校区',medical:'医学区',aerial:'全校鸟瞰',core:'主四合院',plan:'总平面',reset:'重置',help:'操作与来源',tourTitle:'建筑漫游 · 校园地标',explore:'查看',cut:'高度截面',stone:'石灰石',glass:'玻璃',roads:'道路',plazas:'广场',green:'绿地',loading:'正在打开校园模型…',mouseHelp:'拖动旋转 · 滚轮缩放 · 右键平移',helpHeading:'在三维空间中探索校园',helpOrbit:'鼠标左键拖动旋转，滚轮缩放，右键拖动平移。触屏设备使用单指旋转，双指缩放或平移。',helpSelect:'点击模型或列表中的建筑，查看尺寸、形态说明和资料来源。可以逐栋隐藏，也可以单独查看。',helpTour:'通过建筑漫游查看地标，切换外部细节，或用高度截面对比体块。截面仅裁切外部表面，不表示内部楼层或室内结构。',helpOffline:'模型、三维引擎和预览均内嵌在 HTML 中。无需网络或服务器，直接用浏览器打开即可。交互显示需要 WebGL 2。',helpAccuracy:'1 单位 = 1 米。平面采用带地理坐标的公开地图，部分地标高度来自学校或项目公开资料；其他高度、屋顶、立面开窗、树位和道路宽度为近似。地面按相对 Z=0 平整化。这是独立制作的室外空间研究模型，不是学校官方 BIM 或实测模型。',helpLanguages:'设备语言偏好中有中文时首次打开默认中文，其余设备默认英文。浏览器存储可用时会记住手动选择。中文建筑名为便于识别的译名。',sources:'资料来源',officialMap:'学校官方地图',architecture:'学校建筑介绍',cityData:'芝加哥市建筑数据',snapshot:'公开资料快照 · 2026年10月12日',close:'关闭',search:'搜索建筑名称或编号',empty:'没有匹配的建筑',exploreTitle:'探索校园空间',exploreSub:'选择建筑，查看尺寸、形态说明与来源。',intro:'建筑逐栋分层，室外环境单独一层，含19处建筑地标。模型结合公开地图轮廓、已发表高度及明确标注的估算尺寸。',published:'公开资料高度',planning:'规划图尺寸',estimated:'高度估算',highest:'模型最高点',area:'地图平面占地',width:'东西向范围',depth:'南北向范围',focus:'定位建筑',isolate:'单独查看',clear:'取消选择',sourceHeight:'高度来源',sourceMap:'平面来源',precision:'平面为公开地图近似轮廓，屋顶与立面细节简化，未取得实测精度证明。',basisLabel:'高度依据：',error:'当前浏览器无法启动交互显示，已显示静态预览。请使用支持 WebGL 2 的浏览器并启用图形加速。尺寸查询与 3DS 下载仍可使用。',static:'静态预览 · WebGL 未启用',lost:'三维显示暂时中断，重新打开 HTML 可恢复模型。',hide:'隐藏',show:'显示',status:'栋显示 · 米制 · 公开资料室外模型',languageLabel:'Switch to English',prevLabel:'上一个地标',nextLabel:'下一个地标',cutLabel:'水平截面高度',modelLabel:'可旋转与缩放的芝加哥大学校园模型',searchLabel:'搜索建筑',sidebarLabel:'建筑图层与尺寸信息',tourLabel:'选择校园地标',snapshotTitle:'芝加哥大学 · 海德公园三维校园'};
let stored=null;try{stored=localStorage.getItem('uchicago-model-language');}catch{}
let lang=initialLanguage(navigator.languages?.length?navigator.languages:[navigator.language||'en'],stored);
const t=key=>(lang==='zh'?zh[key]:en[key])||en[key]||key;
const nameOf=r=>lang==='zh'?(r.name_zh||r.name):r.name;
const brief=r=>lang==='zh'?(r.short_zh||r.name_zh||r.name):(r.short||r.name);
const byLayer=new Map(records.map(r=>[r.layer,r]));const byCode=new Map(records.map(r=>[r.code,r]));
const buildings=new Map(), envMeshes=[], pickMeshes=[], details=[];
let selected=null,category='all',renderer=null,scene,camera,controls,campus,sun,frameHeight=1500,viewMode='aerial',staticMode=false;
const sidebar=$('sidebar'),host=$('viewport'),compact=matchMedia('(max-width:760px)');
const tourIds=[150457349,156128082,1228219576,157655069,159093828,194224828,125667497,152422729,441025431,10657061,11687839,152586235,387213841,143926554,143926548,152422458,152284260,143457513,142870150];
const tour=tourIds.map(id=>records.find(r=>r.osm_id===id)).filter(Boolean);let tourIndex=0;
const labelNodes=new Map();
for(const r of records.filter(r=>r.landmark)){const el=document.createElement('div');el.className='map-label';$('map-labels').append(el);labelNodes.set(r.code,el);}
function syncSidebar(){sidebar.classList.toggle('closed',compact.matches);$('toggle-sidebar').setAttribute('aria-expanded',String(!sidebar.classList.contains('closed')));}
syncSidebar();compact.addEventListener('change',syncSidebar);
$('toggle-sidebar').onclick=()=>{sidebar.classList.toggle('closed');$('toggle-sidebar').setAttribute('aria-expanded',String(!sidebar.classList.contains('closed')));};
$('close-sidebar').onclick=()=>{sidebar.classList.add('closed');$('toggle-sidebar').setAttribute('aria-expanded','false');};
$('open-help').onclick=()=>$('help-dialog').showModal();$('close-help').onclick=()=>$('help-dialog').close();
$('help-dialog').addEventListener('click',e=>{if(e.target===e.currentTarget){const b=e.target.getBoundingClientRect();if(e.clientX<b.left||e.clientX>b.right||e.clientY<b.top||e.clientY>b.bottom)e.target.close();}});
function download(blob,name){const url=URL.createObjectURL(blob),a=document.createElement('a');a.href=url;a.download=name;a.click();setTimeout(()=>URL.revokeObjectURL(url),1000);}
const bytes=Uint8Array.from(atob(data.model),c=>c.charCodeAt(0));
$('download-3ds').onclick=()=>download(new Blob([bytes],{type:'application/octet-stream'}),'UChicago_HydePark.3ds');
$('download-image').onclick=()=>{if(!renderer)return;render();renderer.domElement.toBlob(b=>{if(b)download(b,'UChicago_HydePark_view.png');});};
function listRecords(){const q=$('search').value.trim().toLowerCase();return records.filter(r=>(category==='all'||(category==='landmark'?r.landmark:r.zone===category))&&(!q||[r.name,r.name_zh,r.code,r.short,r.short_zh].some(s=>s?.toLowerCase().includes(q))));}
function refreshList(){
 const list=$('building-list');list.replaceChildren();const shown=listRecords();
 if(!shown.length){const el=document.createElement('p');el.className='empty';el.textContent=t('empty');list.append(el);}
 for(const r of shown){
  const row=document.createElement('div');row.className='row'+(selected===r.code?' selected':'');row.dataset.code=r.code;
  const cb=document.createElement('input');cb.type='checkbox';cb.checked=buildings.get(r.code)?.visible??true;cb.setAttribute('aria-label',t('show')+nameOf(r));cb.onchange=()=>setVisible(r.code,cb.checked);
  const btn=document.createElement('button');btn.className='building-button';btn.title=r.name;
  const nm=document.createElement('span');nm.className='building-name';nm.textContent=nameOf(r);
  const meta=document.createElement('span');meta.className='building-meta';meta.textContent=r.code+' · '+t(r.zone)+(r.landmark?'  ◆':'');
  btn.append(nm,meta);btn.onclick=()=>selectBuilding(r.code,true);row.append(cb,btn);list.append(row);
 }
 updateCount();
}
function updateCount(){const n=buildings.size?[...buildings.values()].filter(g=>g.visible).length:records.length;$('visible-count').innerHTML=n+'<small>/ '+records.length+'</small>';if(staticMode)$('status-text').textContent=t('static');else $('status-text').textContent=n+' / '+records.length+' '+t('status');}
function setVisible(code,value){const g=buildings.get(code);if(g)g.visible=value;if(!value&&code===selected)selectBuilding(null);updateCount();render();}
$('search').oninput=refreshList;
for(const b of document.querySelectorAll('[data-category]'))b.onclick=()=>{category=b.dataset.category;for(const bb of document.querySelectorAll('[data-category]')){bb.classList.toggle('active',bb===b);bb.setAttribute('aria-pressed',String(bb===b));}refreshList();};
$('show-all').onclick=()=>{for(const g of buildings.values())g.visible=true;$('environment').checked=true;envMeshes.forEach(m=>m.visible=true);refreshList();render();};
$('environment').onchange=()=>{envMeshes.forEach(m=>m.visible=$('environment').checked);render();};
$('details').onchange=()=>{details.forEach(m=>m.visible=$('details').checked);render();};
$('labels').onchange=render;
$('shadows').onchange=()=>{if(renderer){renderer.shadowMap.enabled=$('shadows').checked;sun.castShadow=$('shadows').checked;scene.traverse(o=>{if(o.isMesh)(Array.isArray(o.material)?o.material:[o.material]).forEach(m=>m.needsUpdate=true);});render();}};
const clipPlane=new THREE.Plane(new THREE.Vector3(0,0,-1),65);
function updateCut(){const on=$('cut-enabled').checked,h=Number($('cut-height').value);$('cut-height').disabled=!on;$('cut-value').textContent=h+' m';clipPlane.constant=h;if(renderer){renderer.clippingPlanes=on?[clipPlane]:[];render();}}
$('cut-enabled').onchange=updateCut;$('cut-height').oninput=updateCut;
function emptyDetail(){const p=$('detail');p.replaceChildren();for(const [key,cls] of [['exploreTitle','detail-title'],['exploreSub','detail-sub'],['intro','detail-note']]){const el=document.createElement('div');el.className=cls;el.textContent=t(key);p.append(el);}}
function refreshDetail(){
 if(!selected){emptyDetail();return;}const r=byCode.get(selected),p=$('detail');p.replaceChildren();
 const title=document.createElement('div');title.className='detail-title';title.textContent=nameOf(r);
 const sub=document.createElement('div');sub.className='detail-sub';const badge=document.createElement('span');badge.className='badge '+r.height_status;badge.textContent=t(r.height_status);sub.append(badge,document.createTextNode(r.code+' · '+t(r.zone)));
 const dl=document.createElement('dl');dl.className='dimensions';
 for(const [key,value] of [['highest',r.height.toFixed(2)+' m'],['area',Math.round(r.area).toLocaleString(lang==='zh'?'zh-CN':'en-US')+' m²'],['width',r.width.toFixed(1)+' m'],['depth',r.depth.toFixed(1)+' m']]){const cell=document.createElement('div'),dt=document.createElement('dt'),dd=document.createElement('dd');dt.textContent=t(key);dd.textContent=value;cell.append(dt,dd);dl.append(cell);}
 const actions=document.createElement('div');actions.className='detail-actions';
 for(const [key,fn] of [['focus',()=>focusBuilding(r.code)],['isolate',()=>{for(const[c,g]of buildings)g.visible=c===r.code;refreshList();focusBuilding(r.code);}],['clear',()=>selectBuilding(null)]]){const b=document.createElement('button');b.textContent=t(key);b.onclick=fn;actions.append(b);}
 const note=document.createElement('p');note.className='detail-note';note.textContent=lang==='zh'?r.partition:r.partition_en;
 const basis=document.createElement('p');basis.className='detail-note';basis.textContent=t('basisLabel')+(lang==='zh'?r.basis:r.basis_en);
 const prec=document.createElement('p');prec.className='detail-note';prec.textContent=t('precision');
 const links=document.createElement('p');links.className='detail-note';
 for(const[key,url]of [['sourceHeight',r.source],['sourceMap',r.footprint_source]]){const a=document.createElement('a');a.href=url;a.target='_blank';a.rel='noopener';a.textContent=t(key);links.append(a,document.createTextNode(' · '));}
 p.append(title,sub,dl,actions,note,basis,prec,links);
}
function selectBuilding(code,focus=false){
 selected=code;for(const[c,g]of buildings)g.traverse(m=>{if(m.isMesh)(Array.isArray(m.material)?m.material:[m.material]).forEach(mat=>{mat.emissive.set(c===code?0x682919:0);mat.emissiveIntensity=c===code?.22:0;});});
 if(code){const g=buildings.get(code);if(g)g.visible=true;const idx=tour.findIndex(r=>r.code===code);if(idx>=0){tourIndex=idx;refreshTour();}}
 refreshDetail();refreshList();if(focus)focusBuilding(code);render();
}
function refreshTour(){const s=$('tour-select');s.replaceChildren();for(const r of tour){const op=document.createElement('option');op.value=r.code;op.textContent=brief(r);s.append(op);}s.value=tour[tourIndex]?.code||'';$('tour-step').textContent=(tourIndex+1)+' / '+tour.length;}
function stepTour(delta){tourIndex=(tourIndex+delta+tour.length)%tour.length;refreshTour();selectBuilding(tour[tourIndex].code,true);}
$('tour-prev').onclick=()=>stepTour(-1);$('tour-next').onclick=()=>stepTour(1);$('tour-go').onclick=()=>selectBuilding(tour[tourIndex].code,true);$('tour-select').onchange=e=>{tourIndex=tour.findIndex(r=>r.code===e.target.value);refreshTour();selectBuilding(tour[tourIndex].code,true);};
function applyLanguage(){
 document.documentElement.lang=lang==='zh'?'zh-CN':'en';document.title=t('snapshotTitle');
 for(const el of document.querySelectorAll('[data-i18n]'))el.textContent=t(el.dataset.i18n);
 $('language').textContent=lang==='zh'?'English':'中文';$('language').setAttribute('aria-label',t('languageLabel'));
 $('search').placeholder=t('search');$('search').setAttribute('aria-label',t('searchLabel'));sidebar.setAttribute('aria-label',t('sidebarLabel'));
 $('tour-select').setAttribute('aria-label',t('tourLabel'));$('tour-prev').setAttribute('aria-label',t('prevLabel'));$('tour-next').setAttribute('aria-label',t('nextLabel'));$('cut-height').setAttribute('aria-label',t('cutLabel'));
 if(renderer)renderer.domElement.setAttribute('aria-label',t('modelLabel'));
 for(const[r,el]of labelNodes)el.textContent=brief(byCode.get(r));
 const err=$('render-error');if(err)err.textContent=t('error');refreshTour();refreshList();refreshDetail();render();
}
$('language').onclick=()=>{lang=lang==='en'?'zh':'en';try{localStorage.setItem('uchicago-model-language',lang);}catch{}applyLanguage();};
function aspect(){return host.clientWidth/Math.max(host.clientHeight,1);}
function updateFrustum(){if(!camera)return;const a=aspect();camera.left=-frameHeight*a/2;camera.right=frameHeight*a/2;camera.top=frameHeight/2;camera.bottom=-frameHeight/2;camera.updateProjectionMatrix();}
function fitBox(b,mode='aerial',pad=1.16){
 if(!camera)return;const center=b.getCenter(new THREE.Vector3());const back=mode==='plan'?new THREE.Vector3(0,-.00001,1):new THREE.Vector3(1.15,-.95,1.2).normalize();
 camera.position.copy(center).addScaledVector(back,3000);camera.up.set(0,0,1);camera.lookAt(center);camera.updateMatrixWorld(true);controls.target.copy(center);camera.zoom=1;
 const right=new THREE.Vector3().setFromMatrixColumn(camera.matrix,0),up=new THREE.Vector3().setFromMatrixColumn(camera.matrix,1);let xmin=Infinity,xmax=-Infinity,ymin=Infinity,ymax=-Infinity;
 for(const x of [b.min.x,b.max.x])for(const y of [b.min.y,b.max.y])for(const z of [b.min.z,b.max.z]){const p=new THREE.Vector3(x,y,z).sub(center),xx=p.dot(right),yy=p.dot(up);xmin=Math.min(xmin,xx);xmax=Math.max(xmax,xx);ymin=Math.min(ymin,yy);ymax=Math.max(ymax,yy);}
 frameHeight=Math.max((ymax-ymin)*pad,(xmax-xmin)/aspect()*pad,50);updateFrustum();controls.update();render();
}
function setViewButtons(){for(const key of ['aerial','core','plan']){$(key).classList.toggle('active',viewMode===key);$(key).setAttribute('aria-pressed',String(viewMode===key));}}
function fullView(mode){viewMode=mode;setViewButtons();if(!campus)return;const b=mode==='core'?new THREE.Box3(new THREE.Vector3(475,630,0),new THREE.Vector3(890,1160,65)):new THREE.Box3().setFromObject(campus);fitBox(b,mode==='plan'?'plan':'aerial');}
function focusBuilding(code){const g=buildings.get(code);if(!g||!camera)return;g.visible=true;g.updateWorldMatrix(true,true);viewMode='focus';setViewButtons();fitBox(new THREE.Box3().setFromObject(g),'aerial',1.55);}
$('aerial').onclick=()=>fullView('aerial');$('plan').onclick=()=>fullView('plan');$('core').onclick=()=>fullView('core');$('reset-view').onclick=()=>{selectBuilding(null);$('cut-enabled').checked=false;updateCut();fullView('aerial');};
function updateLabels(){
 if(!camera)return;const boxes=[];const picked=[...labelNodes].sort(([aa],[bb])=>(aa===selected?-1:bb===selected?1:0));
 for(const[code,el]of picked){const r=byCode.get(code),g=buildings.get(code);el.style.display='none';if(!$('labels').checked||!g?.visible)continue;
  if($('cut-enabled').checked&&r.height>Number($('cut-height').value))continue;
  const p=new THREE.Vector3(r.center[0],r.center[1],r.height+3).project(camera);if(Math.abs(p.x)>.92||Math.abs(p.y)>.9||Math.abs(p.z)>1)continue;
  const xx=(p.x+1)/2*host.clientWidth,yy=(1-p.y)/2*host.clientHeight;
  if(yy<65||yy>host.clientHeight-150||(xx>host.clientWidth-255&&yy<210))continue;
  const ww=el.textContent.length*(lang==='zh'?8:5)+18,hh=23;const b=[xx-ww/2,yy-hh,xx+ww/2,yy];
  if(code!==selected&&boxes.some(a=>!(a[2]+12<b[0]||b[2]+12<a[0]||a[3]+10<b[1]||b[3]+10<a[1])))continue;
  if(code!==selected&&boxes.length>9)continue;boxes.push(b);el.style.left=xx+'px';el.style.top=yy+'px';el.style.display='block';el.classList.toggle('selected',code===selected);
 }
}
function render(){
 if(!renderer)return;renderer.render(scene,camera);const n=new THREE.Vector3(0,1,0).transformDirection(camera.matrixWorldInverse);$('north-arrow').style.transform='rotate('+Math.atan2(n.x,n.y)+'rad)';
 const mpp=(camera.right-camera.left)/camera.zoom/Math.max(host.clientWidth,1),raw=mpp*80,pow=10**Math.floor(Math.log10(raw));const length=[1,2,5,10].map(x=>x*pow).find(x=>x>=raw)||10*pow;
 $('scale-line').style.width=(length/mpp)+'px';$('scale-text').textContent=length<1?Math.round(length*100)+' cm':length+' m';updateLabels();
}
applyLanguage();
try{
 THREE.Object3D.DEFAULT_UP.set(0,0,1);renderer=new THREE.WebGLRenderer({antialias:true,preserveDrawingBuffer:true});renderer.setPixelRatio(Math.min(devicePixelRatio||1,1.5));renderer.setClearColor(0xe9ece3);renderer.outputColorSpace=THREE.SRGBColorSpace;renderer.toneMapping=THREE.NoToneMapping;renderer.shadowMap.enabled=true;renderer.shadowMap.type=THREE.PCFShadowMap;
 renderer.domElement.setAttribute('aria-label',t('modelLabel'));renderer.domElement.tabIndex=0;$('canvas-host').append(renderer.domElement);
 scene=new THREE.Scene();camera=new THREE.OrthographicCamera(-1000,1000,1000,-1000,.1,10000);camera.up.set(0,0,1);scene.add(new THREE.HemisphereLight(0xffffff,0x849177,2.0));
 sun=new THREE.DirectionalLight(0xffffff,2.2);sun.position.set(-400,-700,1600);sun.target.position.set(750,800,0);sun.castShadow=true;sun.shadow.mapSize.set(2048,2048);sun.shadow.camera.left=-1400;sun.shadow.camera.right=1400;sun.shadow.camera.top=1400;sun.shadow.camera.bottom=-1400;sun.shadow.camera.near=1;sun.shadow.camera.far=4500;sun.shadow.bias=-.00015;sun.shadow.normalBias=.35;scene.add(sun,sun.target);
 campus=new TDSLoader().parse(bytes.buffer,'');const meshes=[];campus.traverse(o=>{if(o.isMesh)meshes.push(o);});
 for(const m of meshes){
  const old=Array.isArray(m.material)?m.material:[m.material];const materials=old.map(mm=>{const mat=mm.clone();const co=data.palette[mat.name];if(co)mat.color.setRGB(co[0]/255,co[1]/255,co[2]/255,THREE.SRGBColorSpace);mat.shininess=mat.name==='Glass'?25:0;mat.specular.set(mat.name==='Glass'?0x222222:0);mat.flatShading=true;mat.emissiveIntensity=0;if(mat.name==='Glass'&&m.name.startsWith(records.find(r=>r.osm_id===159093828)?.code+'D')){mat.transparent=true;mat.opacity=.73;mat.depthWrite=false;}return mat;});
  m.material=Array.isArray(m.material)?materials:materials[0];m.receiveShadow=true;
  const r=byLayer.get(data.layers[m.name]?.layer);
  if(r){let g=buildings.get(r.code);if(!g){g=new THREE.Group();g.name=r.code;buildings.set(r.code,g);campus.add(g);}g.attach(m);m.castShadow=true;m.userData.code=r.code;pickMeshes.push(m);if(m.name.includes('D'))details.push(m);}
  else{envMeshes.push(m);m.castShadow=materials.some(mat=>['Leaves','Trunk','Furniture'].includes(mat.name));}
 }
 scene.add(campus);controls=new OrbitControls(camera,renderer.domElement);controls.enableDamping=true;controls.dampingFactor=.08;controls.minZoom=.25;controls.maxZoom=60;controls.maxPolarAngle=Math.PI*.485;controls.screenSpacePanning=true;controls.addEventListener('change',render);
 let lastAspect=aspect();const observer=new ResizeObserver(()=>{const a=aspect();if(a<lastAspect)frameHeight*=lastAspect/a;lastAspect=a;renderer.setSize(host.clientWidth,host.clientHeight);updateFrustum();render();});observer.observe(host);
 renderer.setSize(host.clientWidth,host.clientHeight);fullView('aerial');refreshList();
 const ray=new THREE.Raycaster(),pointer=new THREE.Vector2();let down=null;
 function pick(e){const b=renderer.domElement.getBoundingClientRect();pointer.set((e.clientX-b.left)/b.width*2-1,-(e.clientY-b.top)/b.height*2+1);ray.setFromCamera(pointer,camera);return ray.intersectObjects(pickMeshes.filter(m=>m.visible&&m.parent.visible),false).find(h=>!$('cut-enabled').checked||h.point.z<=clipPlane.constant)?.object.userData.code||null;}
 renderer.domElement.addEventListener('pointerdown',e=>down={x:e.clientX,y:e.clientY});renderer.domElement.addEventListener('pointerup',e=>{if(down&&e.button===0&&Math.hypot(e.clientX-down.x,e.clientY-down.y)<5)selectBuilding(pick(e));down=null;});
 renderer.domElement.addEventListener('pointermove',e=>{const tip=$('hover-tip');if(e.buttons||e.pointerType==='touch'){tip.style.display='none';return;}const code=pick(e);if(code){const r=byCode.get(code);tip.textContent=nameOf(r)+' · '+r.height.toFixed(2)+' m';tip.style.display='block';const b=host.getBoundingClientRect();tip.style.left=Math.min(e.clientX-b.left+14,host.clientWidth-tip.offsetWidth-10)+'px';tip.style.top=Math.min(e.clientY-b.top+14,host.clientHeight-tip.offsetHeight-38)+'px';renderer.domElement.style.cursor='pointer';}else{tip.style.display='none';renderer.domElement.style.cursor='grab';}});
 renderer.domElement.addEventListener('pointerleave',()=>$('hover-tip').style.display='none');renderer.domElement.addEventListener('webglcontextlost',e=>{e.preventDefault();$('status-text').textContent=t('lost');});
 function animate(){requestAnimationFrame(animate);controls.update();}animate();$('loading').remove();
}catch(err){console.error(err);if(renderer)renderer.dispose();renderer=null;staticMode=true;$('canvas-host').replaceChildren();$('fallback').src=data.preview;$('fallback').style.display='block';$('loading').remove();const note=document.createElement('div');note.className='error-message';note.id='render-error';note.textContent=t('error');host.append(note);$('download-image').disabled=true;updateCount();}
