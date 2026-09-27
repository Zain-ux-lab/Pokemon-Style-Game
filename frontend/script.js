/* Local visual prototype only. The multiplayer server will own real match state. */
const TYPES = { Magic: '#6a64a2', Physical: '#9c633b', Spirit: '#3c827c' };
const STRONG = { Magic: 'Physical', Physical: 'Spirit', Spirit: 'Magic' };
const DEFINITIONS = [
  {name:'Mage',type:'Magic',maxHp:100,moves:[
    {name:'Arcane Bolt',symbol:'✦',power:22,description:'A steady bolt of magic. Reliable damage, with no cost.'},
    {name:'Gather Power',symbol:'◎',power:0,effect:'charge',description:'Prepare a charge for Starfall. The charge clears when you switch.'},
    {name:'Starfall',symbol:'✧',power:48,effect:'burst',description:'Spend your charge to unleash a powerful spell.'}]},
  {name:'Sporestag',type:'Physical',maxHp:120,moves:[
    {name:'Horn Jab',symbol:'◆',power:20,description:'A direct strike with a sturdy branching horn.'},
    {name:'Shell Brace',symbol:'◈',power:0,effect:'brace',description:'Halve damage during the next enemy turn. Prepare +12 damage for your next jab or burst.'},
    {name:'Spore Burst',symbol:'✳',power:18,description:'A burst of spores. Uses your prepared shell bonus, just like Horn Jab.'}]},
  {name:'Glowmire',type:'Spirit',maxHp:90,moves:[
    {name:'Ember Beam',symbol:'✦',power:21,description:'Send a focused beam of lantern light at the opponent.'},
    {name:'Overburn',symbol:'◉',power:38,effect:'burn',description:'Spend 12 HP to deal heavy damage. Cannot knock yourself out.'},
    {name:'Siphon Light',symbol:'◇',power:13,effect:'heal',description:'Deal light damage and recover up to 10 HP.'}]}
];
function sprite(name){
 const shapes = name==='Mage' ? '<path fill="#394d65" d="M15 28h34l8 30H9z"/><path fill="#526e86" d="M22 28h20l7 26H16z"/><path fill="#e4c9a0" d="M24 17h16v17H24z"/><path fill="#e6e0cf" d="M22 27h21v8h-4v7h-5v5h-6v-6h-4z"/><path fill="#344b63" d="M13 18h38v6H13zM23 10h20v9H23zM28 3h10v9H28zM33 0h5v4h-5z"/><path fill="#bea16b" d="M20 17h25v3H20z"/><path fill="#27353c" d="M13 56h14v5H13zM36 56h15v5H36z"/><path fill="#a07143" d="M51 22h3v32h-3z"/><path fill="#9fdbcd" d="M49 17h7v7h-7z"/><path fill="#313c41" d="M27 24h3v3h-3zM36 24h3v3h-3z"/>' : name==='Sporestag' ? '<path fill="#455742" d="M8 45h8v13H8zM22 46h7v14h-7zM39 46h7v14h-7zM51 43h7v15h-7z"/><path fill="#7f9152" d="M8 26h46v25H8zM16 19h29v9H16z"/><path fill="#a4ad66" d="M18 23h25v20H18z"/><path fill="#576b48" d="M33 23h5v27h-5z"/><path fill="#64704b" d="M4 34h18v16H4z"/><path fill="#d6c39a" d="M7 19h5v18H7zM2 16h5v8H2zM11 14h5v10h-5z"/><path fill="#e6dec1" d="M24 11h4v12h-4zM42 17h4v10h-4z"/><path fill="#bd7754" d="M17 8h18v7H17zM21 4h10v5H21zM37 15h16v6H37z"/><path fill="#e8c095" d="M21 8h4v3h-4zM28 9h4v3h-4zM41 16h4v3h-4z"/><path fill="#182e2b" d="M7 36h4v4H7z"/>' : '<path fill="#8cb9af" d="M20 54h24v4H20zM25 59h13v3H25z"/><path fill="#415d60" d="M19 17h26v36H19zM15 21h34v5H15zM15 47h34v6H15zM24 7h16v12H24z"/><path fill="#98b9a3" d="M28 10h8v7h-8z"/><path fill="#dbb670" d="M23 25h18v21H23z"/><path fill="#f6d994" d="M27 28h10v14H27z"/><path fill="#fff1bd" d="M30 30h5v8h-5z"/><path fill="#314b51" d="M29 22h4v26h-4zM19 34h25v3H19z"/><path fill="#bad7c4" d="M9 28h5v13H9zM50 26h5v13h-5z"/>';
 return `<svg class="sprite" viewBox="0 0 64 64" shape-rendering="crispEdges" role="img" aria-label="${name} placeholder artwork"><ellipse cx="32" cy="61" rx="24" ry="2" fill="#263d3320"/>${shapes}</svg>`;
}
let state;
const $=id=>document.getElementById(id);
function reset(){state={teams:[0,1].map(()=>DEFINITIONS.map(d=>({...d,hp:d.maxHp,charge:false,guard:false,ready:false}))),active:[0,1],player:0,turn:1,replacement:null,winner:null};$('log').replaceChildren();if($('switch-dialog').open)$('switch-dialog').close();log('Teams revealed. Player 1 opens the battle.');render();}
function current(p=state.player){return state.teams[p][state.active[p]];}
function unavailable(move,c=current()){if(move.effect==='burst'&&!c.charge)return 'Requires a charge';if(move.effect==='charge'&&c.charge)return 'Already charged';if(move.effect==='burn'&&c.hp<=12)return 'Requires more than 12 HP';return '';}
function damage(move,c=current(),target=current(1-state.player)){if(!move.power)return 0;return Math.max(0,Math.floor((move.power+(c.ready?12:0))*(STRONG[c.type]===target.type?1.25:1)*(target.guard?.5:1)));}
function log(text){const li=document.createElement('li');li.textContent=text;$('log').append(li);$('log').scrollTop=$('log').scrollHeight;}
function preview(index){const c=current(),m=c.moves[index],n=damage(m),reason=unavailable(m);$('details').style.setProperty('--type',TYPES[c.type]);$('details').innerHTML=`<div class="detail-kicker">${c.type} / ${m.power?'Attack':'Preparation'}</div><h3>${m.name}</h3><p>${m.description}</p>${m.power?`<div class="damage">${n}<small>damage${STRONG[c.type]===current(1-state.player).type?' · type advantage':''}</small></div>`:'<div class="damage">Prepare<small>Uses this turn</small></div>'}${reason?`<div class="requirement">${reason}</div>`:''}`;}
function render(){
 hideDetails();
 for(let side=0;side<2;side++){const p=side===0?state.player:1-state.player,c=current(p);$(`hud-${side}`).style.setProperty('--type',TYPES[c.type]);$(`hud-${side}`).innerHTML=`<div class="side-label">${side===0?'YOU':'OPPONENT'} <span>PLAYER ${p+1}</span></div><div class="hud-top"><strong>${c.name}</strong><span class="type">${c.type.toUpperCase()}</span></div><div class="health" role="meter" aria-label="${side===0?'Your':'Opponent'} health" aria-valuemin="0" aria-valuemax="${c.maxHp}" aria-valuenow="${c.hp}"><span style="width:${c.hp/c.maxHp*100}%"></span></div><div class="hp"><span>${c.hp} / ${c.maxHp} HP</span><span>${[c.charge?'Charged':'',c.guard?'Guarded':'',c.ready?'Prepared':''].filter(Boolean).join(' · ')}</span></div>`;$(`fighter-${side}`).innerHTML=sprite(c.name);$(`fighter-${side}`).classList.toggle('fainted',c.hp===0);}
 $('enemy-roster').innerHTML=state.teams[1-state.player].map((c,i)=>`<div class="portrait enemy-portrait ${state.active[1-state.player]===i?'active':''} ${c.hp===0?'knocked-out':''}" aria-label="${c.name}, ${c.hp} of ${c.maxHp} health${state.active[1-state.player]===i?', active':''}">${sprite(c.name)}<small>${c.name}</small><div class="health"><span style="width:${c.hp/c.maxHp*100}%"></span></div></div>`).join('');
 $('turn').textContent=state.winner!==null?`PLAYER ${state.winner+1} WINS`:state.replacement!==null?`PLAYER ${state.replacement+1} · DEPLOY`:`PLAYER ${state.player+1}'S TURN`;
 $('team-label').textContent=`YOUR TEAM · P${state.player+1}`;$('turn-count').textContent=`TURN ${state.turn}`;
 $('roster').innerHTML=state.teams[state.player].map((c,i)=>`<button class="portrait ${state.active[state.player]===i?'active':''}" aria-label="${c.name}, ${c.hp} of ${c.maxHp} health${state.active[state.player]===i?', active':''}" ${c.hp===0||i===state.active[state.player]||state.winner!==null?'disabled':''} data-slot="${i}">${sprite(c.name)}<small>${c.name}</small><div class="health"><span style="width:${c.hp/c.maxHp*100}%"></span></div></button>`).join('');
 $('roster').querySelectorAll('button').forEach(b=>b.onclick=()=>openSwitch(Number(b.dataset.slot)));
 const c=current();$('moves').innerHTML=c.moves.map((m,i)=>`<button class="move ${unavailable(m)?'unavailable':''}" style="--type:${TYPES[c.type]}" aria-disabled="${!!unavailable(m)}" ${state.winner!==null||state.replacement!==null?'disabled':''} data-move="${i}"><span class="move-symbol">${m.symbol}</span>${m.name}</button>`).join('');
 $('moves').querySelectorAll('button').forEach(b=>{const i=Number(b.dataset.move);b.onmouseenter=()=>showDetails(i,b);b.onfocus=()=>showDetails(i,b);b.onmouseleave=scheduleHideDetails;b.onblur=scheduleHideDetails;b.onclick=()=>act(i);});
 $('switch').disabled=state.winner!==null;$('switch').innerHTML=state.replacement!==null?'⇄ Deploy replacement <span>Free replacement</span>':'⇄ Switch character <span>Uses your turn</span>';
 preview(0);if(state.winner!==null){$('details').innerHTML=`<div class="detail-kicker">MATCH COMPLETE</div><h3>Player ${state.winner+1} wins</h3><p>All three opposing characters are knocked out. Start a new battle to play again.</p>`;}
}
let detailTimer;
function hideDetails(){clearTimeout(detailTimer);document.querySelector('.detail-panel').classList.remove('is-visible');document.querySelectorAll('[aria-describedby="details"]').forEach(b=>b.removeAttribute('aria-describedby'));}
function scheduleHideDetails(){clearTimeout(detailTimer);detailTimer=setTimeout(()=>{if(!document.querySelector('.detail-panel:hover')&&!document.querySelector('.move:hover')&&!document.querySelector('.move:focus-visible'))hideDetails();},120);}
function showDetails(i,button){clearTimeout(detailTimer);preview(i);const panel=document.querySelector('.detail-panel');panel.classList.add('is-visible');button.setAttribute('aria-describedby','details');const r=button.getBoundingClientRect(),size=panel.offsetWidth;panel.style.left=Math.max(8,r.left-size-14)+'px';panel.style.top=Math.max(8,Math.min(innerHeight-size-8,r.top+r.height/2-size/2))+'px';}
const detailPanel=document.querySelector('.detail-panel');
detailPanel.onmouseenter=()=>clearTimeout(detailTimer);detailPanel.onmouseleave=scheduleHideDetails;
document.addEventListener('keydown',e=>{if(e.key==='Escape')hideDetails();});
window.addEventListener('resize',hideDetails);
function act(i){if(state.winner!==null||state.replacement!==null)return;const p=state.player,c=current(),target=current(1-p),m=c.moves[i];if(unavailable(m)){preview(i);return;}hideDetails();const dealt=damage(m),before=target.hp;
 if(m.power){target.hp=Math.max(0,target.hp-dealt);c.ready=false;}
 if(m.effect==='charge')c.charge=true;if(m.effect==='burst')c.charge=false;if(m.effect==='brace'){c.guard=true;c.ready=true;}if(m.effect==='burn')c.hp-=12;if(m.effect==='heal')c.hp=Math.min(c.maxHp,c.hp+10);
 target.guard=false;log(`P${p+1} · ${c.name} used ${m.name}${m.power?` — ${before-target.hp} damage.`:'.'}`);
 state.player=1-p;state.turn++;
 if(target.hp===0){if(state.teams[1-p].every(c=>c.hp===0)){state.winner=p;log(`Player ${p+1} wins the match!`);}else{state.replacement=1-p;log(`${target.name} is knocked out. Choose a free replacement.`);}}
 render();if(state.replacement!==null)openSwitch();
}
function openSwitch(preferred){if(state.winner!==null)return;const forced=state.replacement!==null;$('switch-title').textContent=forced?'Deploy a replacement':'Switch your character?';$('switch-description').textContent=forced?'Your replacement is free. You still get your normal action.':'Switching ends your turn. Charges, protection, and prepared bonuses are cleared.';$('switch-dialog').querySelector('.close').hidden=forced;
 $('switch-options').innerHTML=state.teams[state.player].map((c,i)=>({c,i})).filter(({c,i})=>c.hp>0&&i!==state.active[state.player]).map(({c,i})=>`<button class="reserve" data-slot="${i}"><strong>${c.name} · ${c.type}</strong><small>${c.hp} / ${c.maxHp} HP</small></button>`).join('');
 $('switch-options').querySelectorAll('button').forEach(b=>b.onclick=()=>swap(Number(b.dataset.slot)));if(!$('switch-dialog').open)$('switch-dialog').showModal();if(preferred!==undefined)$('switch-options').querySelector(`[data-slot="${preferred}"]`)?.focus();
}
function swap(i){const p=state.player,old=current(),next=state.teams[p][i];if(state.winner!==null||!next||next.hp===0||i===state.active[p])return;old.charge=false;old.ready=false;old.guard=false;state.active[p]=i;log(`P${p+1} deployed ${next.name}${state.replacement!==null?' — free replacement.':' — turn used.'}`);if(state.replacement!==null)state.replacement=null;else{current(1-p).guard=false;state.player=1-p;state.turn++;}$('switch-dialog').close();render();}
 $('switch-dialog').addEventListener('cancel',e=>{if(state.replacement!==null)e.preventDefault();});$('switch').onclick=()=>openSwitch();$('restart').onclick=reset;reset();
