'use strict';
const $=s=>document.querySelector(s), $$=s=>[...document.querySelectorAll(s)];
const fmt=(n,p=2)=>Number(n).toLocaleString('en-US',{minimumFractionDigits:p,maximumFractionDigits:p});
const svgNS='http://www.w3.org/2000/svg';
function el(name,attrs={},text){const e=document.createElementNS(svgNS,name);for(const [k,v]of Object.entries(attrs))e.setAttribute(k,v);if(text!==undefined)e.textContent=text;return e;}
function label(x,y,t,anchor='start'){return el('text',{x,y,'text-anchor':anchor},t);}
function set(name,n,p=2){const e=$(`[data-value="${name}"]`);if(e)e.textContent=fmt(n,p);}
function requests(d){const svg=$('#request-chart'),rows=d.gsm8k.per_request,mean=d.gsm8k.summary.mean_tok_per_s,w=Math.max(300,svg.clientWidth),h=170,left=8,right=38,top=14,bottom=15,max=Math.ceil(Math.max(...rows.map(r=>r.tok_per_s))/50)*50,step=(w-left-right)/rows.length;
 svg.setAttribute('viewBox',`0 0 ${w} ${h}`);
 const y=v=>h-bottom-v/max*(h-top-bottom);svg.replaceChildren();
 for(const value of [0,100,200]){if(value>max)continue;svg.append(el('line',{x1:left,x2:w-right,y1:y(value),y2:y(value),stroke:'#e3e5dc'}),label(w-right+8,y(value)+3,value));}
 rows.forEach((r,i)=>{const bar=el('rect',{x:left+i*step,y:y(r.tok_per_s),width:Math.max(2,step-4),height:h-bottom-y(r.tok_per_s),rx:1,fill:r.finish_reason==='length'?'#94600d':'#2c45d9'});bar.append(el('title',{},`Request ${i+1}: ${fmt(r.tok_per_s)} tok/s; ${r.finish_reason==='length'?'token cap':'completed'}`));svg.append(bar);});
 svg.append(el('line',{x1:left,x2:w-right,y1:y(mean),y2:y(mean),stroke:'#20221f','stroke-dasharray':'3 4','stroke-width':1}));
}
function storage(d){const colors=['#2c45d9','#7787df','#b8c0e4'];const items=[...d.storage.models,{name:'Docker image',bytes:d.storage.image_bytes}];const total=items.reduce((a,r)=>a+r.bytes,0);$('#total-storage').textContent=fmt(total/1e9);items.forEach((r,i)=>{const segment=document.createElement('span');segment.style.cssText=`width:${r.bytes/total*100}%;background:${colors[i]}`;segment.title=`${r.name}: ${fmt(r.bytes/1e9)} GB`;$('#storage-track').append(segment);const row=document.createElement('div');row.className='storage-item';const dot=document.createElement('i');dot.style.background=colors[i];const name=document.createElement('strong');name.textContent=r.name;const size=document.createElement('span');size.textContent=`${fmt(r.bytes/1e9)} GB`;row.append(dot,name,size);$('#storage-rows').append(row);const exact=document.createElement('div');exact.className='exact-item';exact.textContent=`${r.name}: ${fmt(r.bytes,0)} logical/reported bytes${r.allocated_bytes?`; ${fmt(r.allocated_bytes,0)} allocated bytes; ${r.files} files`:''}.`;$('#exact-storage').append(exact);});}
function quality(d){const q=d.q200;for(let i=0;i<q.total_count;i++){const e=document.createElement('i');if(i>=q.correct_count)e.className='failed';$('#quality-matrix').append(e);}for(const [key,name]of [['gsm8k','GSM8K'],['humaneval','HumanEval'],['ifeval','IFEval'],['hard_reasoning','Hard reasoning']]){const f=q.families[key],tr=document.createElement('tr');for(const txt of [name,`${f.correct} / ${f.n}`,`${fmt(f.accuracy_pct,f.accuracy_pct%1?2:0)}%`]){const td=document.createElement('td');td.textContent=txt;tr.append(td);}$('#family-results').append(tr);}}
let traceData=[],activeMetric='power';
const traceSettings={power:{label:'GPU power',unit:'W',max:400,step:100},vram:{label:'GPU memory',unit:'GiB',max:24,step:6},temperature:{label:'GPU temperature',unit:'°C',max:80,step:20}};
function trace(metric){activeMetric=metric;const svg=$('#trace-chart'),c=traceSettings[metric],w=Math.max(280,svg.clientWidth),h=w<600?235:280,l=36,r=12,t=22,b=32,plotW=w-l-r,plotH=h-t-b,last=traceData.at(-1).s;svg.replaceChildren();svg.setAttribute('viewBox',`0 0 ${w} ${h}`);svg.setAttribute('aria-label',`${c.label} during the primary suite: ${traceData.length} recorded samples`);const x=s=>l+s/last*plotW,y=v=>h-b-v/c.max*plotH;
 for(let v=0;v<=c.max;v+=c.step){svg.append(el('line',{x1:l,x2:w-r,y1:y(v),y2:y(v),stroke:'#e3e5dc'}),label(l-10,y(v)+4,v,'end'));}
 for(let minute=0;minute<=Math.floor(last/60);minute+=(w<600?10:5))svg.append(label(x(minute*60),h-7,minute,'middle'));
 svg.append(label(l,12,c.unit));
 const path=traceData.map((row,i)=>`${i?'L':'M'}${x(row.s).toFixed(2)},${y(row[metric]).toFixed(2)}`).join(' ');
 svg.append(el('path',{d:path+` L${x(last)},${h-b} L${l},${h-b} Z`,fill:'#2c45d9','fill-opacity':'.045'}),el('path',{d:path,class:'trace-line'}));
 const marker=el('g',{visibility:'hidden',id:'trace-marker'}),line=el('line',{x1:0,x2:0,y1:t,y2:h-b,stroke:'#60635e','stroke-dasharray':'3 4'}),dot=el('circle',{r:4,fill:'#2c45d9',stroke:'#fff','stroke-width':2});marker.append(line,dot);svg.append(marker);
 svg.onpointermove=e=>{const box=svg.getBoundingClientRect(),px=(e.clientX-box.left)/box.width*w,second=Math.max(0,Math.min(last,(px-l)/plotW*last));let lo=0,hi=traceData.length-1;while(lo<hi){const mid=(lo+hi)>>1;if(traceData[mid].s<second)lo=mid+1;else hi=mid;}const row=traceData[lo],xp=x(row.s);line.setAttribute('x1',xp);line.setAttribute('x2',xp);dot.setAttribute('cx',xp);dot.setAttribute('cy',y(row[metric]));marker.setAttribute('visibility','visible');$('#trace-readout').textContent=`${fmt(row.s/60,1)} min · ${fmt(row[metric],metric==='temperature'?0:2)} ${c.unit}`;};
 svg.onpointerleave=()=>{marker.setAttribute('visibility','hidden');$('#trace-readout').textContent=`${c.label} · primary suite`};
 $('#trace-readout').textContent=`${c.label} · primary suite`;
 $$('[data-trace]').forEach(b=>b.setAttribute('aria-pressed',String(b.dataset.trace===metric)));
}
async function init(){try{const res=await fetch('data.json');if(!res.ok)throw Error(`HTTP ${res.status}`);const d=await res.json();window.reportData=d;
 set('speed',d.gsm8k.summary.mean_tok_per_s,1);set('al',d.gsm8k.summary.mean_acceptance_length);set('ttft',d.mixed.summary.median_ttft_s*1000,0);set('mixed',d.mixed.summary.aggregate_tps);set('tokens',d.mixed.summary.tokens,0);set('q200speed',d.q200_throughput.aggregate_e2e_tps);set('longspeed',d.long_context.decode_tok_per_s);set('prefill',d.long_context.prefill_tok_per_s);set('n2',d.niah[0].predicted_per_second);set('n3',d.niah[1].predicted_per_second);
 requests(d);storage(d);quality(d);traceData=d.trace;trace('power');$('#trace-count').textContent=`${fmt(traceData.length,0)} samples · ${fmt(traceData.at(-1).s/60,1)} minutes`;
 $$('[data-trace]').forEach(b=>b.addEventListener('click',()=>trace(b.dataset.trace)));
 $('#snapshot-date').textContent=`Storage & runtime snapshot: ${new Date(d.updated_at).toLocaleDateString('en-US',{year:'numeric',month:'long',day:'numeric',timeZone:'UTC'})}.`;
 let resizeTimer;window.addEventListener('resize',()=>{clearTimeout(resizeTimer);resizeTimer=setTimeout(()=>{requests(d);trace(activeMetric);},80);});
 document.documentElement.dataset.ready='true';
 }catch(e){const note=document.createElement('p');note.className='error';note.setAttribute('role','alert');note.textContent=`Chart data could not load (${e.message}). Use the linked frozen evidence for results.`;$('#main').prepend(note);document.documentElement.dataset.ready='error';}}
$('#copy-command').addEventListener('click',async()=>{try{await navigator.clipboard.writeText($('#launch').textContent);$('#copy-feedback').textContent='Command copied.';}catch{$('#copy-feedback').textContent='Select and copy the command above; clipboard access is unavailable.';}});
init();
