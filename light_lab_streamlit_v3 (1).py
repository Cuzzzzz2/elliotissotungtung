import streamlit as st
import streamlit.components.v1 as components

st.set_page_config(page_title="LIGHT LAB", page_icon="🔦", layout="wide")

st.markdown("""
<style>
.block-container {padding-top:1rem;padding-bottom:1rem;max-width:1100px}
</style>
""", unsafe_allow_html=True)

st.title("🔦 LIGHT LAB : 빛의 경로를 설계하라")
st.caption("거울·프리즘·색상 필터로 빛을 조종하고, 제한된 이동 횟수 안에 모든 목표물을 충전하세요.")

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
button{border:1px solid #405675;background:#1b2b43;color:#edf5ff;padding:9px 12px;border-radius:9px;font-weight:700;font-size:13px;cursor:pointer}
button:hover:not(:disabled){background:#2a4161}button:disabled{opacity:.35;cursor:not-allowed}
button.primary{background:#2563eb;border-color:#3b82f6}button.selected{outline:2px solid #67e8f9;background:#164e63}
button.small{padding:7px 10px}
.menu{display:grid;grid-template-columns:repeat(12,1fr);gap:5px}
.stg{padding:5px 0;font-size:13px;line-height:1.2}.stg small{font-size:9px;color:#fcd34d}
.boardbox{background:#101c30;border:1px solid #263b59;border-radius:14px;padding:7px;box-shadow:0 12px 35px #0005}
canvas{display:block;width:100%;height:auto;border-radius:8px;touch-action:manipulation}
.tools{display:flex;gap:7px;flex-wrap:wrap;margin:10px 0}
.statusline{display:flex;justify-content:space-between;align-items:center;gap:8px;flex-wrap:wrap;font-size:13px;color:#b8c9df}
.goals{display:flex;gap:7px;flex-wrap:wrap;margin-top:9px}
.goalchip{font-size:12px;padding:6px 9px;border:1px solid #3a506e;border-radius:20px;background:#172840}
.goalchip.done{border-color:#4ade80;color:#bbf7d0;background:#123326}
.bar{height:9px;background:#26364e;border-radius:20px;overflow:hidden;margin-top:6px}
.fill{height:100%;width:0;background:linear-gradient(90deg,#22d3ee,#a78bfa,#f472b6);transition:width .2s}
.hint{font-size:13px;color:#b8c9df;line-height:1.55;margin-top:8px;min-height:20px}
.win{color:#86efac;font-weight:800}.warn{color:#fcd34d}
@media(max-width:560px){.wrap{padding:4px}.panel{padding:9px}button{padding:8px 9px}.menu{grid-template-columns:repeat(6,1fr)}}
</style></head><body><div class="wrap">
<div class="head"><div><h2 id="levelTitle"></h2><div class="sub" id="levelDesc"></div></div>
<div class="levelrow"><button class="small" id="prev">◀ 이전</button><span id="stageCount" class="sub"></span><button class="small" id="next">다음 ▶</button></div></div>
<div class="panel"><div class="menu" id="menu"></div><div class="sub" id="lockinfo" style="margin-top:7px"></div></div>
<div class="panel">
 <div class="statusline"><span>목표 충전 진행도</span><b id="pct">0%</b></div>
 <div class="bar"><div class="fill" id="fill"></div></div>
 <div class="goals" id="goals"></div>
</div>
<div class="boardbox"><canvas id="game" width="900" height="650"></canvas></div>
<div class="tools" id="tools"></div>
<div class="tools">
 <button id="fire" class="primary">▶ 빛 발사</button>
 <button id="undo">↶ 되돌리기</button>
 <button id="reset">↺ 초기화</button>
</div>
<div class="panel">
 <div class="statusline"><b>이동 횟수 <span id="moves"></span></b><span id="par"></span></div>
 <div class="statusline" style="margin-top:5px"><span>배치·회전·색 변경·제거가 각각 1회로 계산됩니다. (회전: 부품 다시 클릭 · 제거: 우클릭 또는 🗑 도구)</span></div>
 <div class="hint" id="hint"></div>
</div>
</div>
<script>
(()=>{
const canvas=document.getElementById('game'),ctx=canvas.getContext('2d');
const W=10,H=7,S=82,OX=40,OY=35,SPEED=8;
const COL={R:'#fb5268',G:'#42df91',B:'#5b9cff',W:'#fff0a6'};
const NAME={R:'빨강',G:'초록',B:'파랑',W:'흰색',A:'아무 색'};
const DX=[0,1,0,-1],DY=[-1,0,1,0];
const TOOLS={m1:'╱ 거울',m2:'╲ 거울',p:'◇ 프리즘',fR:'🟥 빨강 필터',fG:'🟩 초록 필터',fB:'🟦 파랑 필터',erase:'🗑 제거'};
const M=['m1','m2'],MF=['m1','m2','fR','fG','fB'],MP=['m1','m2','p'],ALL=['m1','m2','p','fR','fG','fB'];
// src:[x,y,방향(0위1오른2아래3왼),색]  goals:[x,y,색]  par=최소 부품 수, limit=par+4
const L=(name,desc,par,o)=>Object.assign({name,desc,par,limit:par+4,walls:[],abs:[]},o);
const LV=[
 L('첫 번째 빛','거울로 빛을 꺾어 흰색 목표물에 보내세요.',1,{src:[[0,3,1,'W']],goals:[[5,1,'W']],walls:[[7,3],[3,5]],allow:M}),
 L('벽 우회','고정 벽(회색)은 빛을 막습니다. 거울로 돌아가세요.',2,{src:[[0,3,1,'W']],goals:[[8,5,'W']],walls:[[4,2],[4,3],[4,4],[7,1]],abs:[[6,6]],allow:M}),
 L('색상 필터','필터는 해당 색만 통과시킵니다. 파란 목표물을 충전하세요.',2,{src:[[0,3,1,'W']],goals:[[6,0,'B']],walls:[[4,5],[2,5]],abs:[[3,1],[8,4]],allow:MF}),
 L('프리즘 입문','프리즘은 흰빛을 직진·우회전·좌회전 3갈래로 나눕니다. 색은 직진=빨강, 우회전=초록, 좌회전=파랑으로 항상 같습니다.',1,{src:[[0,3,1,'W']],goals:[[8,3,'R'],[3,6,'G'],[3,0,'B']],walls:[[6,1],[6,5]],allow:MP}),
 L('프리즘 + 거울','갈라진 세 빛을 거울로 목표물까지 유도하세요.',3,{src:[[0,3,1,'W']],goals:[[8,3,'R'],[7,6,'G'],[6,0,'B']],walls:[[5,2],[5,4]],abs:[[7,2],[6,5]],allow:MP}),
 L('세 개의 레이저','색깔 레이저 두 개와 흰 레이저 하나. 빛이 교차해도 서로 간섭하지 않습니다.',4,{src:[[0,1,1,'R'],[0,5,1,'B'],[9,3,3,'W']],goals:[[3,6,'R'],[6,1,'B'],[5,0,'G']],walls:[[1,3],[8,1]],abs:[[4,6],[2,2]],allow:MF}),
 L('흡수 장애물','파란 목표물만 색이 정해져 있고, 나머지(*)는 어떤 색이든 OK. 검은 흡수체는 빛을 삼킵니다.',3,{src:[[0,3,1,'W']],goals:[[8,1,'B'],[8,5,'A'],[4,3,'A']],walls:[[5,3],[7,3]],abs:[[6,2],[6,4]],allow:ALL}),
 L('이중 필터','흰 레이저 두 개를 각각 알맞은 색으로 걸러 보내세요.',4,{src:[[0,1,1,'W'],[9,5,3,'W']],goals:[[7,6,'R'],[5,2,'B']],walls:[[4,2],[2,4],[8,3]],abs:[[3,3],[6,3]],allow:MF}),
 L('프리즘과 레이저','프리즘 빛과 초록 레이저를 동시에 운용하세요. 초록 레이저의 길도 열어야 합니다.',5,{src:[[0,3,1,'W'],[9,5,3,'G']],goals:[[8,1,'B'],[5,0,'R'],[3,5,'G'],[1,6,'G']],walls:[[6,3],[9,3]],abs:[[6,5],[1,2]],allow:ALL}),
 L('필터 미로','흰 레이저 세 개, 필터 세 색. 색마다 알맞은 길을 만들어 주세요.',5,{src:[[0,0,2,'W'],[9,6,0,'W'],[4,0,2,'W']],goals:[[7,3,'R'],[3,2,'G'],[4,6,'B']],walls:[[2,5],[6,4]],abs:[[5,1],[5,5]],allow:ALL}),
 L('쌍둥이 프리즘','프리즘 두 개를 알맞은 위치에 놓아 모든 색을 전달하세요.',3,{src:[[0,1,1,'W'],[9,5,3,'W']],goals:[[5,3,'R'],[7,2,'G'],[7,6,'B'],[2,5,'A'],[2,0,'A']],walls:[[6,1],[8,3]],abs:[[4,5]],allow:ALL}),
 L('마스터 광학자','마지막 도전! 프리즘의 세 갈래와 초록 레이저를 모두 정확한 목표물에 전달하세요.',5,{src:[[0,3,1,'W'],[9,3,3,'G']],goals:[[8,1,'B'],[8,5,'G'],[4,0,'R'],[7,0,'G']],walls:[[5,3],[1,1],[1,5]],abs:[[6,2],[6,4]],allow:ALL})
];
// 잠금 해제: 이전 스테이지 클리어 + 누적 별 개수
const NEED=[0,0,0,0,0,0,0,0,0,12,15,18];
const KEY='lightlab_v3';
let save={stars:Array(LV.length).fill(0)};
try{const s=JSON.parse(localStorage.getItem(KEY));if(s&&Array.isArray(s.stars))s.stars.forEach((v,i)=>{if(i<LV.length)save.stars[i]=v|0});}catch(e){}
const persist=()=>{try{localStorage.setItem(KEY,JSON.stringify(save))}catch(e){}};
const total=()=>save.stars.reduce((a,b)=>a+b,0);
const isOpen=i=>i===0||(save.stars[i-1]>0&&total()>=NEED[i]);

let stage=0,tool='m1',pieces=[],moves=0,hist=[],anim=null,lit=[],won=false,stars=0,lastPerm=null;
const $=id=>document.getElementById(id);
const pos=(x,y)=>({x:OX+x*S+S/2,y:OY+y*S+S/2});
const isWall=(x,y)=>LV[stage].walls.some(w=>w[0]===x&&w[1]===y);
const isAbs=(x,y)=>LV[stage].abs.some(w=>w[0]===x&&w[1]===y);
const calc=m=>{const p=LV[stage].par;return m<=p?3:m<=p+2?2:1};
const msg=h=>{$('hint').innerHTML=h};
const PERM=['R','G','B']; // 프리즘 고정 분배: 직진=빨강, 우회전=초록, 좌회전=파랑

// ---------- 광학 시뮬레이션 ----------
function sim(perm){
 const lv=LV[stage],segs=[],hits={},seen=new Set();
 const q=lv.src.map(s=>({x:s[0],y:s[1],d:s[2],c:s[3],t:0}));
 while(q.length){
  const r=q.shift();
  for(let n=0;n<80;n++){
   const nx=r.x+DX[r.d],ny=r.y+DY[r.d];
   if(nx<0||nx>=W||ny<0||ny>=H||isWall(nx,ny))break;
   const key=nx+','+ny+','+r.d+','+r.c;if(seen.has(key))break;seen.add(key);
   segs.push({x0:r.x,y0:r.y,x1:nx,y1:ny,c:r.c,t:r.t});
   r.t++;r.x=nx;r.y=ny;
   if(isAbs(nx,ny))break;
   const gi=lv.goals.findIndex(g=>g[0]===nx&&g[1]===ny);
   if(gi>=0){const gc=lv.goals[gi][2];if((gc===r.c||(gc==='A'&&r.c!=='W'))&&(hits[gi]===undefined||hits[gi]>r.t))hits[gi]=r.t;break;}
   const p=pieces.find(p=>p.x===nx&&p.y===ny);
   if(!p)continue;
   if(p.t==='m')r.d=p.r===0?[1,0,3,2][r.d]:[3,2,1,0][r.d];
   else if(p.t==='f'){if(r.c==='W'||r.c===p.c)r.c=p.c;else break;}
   else if(p.t==='p'&&r.c==='W'){[[r.d,0],[(r.d+1)%4,1],[(r.d+3)%4,2]].forEach(([d,i])=>q.push({x:nx,y:ny,d,c:perm[i],t:r.t}));break;}
  }
 }
 return{segs,hits};
}
function startAnim(res){
 const maxT=Math.max(0,...res.segs.map(s=>s.t+1))+0.6;
 anim={res,t0:performance.now(),p:0,maxT,run:true};lit=[];won=false;update();requestAnimationFrame(loop);
}
function loop(now){
 if(!anim||!anim.run)return;
 anim.p=(now-anim.t0)/1000*SPEED;draw();
 if(anim.p>=anim.maxT)finish();else requestAnimationFrame(loop);
}
function permText(){return lastPerm?`<br>프리즘 분배 규칙 → 직진: <b style="color:${COL[lastPerm[0]]}">${NAME[lastPerm[0]]}</b> · 우회전: <b style="color:${COL[lastPerm[1]]}">${NAME[lastPerm[1]]}</b> · 좌회전: <b style="color:${COL[lastPerm[2]]}">${NAME[lastPerm[2]]}</b>`:''}
function finish(){
 const lv=LV[stage],h=anim.res.hits;anim.run=false;anim.p=1e9;
 lit=Object.keys(h).map(Number);won=lit.length===lv.goals.length;
 if(won){
  stars=calc(moves);if(stars>save.stars[stage]){save.stars[stage]=stars;persist();}
  let t=`<span class="win">🎉 스테이지 클리어! ${'★'.repeat(stars)}${'☆'.repeat(3-stars)} (이동 ${moves}회)</span>`;
  if(stars<3)t+=` · 별 3개는 ${lv.par}회 이내!`;
  if(stage===LV.length-1)t+='<br>🏆 모든 스테이지를 완료했습니다!';
  else if(!isOpen(stage+1))t+=`<br>🔒 다음 스테이지는 누적 별 ${NEED[stage+1]}개가 필요합니다 (현재 ${total()}개). 이전 스테이지를 더 적은 이동으로 다시 깨보세요.`;
  else t+='<br>다음 스테이지가 열렸습니다!';
  msg(t+permText());
 }else{
  const miss=lv.goals.filter((g,i)=>!lit.includes(i)).map(g=>NAME[g[2]]).join(', ');
  msg(`<span class="warn">충전 실패: ${miss} 목표물</span> · 빛의 색/경로를 확인하세요.`+permText());
 }
 update();draw();
}
function fire(){
 lastPerm=pieces.some(p=>p.t==='p')?PERM:null;startAnim(sim(PERM));
 msg('빛이 이동 중...'+permText());
}

// ---------- 그리기 ----------
function rr(x,y,w,h,r){ctx.beginPath();if(ctx.roundRect)ctx.roundRect(x,y,w,h,r);else ctx.rect(x,y,w,h)}
function draw(){
 const lv=LV[stage];
 ctx.clearRect(0,0,900,650);ctx.fillStyle='#0d192b';ctx.fillRect(0,0,900,650);ctx.textAlign='center';
 for(let y=0;y<H;y++)for(let x=0;x<W;x++){
  ctx.fillStyle=(x+y)%2?'#14243a':'#172941';ctx.fillRect(OX+x*S,OY+y*S,S-2,S-2);
  ctx.strokeStyle='#29415f';ctx.lineWidth=1;ctx.strokeRect(OX+x*S,OY+y*S,S-2,S-2);
 }
 lv.walls.forEach(([x,y])=>{const p=pos(x,y);ctx.fillStyle='#475569';ctx.strokeStyle='#94a3b8';ctx.lineWidth=2;rr(p.x-38,p.y-38,76,76,8);ctx.fill();ctx.stroke();
  ctx.strokeStyle='#64748b';ctx.beginPath();ctx.moveTo(p.x-38,p.y);ctx.lineTo(p.x+38,p.y);ctx.moveTo(p.x,p.y-38);ctx.lineTo(p.x,p.y);ctx.stroke();});
 lv.abs.forEach(([x,y])=>{const p=pos(x,y);ctx.save();ctx.fillStyle='#1a0b12';ctx.strokeStyle='#ef4444';ctx.lineWidth=3;ctx.setLineDash([6,5]);
  ctx.beginPath();ctx.arc(p.x,p.y,31,0,7);ctx.fill();ctx.stroke();ctx.setLineDash([]);ctx.strokeStyle='#ef4444aa';ctx.lineWidth=4;
  ctx.beginPath();ctx.moveTo(p.x-12,p.y-12);ctx.lineTo(p.x+12,p.y+12);ctx.moveTo(p.x+12,p.y-12);ctx.lineTo(p.x-12,p.y+12);ctx.stroke();ctx.restore();});
 lv.src.forEach(([x,y,d,c])=>{const p=pos(x,y);ctx.save();ctx.shadowColor=COL[c];ctx.shadowBlur=18;ctx.fillStyle=COL[c];
  ctx.beginPath();ctx.arc(p.x,p.y,15,0,7);ctx.fill();ctx.restore();
  ctx.save();ctx.translate(p.x,p.y);ctx.rotate(d*Math.PI/2);ctx.fillStyle='#0b1220';ctx.beginPath();ctx.moveTo(0,-9);ctx.lineTo(7,4);ctx.lineTo(-7,4);ctx.fill();ctx.restore();
  ctx.fillStyle='#fff';ctx.font='bold 11px sans-serif';ctx.fillText('LASER',p.x,p.y+31);});
 lv.goals.forEach(([x,y,gc],i)=>{
  const p=pos(x,y),on=anim&&anim.res.hits[i]!==undefined&&anim.p>=anim.res.hits[i],color=gc==='A'?'#cbd5e1':COL[gc];
  ctx.save();ctx.shadowColor=color;ctx.shadowBlur=on?26:9;ctx.fillStyle=on?color+'66':'#10243a';ctx.strokeStyle=color;ctx.lineWidth=4;
  ctx.beginPath();ctx.arc(p.x,p.y,25,0,7);ctx.fill();ctx.stroke();
  ctx.fillStyle=on?'#fff':color;ctx.font='bold 15px sans-serif';ctx.fillText(gc==='A'?'*':gc,p.x,p.y+5);
  ctx.font='10px sans-serif';ctx.fillText(on?'FULL':'GOAL',p.x,p.y+39);ctx.restore();});
 pieces.forEach(p=>{
  const q=pos(p.x,p.y);ctx.save();ctx.translate(q.x,q.y);ctx.lineCap='round';
  if(p.t==='m'){ctx.lineWidth=7;ctx.strokeStyle='#e2e8f0';ctx.shadowColor='#93c5fd';ctx.shadowBlur=9;ctx.beginPath();
   if(p.r===0){ctx.moveTo(-23,23);ctx.lineTo(23,-23)}else{ctx.moveTo(-23,-23);ctx.lineTo(23,23)}ctx.stroke();}
  else if(p.t==='f'){ctx.fillStyle=COL[p.c]+'66';ctx.strokeStyle=COL[p.c];ctx.lineWidth=3;ctx.shadowColor=COL[p.c];ctx.shadowBlur=10;rr(-22,-28,44,56,6);ctx.fill();ctx.stroke();
   ctx.shadowBlur=0;ctx.fillStyle='#fff';ctx.font='bold 14px sans-serif';ctx.fillText(p.c,0,5);}
  else{ctx.fillStyle='#5eead4';ctx.strokeStyle='#a5f3fc';ctx.lineWidth=3;ctx.shadowColor='#22d3ee';ctx.shadowBlur=10;
   ctx.beginPath();ctx.moveTo(0,-27);ctx.lineTo(25,22);ctx.lineTo(-25,22);ctx.closePath();ctx.fill();ctx.stroke();
   ctx.shadowBlur=0;ctx.fillStyle='#083344';ctx.font='bold 13px sans-serif';ctx.fillText('RGB',0,10);}
  ctx.restore();});
 if(anim)anim.res.segs.forEach(s=>{
  const f=Math.max(0,Math.min(1,anim.p-s.t));if(f<=0)return;
  const a=pos(s.x0,s.y0),b=pos(s.x1,s.y1),ex=a.x+(b.x-a.x)*f,ey=a.y+(b.y-a.y)*f;
  ctx.save();ctx.strokeStyle=COL[s.c];ctx.lineWidth=4;ctx.lineCap='round';ctx.shadowColor=COL[s.c];ctx.shadowBlur=12;
  ctx.beginPath();ctx.moveTo(a.x,a.y);ctx.lineTo(ex,ey);ctx.stroke();
  if(f<1){ctx.fillStyle='#fff';ctx.beginPath();ctx.arc(ex,ey,6,0,7);ctx.fill();}ctx.restore();});
 if(won){ctx.fillStyle='#86efac';ctx.font='bold 26px sans-serif';ctx.fillText('STAGE CLEAR '+'★'.repeat(stars)+'☆'.repeat(3-stars),450,26);}
}

// ---------- UI ----------
function update(){
 const lv=LV[stage],n=lit.length,pct=Math.round(n/lv.goals.length*100);
 $('levelTitle').textContent=`STAGE ${String(stage+1).padStart(2,'0')} · ${lv.name}`;
 $('levelDesc').textContent=lv.desc;$('stageCount').textContent=`${stage+1} / ${LV.length}`;
 $('pct').textContent=pct+'%';$('fill').style.width=pct+'%';
 $('prev').disabled=stage===0;$('next').disabled=stage>=LV.length-1||!isOpen(stage+1);
 $('goals').innerHTML=lv.goals.map((g,i)=>`<span class="goalchip ${lit.includes(i)?'done':''}">${lit.includes(i)?'✓':'○'} ${NAME[g[2]]} 목표물</span>`).join('');
 $('moves').textContent=`${moves} / ${lv.limit} (남은 ${lv.limit-moves})`;
 $('par').textContent=`★★★ ≤${lv.par}회 · ★★ ≤${lv.par+2}회 · ★ ≤${lv.limit}회`;
 $('undo').disabled=!hist.length;
 $('menu').innerHTML=LV.map((l,i)=>{const s=save.stars[i],o=isOpen(i);
  return `<button class="stg ${i===stage?'selected':''}" data-i="${i}" ${o?'':'disabled'}>${o?i+1:'🔒'}<br><small>${'★'.repeat(s)}${'☆'.repeat(3-s)}</small></button>`}).join('');
 const lk=LV.findIndex((l,i)=>!isOpen(i));
 $('lockinfo').textContent=`⭐ 누적 별 ${total()} / ${LV.length*3}`+(lk<0?' · 모든 스테이지 해금!':` · 🔒 STAGE ${lk+1}: ${save.stars[lk-1]>0?`누적 별 ${NEED[lk]}개 필요`:'이전 스테이지 클리어 필요'}`);
}
function buildTools(){
 const al=LV[stage].allow.concat(['erase']);if(!al.includes(tool))tool=al[0];
 $('tools').innerHTML=al.map(t=>`<button data-t="${t}" class="${t===tool?'selected':''}">${TOOLS[t]}</button>`).join('');
}
function reset(){pieces=[];moves=0;hist=[];anim=null;lit=[];won=false;lastPerm=null;update();draw();
 msg('부품을 배치하고 빛을 발사하세요. 이동 횟수를 아낄수록 별이 많아집니다.');}
function changeStage(n){if(n<0||n>=LV.length||!isOpen(n))return;stage=n;buildTools();reset();}
function clearResult(){anim=null;lit=[];won=false;}
function act(mut){
 const lv=LV[stage];
 if(moves>=lv.limit){msg('<span class="warn">이동 횟수를 모두 사용했습니다. 되돌리기(↶) 또는 초기화(↺)를 사용하세요.</span>');return;}
 hist.push(JSON.stringify({pieces,moves}));mut();moves++;clearResult();update();draw();
 msg('부품을 배치하고 빛을 발사하세요.');
}
function undo(){if(!hist.length)return;const s=JSON.parse(hist.pop());pieces=s.pieces;moves=s.moves;clearResult();update();draw();}
const make=(t,x,y)=>t==='m1'?{x,y,t:'m',r:0}:t==='m2'?{x,y,t:'m',r:1}:t==='p'?{x,y,t:'p'}:{x,y,t:'f',c:t[1]};
function clickCell(e){
 const lv=LV[stage],rect=canvas.getBoundingClientRect();
 const x=(e.clientX-rect.left)*canvas.width/rect.width,y=(e.clientY-rect.top)*canvas.height/rect.height;
 const gx=Math.floor((x-OX)/S),gy=Math.floor((y-OY)/S);
 if(gx<0||gx>=W||gy<0||gy>=H||isWall(gx,gy)||isAbs(gx,gy)||lv.src.some(s=>s[0]===gx&&s[1]===gy)||lv.goals.some(g=>g[0]===gx&&g[1]===gy))return;
 const p=pieces.find(q=>q.x===gx&&q.y===gy);
 if(e.button===2||tool==='erase'){if(p)act(()=>{pieces=pieces.filter(q=>q!==p)});return;}
 if(p){if(p.t==='m')act(()=>{p.r^=1});else if(p.t==='f')act(()=>{p.c={R:'G',G:'B',B:'R'}[p.c]});return;}
 act(()=>{pieces.push(make(tool,gx,gy))});
}
$('tools').onclick=e=>{const t=e.target.closest('button');if(!t)return;tool=t.dataset.t;buildTools();};
$('menu').onclick=e=>{const b=e.target.closest('button');if(b&&!b.disabled)changeStage(+b.dataset.i);};
$('fire').onclick=fire;$('undo').onclick=undo;$('reset').onclick=reset;
$('prev').onclick=()=>changeStage(stage-1);$('next').onclick=()=>changeStage(stage+1);
canvas.addEventListener('click',clickCell);
canvas.addEventListener('contextmenu',e=>{e.preventDefault();clickCell(e);});
buildTools();reset();
})();
</script></body></html>
"""

components.html(html, height=1350, scrolling=True)
st.caption(
    "프리즘은 흰빛만 3갈래로 나누며, 입사 방향 기준 직진=빨강, 우회전=초록, 좌회전=파랑으로 항상 고정입니다. "
    "필터는 같은 색(또는 흰빛)만 통과시키고, 검은 흡수체와 회색 벽은 빛을 막습니다. "
    "진행 상황(별 개수)은 브라우저에 저장됩니다."
)
