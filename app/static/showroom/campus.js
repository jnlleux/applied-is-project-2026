import * as THREE from './vendor/three.module.min.js';
let savedAngle = .72;
export function mountCampus(host, {moving=true, night=false, parking=[], onNavigate=()=>{}, onSelectCar=()=>{}}={}) {
  const scene=new THREE.Scene(); scene.background=new THREE.Color('#f0eee3');
  const renderer=new THREE.WebGLRenderer({antialias:true,alpha:false});
  renderer.setPixelRatio(Math.min(window.devicePixelRatio||1,2));
  renderer.shadowMap.enabled=true;renderer.shadowMap.type=THREE.PCFSoftShadowMap;
  renderer.outputColorSpace=THREE.SRGBColorSpace;
  renderer.domElement.setAttribute('aria-label','Трёхмерная схема AutoRent. Перетащите для поворота; нажмите на здание для перехода в раздел.');
  renderer.domElement.setAttribute('role','img');host.replaceChildren(renderer.domElement);
  const camera=new THREE.OrthographicCamera(-14,14,10,-10,.1,100);
  let angle=savedAngle, zoom=1, frame=0, dead=false, drag=null, last=performance.now(), time=0;
  const meshes=[],materials=[],targets=[],cars=[];
  const mat=(color)=>{const m=new THREE.MeshStandardMaterial({color,roughness:.72});materials.push(m);return m;};
  const white=mat('#fafbf5'),ground=mat('#cddbd1'),road=mat('#aabbb6'),blue=mat('#4668b4'),mint=mat('#64b6a1'),glass=mat('#b5e3e0'),purple=mat('#a18ccc'),dark=mat('#263f46'),leaf=mat('#6cab83'),trunk=mat('#8a8268'),yellow=mat('#e5ba68');
  const block=(w,h,d,m,x,y,z,parent=scene)=>{const g=new THREE.BoxGeometry(w,h,d);meshes.push(g);const b=new THREE.Mesh(g,m);b.position.set(x,y,z);b.castShadow=true;b.receiveShadow=true;parent.add(b);return b;};
  const cylinder=(r,h,m,x,y,z,parent=scene,n=16)=>{const g=new THREE.CylinderGeometry(r,r,h,n);meshes.push(g);const b=new THREE.Mesh(g,m);b.position.set(x,y,z);b.castShadow=true;b.receiveShadow=true;parent.add(b);return b;};
  const building=(x,z,w,h,d,m,page)=>{const group=new THREE.Group();scene.add(group);const b=block(w,h,d,m,x,h/2+.25,z,group);block(w+.2,.16,d+.2,white,x,h+.3,z,group);group.userData.page=page;targets.push(group);return b;};
  const ambient=new THREE.HemisphereLight('#ffffff','#94a798',2.6);scene.add(ambient);
  const sun=new THREE.DirectionalLight('#fff6de',3);sun.position.set(-8,17,9);sun.castShadow=true;sun.shadow.mapSize.set(1024,1024);sun.shadow.camera.left=-14;sun.shadow.camera.right=14;sun.shadow.camera.top=14;sun.shadow.camera.bottom=-14;sun.shadow.normalBias=.03;scene.add(sun);
  block(20,.5,15,ground,0,-.1,0);block(18,.06,3,road,0,.2,3.4);block(2.4,.07,11,road,7,.2,-.5);
  for(let i=-8;i<=8;i+=1.2)block(.55,.015,.06,white,i,.25,3.4);
  for(let z=-5;z<5;z+=1.2)block(.06,.02,.55,white,7,.26,z);
  building(-3,-2,7,2.6,4,blue,'cars');
  for(let x=-5.5;x<=-.5;x+=1.25){block(.85,1.55,.06,glass,x,1.2,.04);block(1,.1,.3,white,x,2.05,.12);}
  for(let x=-5.5;x<=-1;x+=1.4)block(.8,.07,1.25,dark,x,3,-2);
  building(3,-3,2.7,6.2,2.7,mint,'users');
  for(let y=1;y<6;y+=.8)for(let x=2.1;x<4.1;x+=.65)block(.32,.42,.04,glass,x,y,-1.62);
  for(let y=1;y<6;y+=.8)for(let z=-3.9;z<-2;z+=.65)block(.04,.42,.32,glass,4.37,y,z);
  building(3.5,.4,2.3,1.3,1.6,purple,'inspections');
  block(.65,.8,.07,glass,3.5,.75,1.23);
  for(const x of [-6,-4]){cylinder(.07,1.35,white,x,.85,5.9);block(1.3,.14,1.7,mint,x,1.6,5.9);block(.25,.75,.28,dark,x,.65,6.3);}
  building(.7,5.7,2,1.3,1.6,yellow,'bookings');block(.75,.65,.04,glass,.7,1,6.53);
  function tree(x,z){cylinder(.075,.85,trunk,x,.65,z);const g=new THREE.IcosahedronGeometry(.46,1);meshes.push(g);const t=new THREE.Mesh(g,leaf);t.position.set(x,1.35,z);t.scale.y=1.35;t.castShadow=true;scene.add(t);}
  [[-8,-5],[-8,-2],[-8,1],[-8,6],[1,6.5],[3,6.5],[5,6.5],[8,-6],[6,-6],[0,-6]].forEach(p=>tree(...p));
  const lamps=[];
  for(const [x,z] of [[-7,2],[.5,2],[6,1],[6,5]]){const light=new THREE.PointLight('#ffdf9a',0,7);light.position.set(x,1.8,z);scene.add(light);lamps.push(light);cylinder(.035,1.7,dark,x,1,z);block(.35,.1,.35,white,x,1.9,z);}
  function car(x,z,color,rotation=0){const g=new THREE.Group();scene.add(g);g.position.set(x,.32,z);g.rotation.y=rotation;const paint=mat(color);block(1.35,.33,.64,paint,0,.32,0,g);block(.68,.3,.57,glass,-.08,.63,0,g);block(.67,.07,.6,paint,-.08,.81,0,g);for(const a of [-.43,.43])for(const b of [-.34,.34]){const wheel=cylinder(.16,.1,dark,a,.18,b,g);wheel.rotation.x=Math.PI/2;}block(.05,.1,.42,white,.69,.35,0,g);return g;}
  ['#fafbf5','#83ad9c','#f3f0df','#859ac4','#f1d6a5'].forEach((c,i)=>{const x=-5.8+i*1.65;block(.035,.015,1.6,white,x-.75,.25,1.3);const parked=car(x,1.25,c,Math.PI/2);if(parking[i]){parked.userData.car=parking[i].id;targets.push(parked);}});
  cars.push(car(-5,3.5,'#fafbf5'));cars.push(car(4,4.2,'#c0ace2',Math.PI));
  const ringGeo=new THREE.TorusGeometry(.23,.055,8,24);meshes.push(ringGeo);const marker=new THREE.Mesh(ringGeo,mat('#f8f4ff'));marker.position.set(3.5,2.2,.4);marker.rotation.x=-Math.PI/2;scene.add(marker);
  // A working wash bay, charge beacons and a lifting entrance barrier.
  const wash=new THREE.Group();scene.add(wash);wash.userData.page='inspections';targets.push(wash);
  block(.16,1.7,1.9,purple,-3.2,1.05,5.5,wash);block(.16,1.7,1.9,purple,-1.4,1.05,5.5,wash);block(2.1,.2,2,white,-2.3,1.95,5.5,wash);
  const brushes=[cylinder(.2,1.1,mint,-2.95,.9,5.5,wash),cylinder(.2,1.1,mint,-1.65,.9,5.5,wash)];
  for(const brush of brushes){for(let i=0;i<6;i++){const rib=block(.08,1.1,.43,glass,0,0,0,brush);rib.rotation.y=i*Math.PI/3;}}
  car(-2.3,5.5,'#f1eddf',Math.PI/2);
  const gate=new THREE.Group();scene.add(gate);gate.position.set(5.6,1,3.4);cylinder(.13,.85,dark,5.6,.65,3.4);const arm=block(2.4,.12,.14,white,1.1,0,0,gate);
  for(let i=0;i<5;i++)block(.22,.13,.15,purple,.2+i*.42,0,0,gate);
  const beaconMat=mat('#89dfb6');beaconMat.emissive.set('#52b88c');const beacons=[cylinder(.08,.23,beaconMat,-6,1.8,5.9),cylinder(.08,.23,beaconMat,-4,1.8,5.9)];
  const signGroup=new THREE.Group();scene.add(signGroup);signGroup.userData.page='bookings';targets.push(signGroup);cylinder(.045,1.5,dark,6,1,-5,signGroup);block(.9,.6,.08,blue,6,1.9,-5,signGroup);
  const stripe=block(.48,.08,.09,white,6,1.9,-4.95,signGroup);stripe.rotation.z=.45;
  function setNight(value){night=value;scene.background.set(night?'#1d303a':'#f0eee3');ambient.intensity=night?.8:2.6;sun.intensity=night?.55:3;lamps.forEach(l=>l.intensity=night?7:0);glass.emissive.set(night?'#739c93':'#000000');glass.emissiveIntensity=night?.6:0;}
  setNight(night);
  const raycaster=new THREE.Raycaster(),pointer=new THREE.Vector2();
  function pose(){camera.position.set(Math.sin(angle)*21,17,Math.cos(angle)*21);camera.lookAt(0,1,0);camera.zoom=zoom;camera.updateProjectionMatrix();}
  function resize(){const w=Math.max(1,host.clientWidth),h=Math.max(1,host.clientHeight),aspect=w/h;camera.left=-11.4*aspect;camera.right=11.4*aspect;camera.top=11.4;camera.bottom=-11.4;renderer.setSize(w,h,false);pose();}
  const ro=new ResizeObserver(resize);ro.observe(host);resize();
  const down=e=>{drag={x:e.clientX,start:e.clientX,y:e.clientY,angle};renderer.domElement.setPointerCapture(e.pointerId);};
  const move=e=>{if(drag){angle=drag.angle+(e.clientX-drag.x)*.006;pose();}};
  const up=e=>{if(!drag)return;const click=Math.hypot(e.clientX-drag.start,e.clientY-drag.y)<5;drag=null;if(click){const r=renderer.domElement.getBoundingClientRect();pointer.set((e.clientX-r.left)/r.width*2-1,-(e.clientY-r.top)/r.height*2+1);raycaster.setFromCamera(pointer,camera);const hit=raycaster.intersectObjects(targets,true)[0];if(hit){let node=hit.object;while(node&&!node.userData.page&&!node.userData.car)node=node.parent;if(node?.userData.car)onSelectCar(node.userData.car);else if(node)onNavigate(node.userData.page);}}};
  const cancel=()=>{drag=null;};
  renderer.domElement.addEventListener('pointerdown',down);renderer.domElement.addEventListener('pointermove',move);renderer.domElement.addEventListener('pointerup',up);renderer.domElement.addEventListener('pointercancel',cancel);
  const lost=e=>{e.preventDefault();host.dataset.status='unavailable';};renderer.domElement.addEventListener('webglcontextlost',lost);
  function draw(now){if(dead)return;const dt=Math.min((now-last)/1000,.05);last=now;if(moving&&!document.hidden){time+=dt;cars[0].position.x=-8+(time*1.1)%16;cars[1].position.x=8-(time*.8+7)%16;marker.position.y=2.2+Math.sin(time*2)*.12;brushes.forEach(b=>b.rotation.y=time*2);gate.rotation.z=Math.max(0,Math.sin(time*.7))*.9;beaconMat.emissiveIntensity=.4+Math.sin(time*2)*.25;}renderer.render(scene,camera);frame=requestAnimationFrame(draw);}frame=requestAnimationFrame(draw);host.dataset.status='ready';
  return {setNight,setMoving(v){moving=v;},rotate(delta){angle+=delta;pose();},reset(){angle=.72;zoom=1;pose();},dispose(){dead=true;savedAngle=angle;cancelAnimationFrame(frame);ro.disconnect();for(const [name,handler] of [['pointerdown',down],['pointermove',move],['pointerup',up],['pointercancel',cancel],['webglcontextlost',lost]])renderer.domElement.removeEventListener(name,handler);meshes.forEach(x=>x.dispose());materials.forEach(x=>x.dispose());renderer.dispose();renderer.forceContextLoss();renderer.domElement.remove();}};
}
