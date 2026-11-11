import streamlit as st
import streamlit.components.v1 as components

st.set_page_config(page_title="LIGHT LAB", page_icon="🔦", layout="wide")

st.markdown("""
<style>
  .block-container {padding-top: 1.2rem; padding-bottom: 1rem; max-width: 1100px;}
  h1 {letter-spacing: -1px;}
  [data-testid="stMarkdownContainer"] p {line-height: 1.55;}
</style>
""", unsafe_allow_html=True)

st.title("🔦 LIGHT LAB : 빛의 경로를 설계하라")
st.caption("거울과 프리즘을 배치해 빛을 목표물까지 보내는 퍼즐 게임")

with st.expander("🎮 게임 방법", expanded=True):
    st.markdown("""
    1. 아래 부품 목록에서 **거울 / 프리즘**을 선택한 뒤, 게임판의 칸을 눌러 배치하세요.
    2. 배치한 부품을 누르면 회전합니다. **우클릭**하면 제거할 수 있어요.
    3. **빛 발사**를 누르면 광선이 이동합니다. 목표물의 충전량이 100%가 되면 클리어!
    4. 거울은 빛의 방향을 바꾸고, 프리즘은 빛을 세 갈래(R/G/B)로 분리합니다.
    """)

html = r"""
<!DOCTYPE html><html lang="ko"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<style>
*{box-sizing:border-box} body{margin:0;background:#0b1220;color:#e5edf9;font-family:system-ui,-apple-system,sans-serif}
.wrap{width:100%;max-width:980px;margin:auto;padding:10px}
.top{display:flex;justify-content:space-between;align-items:center;gap:10px;flex-wrap:wrap;margin-bottom:10px}
.status{font-size:14px;color:#a9bdd8}.bar{height:10px;background:#26364e;border-radius:20px;overflow:hidden;width:180px;display:inline-block;vertical-align:middle;margin-left:7px}
.fill{height:100%;width:0;background:linear-gradient(90deg,#22d3ee,#a78bfa,#f472b6);transition:width .2s}
button{border:1px solid #425574;background:#1b2b43;color:#eaf2ff;padding:9px 13px;border-radius:10px;font-weight:700;cursor:pointer}
button:hover{background:#2b4161}button.primary{background:#2563eb;border-color:#3b82f6}button.selected{outline:2px solid #67e8f9;background:#164e63}
.boardbox{background:#101c30;border:1px solid #263b59;border-radius:14px;padding:8px;box-shadow:0 12px 35px #0005}
canvas{display:block;width:100%;height:auto;touch-action:manipulation;border-radius:8px}
.tools{display:flex;gap:8px;flex-wrap:wrap;margin:11px 0}.tool{display:flex;align-items:center;gap:7px}
.hint{font-size:12px;color:#91a6c4;margin-top:7px}.win{color:#86efac;font-weight:800}
</style></head><body><div class="wrap">
<div class="top"><div><b>실험실 01</b> <span class="status">· 목표물에 빛을 모으세요</span></div>
<div class="status">목표 충전 <b id="pct">0%</b><span class="bar"><span class="fill" id="fill"></span></span></div></div>
<div class="boardbox"><canvas id="game" width="900" height="570"></canvas></div>
<div class="tools">
<button id="mirror" class="selected">◢ 거울 배치</button>
<button id="prism">◇ 프리즘 배치</button>
<button id="fire" class="primary">▶ 빛 발사</button>
<button id="reset">↺ 초기화</button>
</div>
<div class="hint" id="hint">거울을 선택한 상태입니다. 게임판의 빈 칸을 눌러 배치하세요. 배치한 부품을 다시 누르면 방향이 바뀝니다.</div>
</div>
<script>
(()=>{
const c=document.getElementById('game'),ctx=c.getContext('2d');
const W=10,H=6,S=80,OX=50,OY=45;
const source={x:0,y:3,dir:1}, target={x:9,y:2};
let pieces=[],tool='mirror',rays=[],charge=0,anim=null;
const key=(x,y)=>x+','+y;
function draw(){
 ctx.clearRect(0,0,900,570);
 ctx.fillStyle='#0d192b';ctx.fillRect(0,0,900,570);
 for(let y=0;y<H;y++)for(let x=0;x<W;x++){
  ctx.fillStyle=(x+y)%2?'#14243a':'#172941';ctx.fillRect(OX+x*S,OY+y*S,S-2,S-2);
  ctx.strokeStyle='#29415f';ctx.strokeRect(OX+x*S,OY+y*S,S-2,S-2);
 }
 // source
 let sx=OX+source.x*S+S/2,sy=OY+source.y*S+S/2;
 ctx.save();ctx.shadowColor='#fbbf24';ctx.shadowBlur=18;ctx.fillStyle='#fbbf24';
 ctx.beginPath();ctx.arc(sx,sy,14,0,Math.PI*2);ctx.fill();ctx.restore();
 ctx.fillStyle='#fff';ctx.font='bold 12px sans-serif';ctx.textAlign='center';ctx.fillText('LASER',sx,sy+31);
 // target
 let tx=OX+target.x*S+S/2,ty=OY+target.y*S+S/2;
 ctx.save();ctx.shadowColor='#22d3ee';ctx.shadowBlur=charge>0?18:0;
 ctx.fillStyle='#102f46';ctx.strokeStyle='#67e8f9';ctx.lineWidth=4;
 ctx.beginPath();ctx.arc(tx,ty,25,0,Math.PI*2);ctx.fill();ctx.stroke();
 ctx.fillStyle='#67e8f9';ctx.font='bold 12px sans-serif';ctx.fillText('GOAL',tx,ty+4);ctx.restore();
 // pieces
 pieces.forEach(p=>{
  let x=OX+p.x*S+S/2,y=OY+p.y*S+S/2;
  ctx.save();ctx.translate(x,y);ctx.lineWidth=7;ctx.lineCap='round';
  if(p.type==='mirror'){
   ctx.strokeStyle='#e2e8f0';ctx.shadowColor='#93c5fd';ctx.shadowBlur=8;
   ctx.beginPath(); if(p.rot%2===0){ctx.moveTo(-23,23);ctx.lineTo(23,-23)}else{ctx.moveTo(-23,-23);ctx.lineTo(23,23)}ctx.stroke();
   ctx.fillStyle='#94a3b8';ctx.beginPath();ctx.arc(0,0,4,0,7);ctx.fill();
  }else{
   ctx.fillStyle='#5eead4';ctx.strokeStyle='#a5f3fc';ctx.lineWidth=3;ctx.shadowColor='#22d3ee';ctx.shadowBlur=10;
   ctx.beginPath();ctx.moveTo(0,-27);ctx.lineTo(25,22);ctx.lineTo(-25,22);ctx.closePath();ctx.fill();ctx.stroke();
   ctx.fillStyle='#083344';ctx.font='bold 13px sans-serif';ctx.textAlign='center';ctx.fillText('P',0,9);
  }ctx.restore();
 });
 // rays
 rays.forEach(r=>{
  ctx.save();ctx.strokeStyle=r.color;ctx.lineWidth=4;ctx.shadowColor=r.color;ctx.shadowBlur=12;
  ctx.beginPath();ctx.moveTo(OX+(r.x0+.5)*S,OY+(r.y0+.5)*S);ctx.lineTo(OX+(r.x1+.5)*S,OY+(r.y1+.5)*S);ctx.stroke();ctx.restore();
 });
 if(charge>=100){ctx.fillStyle='#86efac';ctx.font='bold 28px sans-serif';ctx.textAlign='center';ctx.fillText('CLEAR!',450,28);}
}
function reflect(dir,rot){ // dir: 0 up,1 right,2 down,3 left
 if(rot%2===0)return [1,0,3,2][dir]; // /
 return [3,2,1,0][dir]; // \
}
function trace(){
 rays=[];let visited=new Set(),queue=[{x:source.x,y:source.y,dir:source.dir,color:'#fef08a',x0:source.x,y0:source.y}];
 let hit=false;
 while(queue.length){
  let r=queue.shift(),steps=0;
  while(steps++<80){
   let nx=r.x+[0,1,0,-1][r.dir],ny=r.y+[-1,0,1,0][r.dir];
   if(nx<0||nx>=W||ny<0||ny>=H)break;
   let id=key(nx,ny)+':'+r.dir+':'+r.color;if(visited.has(id))break;visited.add(id);
   rays.push({x0:r.x,y0:r.y,x1:nx,y1:ny,color:r.color});
   if(nx===target.x&&ny===target.y){hit=true;break;}
   let p=pieces.find(q=>q.x===nx&&q.y===ny);
   if(p&&p.type==='mirror'){r.dir=reflect(r.dir,p.rot);r.x=nx;r.y=ny;continue;}
   if(p&&p.type==='prism'){
    let dirs=[r.dir,(r.dir+1)%4,(r.dir+3)%4],cols=['#fb7185','#4ade80','#60a5fa'];
    dirs.forEach((d,i)=>queue.push({x:nx,y:ny,dir:d,color:cols[i],x0:nx,y0:ny}));
    break;
   }
   r.x=nx;r.y=ny;
  }
 }
 charge=hit?100:0;
 document.getElementById('pct').textContent=charge+'%';
 document.getElementById('fill').style.width=charge+'%';
 document.getElementById('hint').innerHTML=hit?'<span class="win">🎉 성공! 빛이 목표물에 도달했습니다. 실험 클리어!</span>':'빛이 목표물에 도달하지 못했어요. 부품의 위치와 방향을 바꿔보세요.';
 draw();
}
function setTool(t){tool=t;document.getElementById('mirror').classList.toggle('selected',t==='mirror');document.getElementById('prism').classList.toggle('selected',t==='prism');}
document.getElementById('mirror').onclick=()=>setTool('mirror');
document.getElementById('prism').onclick=()=>setTool('prism');
document.getElementById('fire').onclick=trace;
document.getElementById('reset').onclick=()=>{pieces=[];rays=[];charge=0;document.getElementById('pct').textContent='0%';document.getElementById('fill').style.width='0%';document.getElementById('hint').textContent='초기화했습니다. 부품을 배치해 다시 도전하세요.';draw();};
function cell(e){
 const rect=c.getBoundingClientRect(),x=(e.clientX-rect.left)*c.width/rect.width,y=(e.clientY-rect.top)*c.height/rect.height;
 let gx=Math.floor((x-OX)/S),gy=Math.floor((y-OY)/S);
 if(gx<0||gx>=W||gy<0||gy>=H|| (gx===source.x&&gy===source.y)||(gx===target.x&&gy===target.y))return;
 let p=pieces.find(q=>q.x===gx&&q.y===gy);
 if(e.button===2){if(p)pieces=pieces.filter(q=>q!==p);draw();return;}
 if(p){p.rot=(p.rot+1)%2;}else pieces.push({x:gx,y:gy,type:tool,rot:0});
 rays=[];charge=0;document.getElementById('pct').textContent='0%';document.getElementById('fill').style.width='0%';draw();
}
c.addEventListener('click',cell);c.addEventListener('contextmenu',e=>{e.preventDefault();cell(e);});
draw();
})();
</script></body></html>
"""

components.html(html, height=760, scrolling=False)

st.info("팁: 빛은 벽에 부딪히면 사라집니다. 거울의 방향을 바꾸거나 프리즘을 활용해 목표물까지 경로를 만들어 보세요.")
