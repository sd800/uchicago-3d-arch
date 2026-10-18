import {Box3,Vector3} from 'three';
import {frameCampusBox} from './campus_controls.js';

// A bearing describes the camera side, clockwise from model north (+Y).
// Previously authored record presets have precedence over this presentation catalogue.
export function highlightCamera(record,catalogue,fallback={}) {
 const id=String(record?.facility_id??record?.osm_id??'');
 const view=catalogue.views[id];
 let direction=record?.focus_direction;
 if(!direction&&view){
  const a=view.azimuth_deg*Math.PI/180,e=view.elevation_deg*Math.PI/180;
  direction=[Math.sin(a),Math.cos(a),Math.tan(e)];
 }
 direction??=fallback.direction;
 const center=record?.focus_center??view?.center_m,span=record?.focus_span??view?.span_m;
 return {direction:direction?new Vector3(...direction):undefined,pad:record?.focus_padding??view?.padding??fallback.pad??1.55,center:Array.isArray(center)&&center.length===3&&center.every(Number.isFinite)?new Vector3(...center):undefined,span:Number.isFinite(span)&&span>0?span:undefined};
}

/** Use authored metric framing when supplied; otherwise fit the building. */
export function frameHighlightCamera(camera,controls,bounds,shot,{aspect,distance=3000}) {
 const fixed=shot.center&&shot.span;
 const box=fixed?new Box3(shot.center.clone(),shot.center.clone()):bounds;
 return frameCampusBox(camera,controls,box,{
  aspect,distance,pad:shot.pad,direction:shot.direction,
  minimumHeight:fixed?shot.span:50,pivotHeight:fixed?shot.center.z:undefined
 });
}
