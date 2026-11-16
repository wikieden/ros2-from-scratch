// ros2 专题通用"分步示意图"动画：只填数据就能出一页动画。
// 依赖 anim.js（el / txt / $ / setupPlayer）。
// 用法：STEPPER({
//   h: 图区高度（默认 300）, term: true/false 是否带终端框,
//   boxes: {id: [x, y, w, h, 标题, 小字 或 [小字...], 颜色变量名]},
//   arrows: {id: [x1, y1, x2, y2, 标签, 颜色变量名, 'dash'?]},
//   steps: [{n: 时间轴短名, on: [id...], c: [三行说明], chip: [arrowId, 文字, 位置0-1], term: [终端行], set: {boxId: 新标题}}]
// })
function STEPPER(cfg){
  const sv=$('sv');const H=cfg.h||300;const TERM=cfg.term?130:0;
  const total=H+TERM+(TERM?14:0)+120;
  sv.setAttribute('viewBox',`0 0 680 ${total}`);
  const defs=el('defs',{},sv);
  const COLS=['accent','purple','teal','amber','warm','muted','good','bad','text'];
  COLS.forEach(c=>{const m=el('marker',{id:'ah-'+c,viewBox:'0 0 10 10',refX:9,refY:5,markerWidth:9,markerHeight:9,markerUnits:'userSpaceOnUse',orient:'auto-start-reverse'},defs);el('path',{d:'M0 0 L10 5 L0 10 z',fill:`var(--${c})`},m)});
  const B={},A={};
  for(const id in cfg.arrows){
    const [x1,y1,x2,y2,label,col='muted',dash]=cfg.arrows[id];
    const g=el('g',{},sv);
    const p=el('path',{d:`M${x1} ${y1} L${x2} ${y2}`,stroke:`var(--${col})`,'stroke-width':1.6,fill:'none','marker-end':`url(#ah-${col})`},g);
    if(dash)p.setAttribute('stroke-dasharray','5 4');
    let lt=null;
    if(label){const mx=(x1+x2)/2,my=(y1+y2)/2;const vert=Math.abs(x2-x1)<Math.abs(y2-y1);
      lt=txt(label,{x:vert?mx+6:mx,y:vert?my+4:my-6,'text-anchor':vert?'start':'middle',class:'m'},g);}
    A[id]={g,p,x1,y1,x2,y2,col};
  }
  for(const id in cfg.boxes){
    const [x,y,w,h,title,sub,col='line']=cfg.boxes[id];
    const g=el('g',{},sv);
    const r=el('rect',{x,y,width:w,height:h,rx:8,fill:'var(--bg)',stroke:`var(--${col})`,'stroke-width':1.2},g);
    const subs=sub?(Array.isArray(sub)?sub:[sub]):[];
    const ty=y+h/2-(subs.length*8)+5;
    const t=txt(title,{x:x+w/2,y:ty,'text-anchor':'middle'},g);
    subs.forEach((s,i)=>txt(s,{x:x+w/2,y:ty+17+i*16,'text-anchor':'middle',class:'m'},g));
    B[id]={g,r,t,title};
  }
  const chip=el('g',{opacity:0},sv);
  const chipR=el('rect',{x:0,y:-11,width:10,height:22,rx:11,fill:'var(--warm)'},chip);
  const chipT=txt('',{x:10,y:4,style:'fill:#fff;font-size:11px'},chip);
  let term=[];
  if(TERM){el('rect',{x:20,y:H+6,width:640,height:TERM,rx:8,fill:'#1f1e1d'},sv);
    term=[0,1,2,3,4,5].map(i=>txt('',{x:32,y:H+28+i*18,style:'fill:#e8e6dd;white-space:pre;font-family:Menlo,Consolas,monospace;font-size:11.5px'},sv));}
  const cy=H+TERM+(TERM?14:0)+20;
  const cap=[0,1,2].map(i=>txt('',{x:20,y:cy+i*21,class:i?'m':''},sv));
  const N=cfg.steps.length-1;const tw=640/N;
  const tl=cfg.steps.slice(1).map((s,i)=>{const x=20+i*tw;const r=el('rect',{x,y:cy+70,width:tw-4,height:22,rx:5,fill:'var(--bg)',stroke:'var(--line)'},sv);txt(s.n||String(i+1),{x:x+(tw-4)/2,y:cy+85,'text-anchor':'middle',class:'m'},sv);return r});
  let k;
  function draw(){
    const s=cfg.steps[k];const on=s.on||[];const any=on.length>0&&!s.all;
    for(const id in B){const b=B[id];const hit=s.all||on.includes(id);b.r.setAttribute('stroke-width',hit&&any?2.6:1.2);b.r.setAttribute('fill',hit&&any?'var(--card)':'var(--bg)');b.g.setAttribute('opacity',!any||hit?1:.4);b.t.textContent=(s.set&&s.set[id])||b.title}
    for(const id in A){const a=A[id];const hit=s.all||on.includes(id);a.p.setAttribute('stroke-width',hit&&any?3:1.6);a.g.setAttribute('opacity',!any||hit?1:.3)}
    if(s.chip){const [aid,t,f=.5]=s.chip;const a=A[aid];const x=a.x1+(a.x2-a.x1)*f,y=a.y1+(a.y2-a.y1)*f;
      const w=[...t].reduce((q,ch)=>q+(ch.charCodeAt(0)>255?12:6.6),0)+20;chipR.setAttribute('width',w);chipR.setAttribute('fill',`var(--${a.col==='muted'?'warm':a.col})`);chipT.textContent=t;
      chip.setAttribute('transform',`translate(${x-w/2},${y})`);chip.setAttribute('opacity',1)}else chip.setAttribute('opacity',0);
    term.forEach((t,i)=>{const l=(s.term||[])[i]||'';t.textContent=l;t.style.fill=l.startsWith('$')?'#9fe1cb':'#e8e6dd'});
    cap.forEach((c,i)=>c.textContent=(s.c||[])[i]||'');
    tl.forEach((r,i)=>{const cur=i===k-1;r.setAttribute('fill',cur?'var(--accent-bg)':(i<k-1?'var(--card)':'var(--bg)'));r.setAttribute('stroke',cur?'var(--accent)':'var(--line)')});
  }
  const AN={captureSeed:1,reset(){k=0;draw()},next(){if(k>=N)return false;k++;draw();return true}};
  setupPlayer(AN,cfg.ms||2200);
}
