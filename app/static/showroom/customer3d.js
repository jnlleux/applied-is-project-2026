import * as THREE from './vendor/three.module.min.js';
export function createCar(host,moving=true){
 const renderer=new THREE.WebGLRenderer({antialias:true,alpha:true});renderer.setPixelRatio(Math.min(devicePixelRatio,2));renderer.shadowMap.enabled=true;
 host.replaceChildren(renderer.domElement);renderer.domElement.setAttribute('role','img');renderer.domElement.setAttribute('aria-label','Трёхмерная модель автомобиля на вращающемся подиуме');
 const scene=new THREE.Scene(),camera=new THREE.PerspectiveCamera(36,1,.1,100);camera.position.set(6,4.2,7);camera.lookAt(0,.6,0);
 scene.add(new THREE.HemisphereLight(0xffffff,0x72877c,3));const lamp=new THREE.DirectionalLight(0xffffff,4);lamp.position.set(3,7,5);lamp.castShadow=true;scene.add(lamp);
 const car=new THREE.Group();scene.add(car);const paint=new THREE.MeshStandardMaterial({color:'#227d72',metalness:.5,roughness:.27});
 const dark=new THREE.MeshStandardMaterial({color:'#202b36',roughness:.5}),glass=new THREE.MeshStandardMaterial({color:'#a1c3cf',metalness:.6,roughness:.12}),silver=new THREE.MeshStandardMaterial({color:'#d9e1e1',metalness:.8,roughness:.25});
 const resources=[];
 function box(w,h,d,material,x,y,z){const geometry=new THREE.BoxGeometry(w,h,d);resources.push(geometry);const mesh=new THREE.Mesh(geometry,material);mesh.position.set(x,y,z);mesh.castShadow=true;car.add(mesh);return mesh;}
 box(3.8,.55,1.65,paint,0,.65,0);box(2,.65,1.42,glass,-.2,1.2,0);box(2.05,.09,1.48,paint,-.2,1.56,0);box(.13,.68,1.48,paint,-.25,1.2,0);box(1,.16,1.6,paint,1.35,.98,0);
 box(.08,.18,1.1,dark,1.94,.62,0);box(.08,.14,1.3,silver,-1.94,.6,0);
 const headlights=new THREE.MeshStandardMaterial({color:'#fff4c9',emissive:'#fff4c9',emissiveIntensity:1.5});const tail=new THREE.MeshStandardMaterial({color:'#e26155',emissive:'#8c2218'});
 for(const z of [-.58,.58]){box(.08,.16,.32,headlights,1.94,.84,z);box(.08,.15,.32,tail,-1.94,.84,z);}
 for(const x of [-1.18,1.18])for(const z of [-.85,.85]){const geo=new THREE.CylinderGeometry(.39,.39,.23,32);resources.push(geo);const tire=new THREE.Mesh(geo,dark);tire.rotation.x=Math.PI/2;tire.position.set(x,.4,z);car.add(tire);const rimGeo=new THREE.CylinderGeometry(.23,.23,.25,16);resources.push(rimGeo);const rim=new THREE.Mesh(rimGeo,silver);rim.rotation.x=Math.PI/2;rim.position.copy(tire.position);car.add(rim);}
 const stageGeo=new THREE.CylinderGeometry(3.1,3.2,.15,80);resources.push(stageGeo);const stageMat=new THREE.MeshStandardMaterial({color:'#e3e9dc',roughness:.9});const stage=new THREE.Mesh(stageGeo,stageMat);stage.position.y=-.08;stage.receiveShadow=true;scene.add(stage);
 let frame,drag=false,last=0,previous=performance.now();car.rotation.y=-.35;
 const down=e=>{drag=true;last=e.clientX;renderer.domElement.setPointerCapture(e.pointerId);},move=e=>{if(drag){car.rotation.y+=(e.clientX-last)*.012;last=e.clientX;}},up=()=>{drag=false;};
 renderer.domElement.style.touchAction='pan-y';renderer.domElement.addEventListener('pointerdown',down);renderer.domElement.addEventListener('pointermove',move);renderer.domElement.addEventListener('pointerup',up);renderer.domElement.addEventListener('pointercancel',up);
 const resize=new ResizeObserver(()=>{const w=host.clientWidth,h=host.clientHeight;renderer.setSize(w,h);camera.aspect=w/Math.max(h,1);camera.updateProjectionMatrix();});resize.observe(host);
 function animate(now){const dt=Math.min((now-previous)/1000,.05);previous=now;if(moving&&!drag&&!document.hidden)car.rotation.y+=dt*.3;renderer.render(scene,camera);frame=requestAnimationFrame(animate);}frame=requestAnimationFrame(animate);
 return {setMoving(value){moving=value;},setColor(value){paint.color.set(value);},dispose(){cancelAnimationFrame(frame);resize.disconnect();resources.forEach(r=>r.dispose());[paint,dark,glass,silver,headlights,tail,stageMat].forEach(m=>m.dispose());renderer.dispose();renderer.domElement.remove();}};
}
