import streamlit as st
import streamlit.components.v1 as components

st.set_page_config(page_title="LIGHT LAB", page_icon="🔦", layout="wide")

st.markdown("""
<style>
.block-container {padding-top:1rem;padding-bottom:1rem;max-width:1100px}
</style>
""", unsafe_allow_html=True)

st.title("🔦 LIGHT LAB : 빛의 경로를 설계하라")
st.caption("거울과 프리즘으로 빛을 조종하고, 목표물이 요구하는 색을 정확히 전달하세요.")

html = r"""
<!DOCTYPE html><html lang="ko"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<style>
*{box-sizing:border-box}body{margin:0;background:#0b1220;color:#e5edf9;font-family:system-ui,-apple-system,sans-serif}
.wrap{width:100%;max-width:1000px;margin:auto;padding:8px}
.head{display:flex;justify-content:space-between;align-items:center;gap:10px;flex-wrap:wrap;margin-bottom:9px}
h2{font-size:18px;margin:0}.sub{font-size:12px;color:#9db1ce;margin-top:3px}
.panel{background:#111e32;border:1px solid #2b405e;border-radius:13px;padding:11px;margin-bottom:10px}
.levelrow{display:flex;align-items:center;gap:8px;flex-wrap:wrap}
button,select{border:1px solid #405675;background:#1b2b43;color:#edf5ff;padding:9px 12px;border-radius:9px;font-weight:700;font-size:13px;cursor:pointer}
button:hover{background:#2a4161}button:disabled{opacity:.35;cursor:not-allowed}
button.primary{background:#2563eb;border-color:#3b82f6}button.selected{outline:2px solid #67e8f9;background:#164e63}
button.small{padding:7px 10px}
.boardbox{background:#101c30;border:1px solid #263b59;border-radius:14px;padding:7px;box-shadow:0 12px 35px #0005}
canvas{display:block;width:100%;height:auto;border-radius:8px;touch-action:manipulation}
.tools{display:flex;gap:7px;flex-wrap:wrap;margin:10px 0}
.statusline{display:flex;justify-content:space-between;align-items:center;gap:8px;flex-wrap:wrap;font-size:13px;color:#b8c9df}
.goals{display:flex;gap:7px;flex-wrap:wrap;margin-top:9px}
.goalchip{font-size:12px;padding:6px 9px;border:1px solid #3a506e;border-radius:20px;background:#172840}
.goalchip.done{border-color:#4ade80;color:#bbf7d0;background:#123326}
.bar{height:9px;background:#26364e;border-radius:20px;overflow:hidden;min-width:120px;flex:1}
.fill{height:100%;width:0;background:linear-gradient(90deg,#22d3ee,#a78bfa,#f472b6);transition:width .2s}
.hint{font-size:12px;color:#9db1ce;line-height:1.5;margin-top:9px;min-height:18px}
.win{color:#86efac;font-weight:800}.warn{color:#fcd34d}
@media(max-width:560px){.wrap{padding:4px}.panel{padding:9px}button,select{padding:8px 9px}}
</style></head><body><div class="wrap">
<div class="head"><div><h2 id="levelTitle">STAGE 01 · 첫 번째 빛</h2><div class="sub" id="levelDesc">프리즘으로 빛을 분리해 보세요.</div></div>
<div class="levelrow"><button class="small" id="prev">◀ 이전</button><span id="stageCount" class="sub">1 / 10</span><button class="small" id="next">다음 ▶</button></div></div>
<div class="panel">
 <div class="statusline"><span>목표 충전 진행도</span><b id="pct">0%</b></div>
 <div class="bar"><div class="fill" id="fill"></div></div>
 <div class="goals" id="goals"></div>
</div>
<div class="boardbox"><canvas id="game" width="900" height="650"></canvas></div>
<div class="tools">
 <button id="mirror" class="selected">◢ 거울 배치</button>
 <button id="prism">◇ 프리즘 배치</button>
 <button id="fire" class="primary">▶ 빛 발사</button>
 <button id="reset">↺ 현재 단계 초기화</button>
</div>
<div class="panel">
 <div class="statusline"><b>조작 방법</b><span>부품을 다시 클릭하면 회전 · 우클릭하면 제거</span></div>
 <div class="hint" id="hint">프리즘을 레이저 경로에 배치해 빛을 RGB 세 가지 색으로 분리하세요.</div>
</div>
</div>
<script>
(()=>{
const canvas=document.getElementById('game'),ctx=canvas.getContext('2d');
const W=10,H=7,S=82,OX=40,OY=35;
const COLORS={R:'#fb5268',G:'#42df91',B:'#5b9cff'};
const COLOR_NAMES={R:'빨강',G:'초록',B:'파랑'};
const levels=[
 {name:'첫 번째 빛',desc:'프리즘을 설치하고 빨간색 빛을 목표물에 보내세요.',goals:[{x:8,y:3,c:'R'}]},
 {name:'두 갈래',desc:'빨간색과 초록색 목표물을 각각 충전하세요.',goals:[{x:8,y:3,c:'R'},{x:2,y:6,c:'G'}]},
 {name:'RGB의 시작',desc:'프리즘에서 나온 세 가지 색을 모두 전달하세요.',goals:[{x:8,y:3,c:'R'},{x:2,y:6,c:'G'},{x:2,y:0,c:'B'}]},
 {name:'색의 삼각형',desc:'프리즘을 중앙에 놓고 세 방향으로 빛을 보내세요.',goals:[{x:8,y:3,c:'R'},{x:5,y:6,c:'G'},{x:5,y:0,c:'B'}]},
 {name:'반사 실험',desc:'빨간 빛은 거울로 아래쪽에 반사하고, 초록·파랑도 맞추세요.',goals:[{x:7,y:6,c:'R'},{x:5,y:6,c:'G'},{x:5,y:0,c:'B'}]},
 {name:'엇갈린 목표',desc:'프리즘을 통과한 빛의 경로를 거울로 조절하세요.',goals:[{x:8,y:3,c:'R'},{x:3,y:6,c:'G'},{x:3,y:0,c:'B'}]},
 {name:'두 번의 반사',desc:'거울을 여러 개 사용해 빛을 목표물로 유도하세요.',goals:[{x:8,y:1,c:'R'},{x:2,y:6,c:'G'},{x:2,y:0,c:'B'}]},
 {name:'컬러 미션',desc:'세 색의 목표물이 서로 다른 위치에 있습니다.',goals:[{x:8,y:5,c:'R'},{x:6,y:6,c:'G'},{x:6,y:0,c:'B'}]},
 {name:'정밀 조준',desc:'거울과 프리즘의 위치를 신중하게 선택하세요.',goals:[{x:8,y:2,c:'R'},{x:4,y:6,c:'G'},{x:4,y:0,c:'B'}]},
 {name:'마스터 광학자',desc:'마지막 도전! 모든 색을 정확한 목표물에 전달하세요.',goals:[{x:8,y:3,c:'R'},{x:7,y:6,c:'G'},{x:7,y:0,c:'B'}]}
];
let stage=0,unlocked=0,tool='mirror',pieces=[],rays=[],lit=[],won=false;
const source={x:0,y:3,dir:1};
const $=id=>document.getElementById(id);
const pos=(x,y)=>({x:OX+x*S+S/2,y:OY+y*S+S/2});
function updatePanel(){
 const lv=levels[stage],done=lit.length,pct=Math.round(done/lv.goals.length*100);
 $('levelTitle').textContent=`STAGE ${String(stage+1).padStart(2,'0')} · ${lv.name}`;
 $('levelDesc').textContent=lv.desc;$('stageCount').textContent=`${stage+1} / ${levels.length}`;
 $('pct').textContent=pct+'%';$('fill').style.width=pct+'%';
 $('prev').disabled=stage===0;$('next').disabled=stage>=unlocked;
 $('goals').innerHTML=lv.goals.map((g,i)=>`<span class="goalchip ${lit.includes(i)?'done':''}">${lit.includes(i)?'✓':'○'} ${COLOR_NAMES[g.c]} 목표물</span>`).join('');
}
function draw(){
 ctx.clearRect(0,0,900,650);ctx.fillStyle='#0d192b';ctx.fillRect(0,0,900,650);
 for(let y=0;y<H;y++)for(let x=0;x<W;x++){
  ctx.fillStyle=(x+y)%2?'#14243a':'#172941';ctx.fillRect(OX+x*S,OY+y*S,S-2,S-2);
  ctx.strokeStyle='#29415f';ctx.strokeRect(OX+x*S,OY+y*S,S-2,S-2);
 }
 // source
 let sp=pos(source.x,source.y);ctx.save();ctx.shadowColor='#fff4a3';ctx.shadowBlur=18;ctx.fillStyle='#fff0a6';
 ctx.beginPath();ctx.arc(sp.x,sp.y,14,0,Math.PI*2);ctx.fill();ctx.restore();
 ctx.fillStyle='#fff';ctx.font='bold 12px sans-serif';ctx.textAlign='center';ctx.fillText('LASER',sp.x,sp.y+31);
 // color-coded goals
 levels[stage].goals.forEach((g,i)=>{
  let p=pos(g.x,g.y),on=lit.includes(i),color=COLORS[g.c];
  ctx.save();ctx.shadowColor=color;ctx.shadowBlur=on?24:9;
  ctx.fillStyle=on?color+'55':'#10243a';ctx.strokeStyle=color;ctx.lineWidth=4;
  ctx.beginPath();ctx.arc(p.x,p.y,25,0,Math.PI*2);ctx.fill();ctx.stroke();
  ctx.fillStyle=on?'#ffffff':color;ctx.font='bold 15px sans-serif';ctx.fillText(g.c,p.x,p.y+5);
  ctx.font='10px sans-serif';ctx.fillText(on?'FULL':'GOAL',p.x,p.y+39);ctx.restore();
 });
 // optical devices
 pieces.forEach(p=>{
  let q=pos(p.x,p.y);ctx.save();ctx.translate(q.x,q.y);ctx.lineWidth=7;ctx.lineCap='round';
  if(p.type==='mirror'){
   ctx.strokeStyle='#e2e8f0';ctx.shadowColor='#93c5fd';ctx.shadowBlur=9;
   ctx.beginPath();if(p.rot===0){ctx.moveTo(-23,23);ctx.lineTo(23,-23)}else{ctx.moveTo(-23,-23);ctx.lineTo(23,23)}ctx.stroke();
   ctx.fillStyle='#94a3b8';ctx.beginPath();ctx.arc(0,0,4,0,7);ctx.fill();
  }else{
   ctx.fillStyle='#5eead4';ctx.strokeStyle='#a5f3fc';ctx.lineWidth=3;ctx.shadowColor='#22d3ee';ctx.shadowBlur=10;
   ctx.beginPath();ctx.moveTo(0,-27);ctx.lineTo(25,22);ctx.lineTo(-25,22);ctx.closePath();ctx.fill();ctx.stroke();
   ctx.fillStyle='#083344';ctx.font='bold 13px sans-serif';ctx.textAlign='center';ctx.fillText('RGB',0,8);
  }ctx.restore();
 });
 rays.forEach(r=>{
  ctx.save();ctx.strokeStyle=r.color;ctx.lineWidth=4;ctx.shadowColor=r.color;ctx.shadowBlur=12;
  ctx.beginPath();ctx.moveTo(pos(r.x0,r.y0).x,pos(r.x0,r.y0).y);ctx.lineTo(pos(r.x1,r.y1).x,pos(r.x1,r.y1).y);ctx.stroke();ctx.restore();
 });
 if(won){ctx.fillStyle='#86efac';ctx.font='bold 30px sans-serif';ctx.textAlign='center';ctx.fillText('STAGE CLEAR!',450,24);}
}
function reflect(dir,rot){return rot===0?[1,0,3,2][dir]:[3,2,1,0][dir];}
function fire(){
 rays=[];lit=[];won=false;let queue=[{x:source.x,y:source.y,dir:source.dir,color:'#fff0a6',code:'W'}];
 let visited=new Set(),goalHits={};
 while(queue.length){
  let r=queue.shift(),steps=0;
  while(steps++<100){
   let nx=r.x+[0,1,0,-1][r.dir],ny=r.y+[-1,0,1,0][r.dir];
   if(nx<0||nx>=W||ny<0||ny>=H)break;
   let state=`${nx},${ny},${r.dir},${r.code}`;if(visited.has(state))break;visited.add(state);
   rays.push({x0:r.x,y0:r.y,x1:nx,y1:ny,color:r.color});
   let gi=levels[stage].goals.findIndex(g=>g.x===nx&&g.y===ny);
   if(gi>=0){if(levels[stage].goals[gi].c===r.code)goalHits[gi]=true;r.x=nx;r.y=ny;break;}
   let device=pieces.find(p=>p.x===nx&&p.y===ny);
   if(device&&device.type==='mirror'){r.dir=reflect(r.dir,device.rot);r.x=nx;r.y=ny;continue;}
   if(device&&device.type==='prism'){
    // 입사한 빛을 빨강(직진), 초록(아래), 파랑(위)으로 분리
    [{dir:r.dir,code:'R'},{dir:(r.dir+1)%4,code:'G'},{dir:(r.dir+3)%4,code:'B'}].forEach(b=>queue.push({x:nx,y:ny,dir:b.dir,code:b.code,color:COLORS[b.code]}));
    break;
   }
   r.x=nx;r.y=ny;
  }
 }
 lit=Object.keys(goalHits).map(Number);won=lit.length===levels[stage].goals.length;
 if(won)unlocked=Math.max(unlocked,Math.min(stage+1,levels.length-1));
 updatePanel();draw();
 if(won){$('hint').innerHTML='<span class="win">🎉 스테이지 클리어! 모든 목표물이 지정된 색으로 충전되었습니다.</span>';if(stage===levels.length-1)$('hint').innerHTML+='<br>🏆 축하합니다! 모든 10개 스테이지를 완료했습니다!';}
 else{
  let wrong=levels[stage].goals.filter((g,i)=>!lit.includes(i)).map(g=>COLOR_NAMES[g.c]).join(', ');
  $('hint').innerHTML=`<span class="warn">아직 충전되지 않은 목표물: ${wrong}</span> · 목표물의 색과 빛의 색이 일치하는지 확인하세요.`;
 }
}
function setTool(t){tool=t;$('mirror').classList.toggle('selected',t==='mirror');$('prism').classList.toggle('selected',t==='prism');}
function reset(){pieces=[];rays=[];lit=[];won=false;updatePanel();draw();$('hint').textContent='부품을 배치하고 빛을 발사해 보세요. 프리즘은 RGB 세 가지 색으로 빛을 나눕니다.';}
function changeStage(n){if(n<0||n>=levels.length||n>unlocked)return;stage=n;reset();}
$('mirror').onclick=()=>setTool('mirror');$('prism').onclick=()=>setTool('prism');
$('fire').onclick=fire;$('reset').onclick=reset;
$('prev').onclick=()=>changeStage(stage-1);$('next').onclick=()=>changeStage(stage+1);
function clickCell(e){
 const rect=canvas.getBoundingClientRect(),x=(e.clientX-rect.left)*canvas.width/rect.width,y=(e.clientY-rect.top)*canvas.height/rect.height;
 let gx=Math.floor((x-OX)/S),gy=Math.floor((y-OY)/S);
 if(gx<0||gx>=W||gy<0||gy>=H||(gx===source.x&&gy===source.y)||levels[stage].goals.some(g=>g.x===gx&&g.y===gy))return;
 let p=pieces.find(q=>q.x===gx&&q.y===gy);
 if(e.button===2){if(p)pieces=pieces.filter(q=>q!==p);}
 else if(p){p.rot=(p.rot+1)%2;}
 else pieces.push({x:gx,y:gy,type:tool,rot:0});
 rays=[];lit=[];won=false;updatePanel();draw();
}
canvas.addEventListener('click',clickCell);canvas.addEventListener('contextmenu',e=>{e.preventDefault();clickCell(e);});
updatePanel();draw();
})();
</script></body></html>
"""

components.html(html, height=900, scrolling=False)
st.caption("색상 규칙: 프리즘은 빨강(R)은 직진, 초록(G)은 아래쪽, 파랑(B)은 위쪽으로 분리합니다. 목표물은 표시된 색과 같은 빛을 받아야 충전됩니다.")
