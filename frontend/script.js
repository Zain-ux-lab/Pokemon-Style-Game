// The server owns combat, legal actions, damage previews and bot decisions.
let state = null;
let catalog = [];
let selection = [];
let loadouts = {};
let busy = false;
let disconnected = false;
let detailTimer;
const $ = id => document.getElementById(id);
const TYPES = {Magic:'#6a64a2', Physical:'#9c633b', Spirit:'#3c827c'};
const TYPE_SYMBOLS = {Magic:'✦',Physical:'◆',Spirit:'◉'};
const EFFECT_NAMES = {spores:'Spores',thorns:'Thorns',mark:'Marked',paralyse:'Paralysed',confuse:'Confused',weaken:'Weakened',expose:'Exposed',echo:'Spell echo'};
function escapeText(value) {
  return String(value).replace(/[&<>"']/g, c => ({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c]));
}
function confusedMove(c, index) { return c.statuses?.some(s=>s.name==='confuse' && s.moveIndex===index); }
function effectIndicators(c, player) {
  const statuses=c.statuses??[];
  if (!statuses.length) return '';
  const owner=player===0?'your':'the opponent’s';
  return `<details class="effect-indicators"><summary aria-label="${escapeText(c.name)}: ${statuses.map(s=>`${EFFECT_NAMES[s.name]??s.name}, ${s.turnsRemaining} ${s.turnsRemaining===1?'action':'actions'} remaining`).join('; ')}. Open effect explanations.">${statuses.map(s=>`<span class="effect-badge">${EFFECT_NAMES[s.name]??s.name} <b>${s.turnsRemaining}</b></span>`).join('')}</summary><div class="effect-explanations">${statuses.map(s=>`<p><strong>${EFFECT_NAMES[s.name]??s.name} · ${s.turnsRemaining} of ${owner} ${s.turnsRemaining===1?'actions remains':'actions remain'}</strong>${escapeText(s.description)}${s.name==='confuse' && Number.isInteger(s.moveIndex)?`<em>${escapeText(c.moves[s.moveIndex]?.name??'Marked move')} causes 8 recoil.</em>`:''}</p>`).join('')}${c.switchBlockedReason?`<p>${escapeText(c.switchBlockedReason)}</p>`:''}</div></details>`;
}
function typeSymbol(type) { return `<span class="type" title="${type}" aria-label="${type}">${TYPE_SYMBOLS[type]??'◇'}</span>`; }
const FRAME_READ_MS = 1800;
const BOT_PAUSE_MS = 700;
const delay = ms => new Promise(resolve => setTimeout(resolve, ms));

async function request(path, body) {
  const response = await fetch(path, {
    method: body === undefined ? 'GET' : 'POST',
    headers: body === undefined ? {} : {'Content-Type':'application/json'},
    body: body === undefined ? undefined : JSON.stringify(body),
    signal: AbortSignal.timeout(10000),
  });
  let data;
  try { data = await response.json(); } catch { data = {}; }
  if (!response.ok) {
    const error = new Error(typeof data.detail === 'string' ? data.detail : 'Could not complete the request. Please try again.');
    error.status = response.status;
    throw error;
  }
  return data;
}
function setError(message = '') {
  document.querySelectorAll('[data-error]').forEach(node => { node.textContent = message; node.hidden = !message; });
  $('retry').hidden = !disconnected;
  $('team-retry').hidden = !disconnected;
}
function current(player = 0) { return state.teams[player][state.active[player]]; }
function allowed(kind, index) { return !busy && !disconnected && state?.actions.some(a => a.kind === kind && a.index === index); }
function artwork(c) { return `<img class="sprite" src="assets/characters/${c.id}.png" alt="${c.name}" decoding="sync">`; }
function portrait(c, index, enemy = false) {
  const player = enemy ? 1 : 0;
  const active = state.active[player] === index;
  const description = `${c.name}, ${c.hp} of ${c.maxHp} health${active ? ', active' : ''}`;
  const kind = state.replacement === 0 ? 'replace' : 'switch';
  return `<${enemy?'div':'button'} class="portrait ${enemy?'enemy-portrait':''} ${active?'active':''} ${c.hp===0?'knocked-out':''}" aria-label="${description}" ${enemy?'':`data-slot="${index}" ${allowed(kind,index)?'':'disabled'}`}>
    ${artwork(c)}<small>${c.name}</small><div class="health"><span style="width:${100*c.hp/c.maxHp}%"></span></div></${enemy?'div':'button'}>`;
}
function render() {
  $('restart').disabled = busy;
  if (!state) {
    $('moves').replaceChildren(); $('roster').replaceChildren(); $('enemy-roster').replaceChildren();
    $('turn').textContent = 'CHOOSE YOUR TEAM';
    return;
  }
  hideDetails();
  if (state.arena) {
    const arena=document.querySelector('.arena');
    arena.style.backgroundImage=`url("${state.arena.image}")`;
    arena.setAttribute('aria-label',`${state.arena.name} battlefield`);
    $('arena-name').textContent=state.arena.name.toUpperCase();
    $('battle-arena-caption').textContent=state.arena.name;
    document.title=`Clashbound · ${state.arena.name}`;
  }
  for (let p=0; p<2; p++) {
    const c = current(p);
    $(`hud-${p}`).style.setProperty('--type', TYPES[c.type]);
    $(`hud-${p}`).innerHTML = `<div class="side-label">${p===0?'YOU':'OPPONENT'} <span>${p===0?'PLAYER':'TACTICAL BOT'}</span></div><div class="hud-top"><strong>${c.name}</strong><span class="type" title="${c.type}" aria-label="${c.type}">${TYPE_SYMBOLS[c.type]}</span></div><div class="health" role="meter" aria-label="${p===0?'Your':'Opponent'} health" aria-valuemin="0" aria-valuemax="${c.maxHp}" aria-valuenow="${c.hp}"><span style="width:${100*c.hp/c.maxHp}%"></span></div><div class="hp">${c.hp} / ${c.maxHp} HP</div>${c.guardPercent?`<div class="guard-state">◈ NEXT HIT −${c.guardPercent}%</div>`:''}`;
    $(`hud-${p}`).innerHTML += effectIndicators(c,p);
    $(`fighter-${p}`).innerHTML = artwork(c);
    $(`fighter-${p}`).classList.toggle('fainted', c.hp===0);
  }
  $('enemy-roster').innerHTML = state.teams[1].map((c,i)=>portrait(c,i,true)).join('');
  $('roster').innerHTML = state.teams[0].map((c,i)=>portrait(c,i)).join('');
  $('roster').querySelectorAll('button').forEach(button => button.onclick=()=>openSwitch(Number(button.dataset.slot)));
  $('team-label').textContent = 'YOUR TEAM';
  $('turn-count').textContent = `TURN ${state.turn}`;
  $('turn').textContent = state.winner!==null ? (state.winner===0?'YOU WIN':'BOT WINS') : disconnected ? 'CONNECTION LOST' : state.replacement===0 ? 'CHOOSE A REPLACEMENT' : state.player===1 ? 'BOT IS CHOOSING…' : busy ? 'RESOLVING TURN…' : 'YOUR TURN';
  $('action-label').textContent = state.winner!==null ? 'MATCH COMPLETE' : state.replacement===0 ? 'DEPLOY A RESERVE' : 'CHOOSE YOUR MOVE';
  const c = current();
  $('moves').innerHTML = c.moves.map((m,i)=>`<button class="move ${confusedMove(c,i)?'confused-move':''}" style="--type:${TYPES[c.type]}" ${allowed('move',i)?'':'disabled'} data-move="${i}" ${confusedMove(c,i)?`aria-label="${escapeText(m.name)}, confused: causes 8 recoil"`:''}><span class="move-symbol">${m.symbol}</span>${m.name}${confusedMove(c,i)?'<small class="move-warning">Confused · 8 recoil</small>':''}</button>`).join('');
  $('moves').querySelectorAll('button').forEach(button=>{
    const index=Number(button.dataset.move);
    button.onclick=()=>sendAction('move',index);
    button.onmouseenter=()=>showDetails(index,button); button.onfocus=()=>showDetails(index,button);
    button.onmouseleave=scheduleHideDetails; button.onblur=scheduleHideDetails;
  });
  $('log').replaceChildren(...state.log.map(message=>{const li=document.createElement('li');li.textContent=message;return li;}));
  $('log').scrollTop=$('log').scrollHeight;
  const result=$('result-dialog');
  if(result && state.winner!==null && !busy && !disconnected){
    $('result-title').textContent=state.winner===0?'Victory':'Defeat';
    $('result-copy').textContent=state.winner===0?'Your team takes the arena.':'The bot takes this battle. Your next move awaits.';
    $('result-team').textContent=state.teams[state.winner].map(c=>c.name).join(' · ');
    if(!result.open)result.showModal();
  }

}
function preview(index) {
  const c=current(), move=c.moves[index];
  $('details').style.setProperty('--type',TYPES[c.type]);
  const label=move.effect==='heal'?'RECOVERY':move.effect==='guard'?'GUARD':'ATTACK';
  const value=move.effect==='guard'?`${move.amount}%`:move.effect==='damage'?(move.baseDamage??move.amount):move.amount;
  const unit=move.effect==='heal'?'HP restored':move.effect==='guard'?'next hit reduction':'base damage';
  const brief=(move.description??'').split('. ').find(t=>!t.includes(' / ')&&!t.includes('Scales with'))??'';
  $('details').innerHTML=`<div class="detail-kicker">${escapeText(move.damageType??label)}</div><h3>${escapeText(move.name)}</h3><div class="damage">${value}<small>${unit}</small></div><p>${escapeText(brief.slice(0,100))}${brief.length>100?'…':''}</p>${confusedMove(c,index)?'<small>Confused · 8 recoil</small>':''}`;
}
function hideDetails() {
  clearTimeout(detailTimer); document.querySelector('.detail-panel').classList.remove('is-visible');
  document.querySelectorAll('[aria-describedby="details"]').forEach(b=>b.removeAttribute('aria-describedby'));
}
function scheduleHideDetails() { clearTimeout(detailTimer); detailTimer=setTimeout(hideDetails,120); }
function showDetails(index,button) {
  if (busy || !state || state.winner!==null) return;
  clearTimeout(detailTimer); preview(index);
  const panel=document.querySelector('.detail-panel');panel.classList.add('is-visible');button.setAttribute('aria-describedby','details');
  const r=button.getBoundingClientRect(),size=panel.offsetWidth;
  panel.style.left=Math.max(8,Math.min(innerWidth-size-8,r.left-size-14))+'px';
  panel.style.top=Math.max(8,Math.min(innerHeight-panel.offsetHeight-8,r.top+r.height/2-panel.offsetHeight/2))+'px';
}
function openSwitch(preferred) {
  if (!state || busy || disconnected || state.winner!==null) return;
  const forced=state.replacement===0, kind=forced?'replace':'switch';
  const actions=state.actions.filter(a=>a.kind===kind);
  if (!actions.length) return;
  $('switch-title').textContent=forced?'Deploy a replacement':'Switch your character?';
  $('switch-description').textContent=forced?'Your replacement is free. You still get your normal action.':'Switching ends your turn. The bot then takes its action.';
  $('switch-dialog').querySelector('.close').hidden=forced;
  $('switch-options').innerHTML=actions.map(a=>{const c=state.teams[0][a.index];return `<button class="reserve" data-slot="${a.index}"><strong>${c.name} · ${c.type}</strong><small>${c.hp} / ${c.maxHp} HP</small></button>`;}).join('');
  $('switch-options').querySelectorAll('button').forEach(button=>button.onclick=()=>sendAction(kind,Number(button.dataset.slot)));
  if (!$('switch-dialog').open) $('switch-dialog').showModal();
  if (preferred!==undefined) $('switch-options').querySelector(`[data-slot="${preferred}"]`)?.focus();
}
async function sendAction(kind,index) {
  if (!allowed(kind,index)) return;
  busy=true; setError(); $('switch-dialog').close(); render();
  try {
    const data=await request('/api/battle/actions',{kind,index,revision:state.revision});
    for (let i=0;i<data.frames.length;i++) {
      const frame=data.frames[i];
      state=frame;render();
      if(frame.animation && typeof document.createElement==='function') playMoveEffect(frame.animation,null);

      if (frame.animation?.moveName) {
        const name=document.createElement('div');name.className='move-announcement';
        name.textContent=`${frame.animation.actor===0?'You':'Opponent'} · ${frame.animation.moveName}`;
        document.querySelector('.arena').append(name);setTimeout(()=>name.remove(),900);
      }
      for (const change of frame.animation?.hpChanges??[]) {
        const c=current(change.player),bar=$(`hud-${change.player}`).querySelector('.health span');
        if (!document.body?.classList.contains('reduce-motion') && !window.matchMedia?.('(prefers-reduced-motion: reduce)').matches) {
          bar?.animate([{width:`${100*(c.hp-change.amount)/c.maxHp}%`},{width:`${100*c.hp/c.maxHp}%`}],{duration:420,easing:'ease-out'});
        }
        const number=document.createElement('span');number.className=`hp-change ${change.amount>0?'recovery':''}`;
        number.textContent=`${change.amount>0?'+':''}${change.amount}`;
        $(`fighter-${change.player}`).append(number);number.style.setProperty('--hp-display-time', `${FRAME_READ_MS}ms`);setTimeout(()=>number.remove(),FRAME_READ_MS);
      }
      if (frame.animation?.kind==='attack') {
        const attacker=$(`fighter-${frame.animation.actor}`), target=$(`fighter-${frame.animation.target}`);
        attacker.classList.remove('attack-animation'); target.classList.remove('hit-animation');
        void attacker.offsetWidth;
        attacker.classList.add('attack-animation'); target.classList.add('hit-animation');
        setTimeout(()=>{attacker.classList.remove('attack-animation');target.classList.remove('hit-animation');},460);
      } else if (frame.animation?.kind==='heal' || frame.animation?.kind==='guard') {
        const fighter=$(`fighter-${frame.animation.actor}`), animation=`${frame.animation.kind}-animation`;
        fighter.classList.remove(animation);
        void fighter.offsetWidth;
        fighter.classList.add(animation);
        setTimeout(()=>fighter.classList.remove(animation),460);
      }
      // Keep the outcome readable, then pause before presenting the next action.
      if (frame.animation) await delay(FRAME_READ_MS);
      if (i<data.frames.length-1) await delay(BOT_PAUSE_MS);
    }
  } catch (error) {
    // Read the saved result after a lost response; never replay a move blindly.
    try { state=(await request('/api/battle')).state; }
    catch (recovery) { if (recovery.status===404) state=null; else disconnected=true; }
    setError(error.status ? error.message : 'Connection interrupted. Check the server, then retry the connection.');
  } finally {
    busy=false; render();
    if (!state) openTeamPicker();
    else if (state.replacement===0 && !disconnected) openSwitch();
  }
}
function renderChoices() {
  const humanoids=['mage','bramblebelly','veyne','coil','bastion'];
  const groups=[
    {id:'humanoids',name:'Humanoids',characters:catalog.filter(c=>humanoids.includes(c.id))},
    {id:'creatures',name:'Creatures',characters:catalog.filter(c=>!humanoids.includes(c.id))},
  ];
  const choice=c=>{
    const rank=selection.indexOf(c.id);
    const featured=c.moves.find(m=>m.effect)||c.moves[0];
    const strength=featured.effect==='guard'?`${featured.power} power · ${featured.effect_amount}% guard`:featured.effect==='heal'?`heal ${featured.effect_amount} HP`:`${featured.power} power`;
    return `<button class="team-choice ${rank>=0?'selected':''}" data-id="${c.id}" aria-pressed="${rank>=0}" ${busy || (selection.length===3 && rank<0)?'disabled':''}><span class="pick-number">${rank>=0?rank+1:'+'}</span>${artwork(c)}<strong>${c.name}</strong><small>${typeSymbol(c.type)} · ${c.maxHp} HP</small><small>${featured.name} · ${strength}</small></button>`;
  };
  $('team-options').innerHTML=groups.map(group=>`<section class="team-group" aria-labelledby="team-${group.id}"><h3 id="team-${group.id}">${group.name}</h3><div class="team-row">${group.characters.map(choice).join('')}</div></section>`).join('');
  $('team-options').querySelectorAll('button').forEach(button=>button.onclick=()=>{
    const id=button.dataset.id; selection=selection.includes(id)?selection.filter(c=>c!==id):[...selection,id];
    renderChoices(); $('team-options').querySelector(`[data-id="${id}"]`).focus();
  });
  $('loadout-options').innerHTML=selection.map(id=>{
    const c=catalog.find(c=>c.id===id);if(!c?.movePool)return '';
    const chosen=loadouts[id]??(loadouts[id]=[0,1,2,3]);
    return `<fieldset class="loadout"><legend>${c.name} · ${chosen.length}/4 moves</legend><details><summary>Character stats</summary><small>${Object.entries(c.stats).map(([k,v])=>`${k} ${v}`).join(' · ')}</small></details><div>${c.movePool.map((m,i)=>{
      const fixed=c.signatureMoves.includes(i),checked=chosen.includes(i);
      return `<label><input type="checkbox" data-character="${id}" data-pool="${i}" ${checked?'checked':''} ${fixed||busy||(!checked&&chosen.length===4)?'disabled':''}>${m.name}${fixed?' · signature':''}</label>`;
    }).join('')}</div></fieldset>`;
  }).join('');
  $('loadout-options').querySelectorAll('input').forEach(input=>input.onchange=()=>{
    const id=input.dataset.character,index=Number(input.dataset.pool);
    loadouts[id]=input.checked?[...loadouts[id],index]:loadouts[id].filter(i=>i!==index);
    renderChoices();
  });
  $('start-battle').disabled=busy || disconnected || selection.length!==3 || selection.some(id=>(loadouts[id]?.length??4)!==4);
  $('start-battle').textContent=busy?'Starting…':`Enter arena · ${selection.length} / 3`;
}
function openTeamPicker(fresh=false) {
  if (busy) return;
  $('switch-dialog').close();hideDetails();
  if(fresh){selection=[];loadouts={};}else selection=state?state.teams[0].map(c=>c.id):selection;
  $('team-cancel').hidden=!state;
  renderChoices();
  if (!$('team-dialog').open) $('team-dialog').showModal();
}
async function startBattle() {
  if (busy || selection.length!==3 || disconnected) return;
  busy=true;setError();renderChoices();render();
  try {
    state=(await request('/api/battle',{roster:selection,loadouts:Object.fromEntries(selection.map(id=>[id,loadouts[id]??[0,1,2,3]]))})).state;
    $('team-dialog').close();
  } catch (error) { setError(error.status?error.message:'Could not start a battle. Check the server and try again.'); }
  finally { busy=false;renderChoices();render(); }
}
async function connect() {
  if (busy) return;
  busy=true;disconnected=false;setError();render();
  try {
    catalog=await request('/api/roster');
    try { state=(await request('/api/battle')).state; }
    catch (error) { if(error.status===404) state=null; else throw error; }
  } catch { disconnected=true;setError('Cannot reach the game server. Start it, then retry the connection.'); }
  finally {
    busy=false;render();
    if(!state) openTeamPicker();
    else if(!disconnected) {
      $('team-dialog').close();
      if(state.replacement===0) openSwitch();
    }
    if($('team-dialog').open) renderChoices();
  }
}
$('switch-dialog').addEventListener('cancel',e=>{if(state?.replacement===0)e.preventDefault();});
function closeTeamPicker() {
  $('team-dialog').close();
  if(state && state.winner!==null)render();
  else if(state?.replacement===0)openSwitch();
}
$('team-dialog').addEventListener('cancel',e=>{
  if(!state || busy)e.preventDefault();
  else if(state.winner!==null){e.preventDefault();closeTeamPicker();}
});
$('team-cancel').onclick=()=>{if(!busy)closeTeamPicker();};
$('restart').onclick=()=>{if(!busy)$('settings-dialog').showModal();};
$('start-battle').onclick=startBattle;$('retry').onclick=connect;$('team-retry').onclick=connect;
document.addEventListener('keydown',e=>{if(e.key==='Escape')hideDetails();});
window.addEventListener('resize',hideDetails);
connect();

function playMoveEffect(animation,move){
  const arena=document.querySelector('.arena'),source=$(`fighter-${animation.actor}`),target=$(`fighter-${animation.target??animation.actor}`);
  if(!arena || !source?.getBoundingClientRect || !target?.getBoundingClientRect)return;
  const name=animation.moveName??move?.name??`${current(animation.actor).name} ${animation.kind}`;
  const seed=[...name].reduce((n,c)=>n+c.charCodeAt(0),0);
  const family=animation.kind==='heal'?'heal':/Spore|Fungal/.test(name)?'spore':/Spark|Static|Voltage|Coil|Current/.test(name)?'spark':/Strike|Slash|Fang|Jab|Kick|Fist|Bash|Volley|Shot|Arrow/.test(name)?'slash':/Ward|Shell|Coat|Screen|Snare/.test(name)?'shield':'spell';
  const a=source.getBoundingClientRect(),b=target.getBoundingClientRect(),r=arena.getBoundingClientRect();
  const effect=document.createElement('div');effect.className=`move-fx fx-${family}`;effect.setAttribute('aria-hidden','true');
  effect.style.cssText=`--hue:${seed%360};--spin:${seed%120-60}deg;left:${a.left+a.width/2-r.left}px;top:${a.top+a.height/2-r.top}px;--dx:${b.left+b.width/2-a.left-a.width/2}px;--dy:${b.top+b.height/2-a.top-a.height/2}px;--duration:${350+seed%100}ms`;
  for(let i=0;i<5+seed%5;i++){const particle=document.createElement('i');particle.style.setProperty('--i',i);effect.append(particle);}
  arena.append(effect);arena.classList.add('impact-light');setTimeout(()=>{effect.remove();arena.classList.remove('impact-light');},460);
}
if($('result-replay'))$('result-replay').onclick=()=>{$('result-dialog').close();openTeamPicker(true);};
