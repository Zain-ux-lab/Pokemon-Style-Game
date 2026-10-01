function sprite(name){
 const shapes = name==='Mage' ? '<path fill="#394d65" d="M15 28h34l8 30H9z"/><path fill="#526e86" d="M22 28h20l7 26H16z"/><path fill="#e4c9a0" d="M24 17h16v17H24z"/><path fill="#e6e0cf" d="M22 27h21v8h-4v7h-5v5h-6v-6h-4z"/><path fill="#344b63" d="M13 18h38v6H13zM23 10h20v9H23zM28 3h10v9H28zM33 0h5v4h-5z"/><path fill="#bea16b" d="M20 17h25v3H20z"/><path fill="#27353c" d="M13 56h14v5H13zM36 56h15v5H36z"/><path fill="#a07143" d="M51 22h3v32h-3z"/><path fill="#9fdbcd" d="M49 17h7v7h-7z"/><path fill="#313c41" d="M27 24h3v3h-3zM36 24h3v3h-3z"/>' : name==='Sporestag' ? '<path fill="#455742" d="M8 45h8v13H8zM22 46h7v14h-7zM39 46h7v14h-7zM51 43h7v15h-7z"/><path fill="#7f9152" d="M8 26h46v25H8zM16 19h29v9H16z"/><path fill="#a4ad66" d="M18 23h25v20H18z"/><path fill="#576b48" d="M33 23h5v27h-5z"/><path fill="#64704b" d="M4 34h18v16H4z"/><path fill="#d6c39a" d="M7 19h5v18H7zM2 16h5v8H2zM11 14h5v10h-5z"/><path fill="#e6dec1" d="M24 11h4v12h-4zM42 17h4v10h-4z"/><path fill="#bd7754" d="M17 8h18v7H17zM21 4h10v5H21zM37 15h16v6H37z"/><path fill="#e8c095" d="M21 8h4v3h-4zM28 9h4v3h-4zM41 16h4v3h-4z"/><path fill="#182e2b" d="M7 36h4v4H7z"/>' : '<path fill="#8cb9af" d="M20 54h24v4H20zM25 59h13v3H25z"/><path fill="#415d60" d="M19 17h26v36H19zM15 21h34v5H15zM15 47h34v6H15zM24 7h16v12H24z"/><path fill="#98b9a3" d="M28 10h8v7h-8z"/><path fill="#dbb670" d="M23 25h18v21H23z"/><path fill="#f6d994" d="M27 28h10v14H27z"/><path fill="#fff1bd" d="M30 30h5v8h-5z"/><path fill="#314b51" d="M29 22h4v26h-4zM19 34h25v3H19z"/><path fill="#bad7c4" d="M9 28h5v13H9zM50 26h5v13h-5z"/>';
 return `<svg class="sprite" viewBox="0 0 64 64" shape-rendering="crispEdges" role="img" aria-label="${name} placeholder artwork"><ellipse cx="32" cy="61" rx="24" ry="2" fill="#263d3320"/>${shapes}</svg>`;
}
// The server owns combat, legal actions, damage previews and bot decisions.
let state = null;
let catalog = [];
let selection = [];
let busy = false;
let disconnected = false;
let detailTimer;
const $ = id => document.getElementById(id);
const TYPES = {Magic:'#6a64a2', Physical:'#9c633b', Spirit:'#3c827c'};
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
function artwork(c) { return sprite(c.art).replace(`${c.art} placeholder artwork`, `${c.name} placeholder artwork`); }
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
    $('switch').disabled = true; $('turn').textContent = 'CHOOSE YOUR TEAM';
    return;
  }
  hideDetails();
  for (let p=0; p<2; p++) {
    const c = current(p);
    $(`hud-${p}`).style.setProperty('--type', TYPES[c.type]);
    $(`hud-${p}`).innerHTML = `<div class="side-label">${p===0?'YOU':'OPPONENT'} <span>${p===0?'PLAYER':'TACTICAL BOT'}</span></div><div class="hud-top"><strong>${c.name}</strong><span class="type">${c.type.toUpperCase()}</span></div><div class="health" role="meter" aria-label="${p===0?'Your':'Opponent'} health" aria-valuemin="0" aria-valuemax="${c.maxHp}" aria-valuenow="${c.hp}"><span style="width:${100*c.hp/c.maxHp}%"></span></div><div class="hp">${c.hp} / ${c.maxHp} HP</div>`;
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
  $('moves').innerHTML = c.moves.map((m,i)=>`<button class="move" style="--type:${TYPES[c.type]}" ${allowed('move',i)?'':'disabled'} data-move="${i}"><span class="move-symbol">${m.symbol}</span>${m.name}</button>`).join('');
  $('moves').querySelectorAll('button').forEach(button=>{
    const index=Number(button.dataset.move);
    button.onclick=()=>sendAction('move',index);
    button.onmouseenter=()=>showDetails(index,button); button.onfocus=()=>showDetails(index,button);
    button.onmouseleave=scheduleHideDetails; button.onblur=scheduleHideDetails;
  });
  const kind = state.replacement===0?'replace':'switch';
  $('switch').disabled = busy || disconnected || !state.actions.some(a=>a.kind===kind);
  $('switch').innerHTML = kind==='replace'?'⇄ Deploy replacement <span>Free replacement</span>':'⇄ Switch character <span>Uses your turn</span>';
  $('log').replaceChildren(...state.log.map(message=>{const li=document.createElement('li');li.textContent=message;return li;}));
  $('log').scrollTop=$('log').scrollHeight;
}
function preview(index) {
  const c=current(), move=c.moves[index];
  $('details').style.setProperty('--type',TYPES[c.type]);
  $('details').innerHTML=`<div class="detail-kicker">ATTACK</div><h3>${move.name}</h3><p>${move.description}</p><div class="damage">${move.damage}<small>damage to ${current(1).name}</small></div>`;
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
  panel.style.left=Math.max(8,r.left-size-14)+'px';
  panel.style.top=Math.max(8,Math.min(innerHeight-size-8,r.top+r.height/2-size/2))+'px';
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
      state=data.frames[i];render();
      if (i<data.frames.length-1) await delay(700);
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
  $('team-options').innerHTML=catalog.map(c=>{
    const rank=selection.indexOf(c.id);
    return `<button class="team-choice ${rank>=0?'selected':''}" data-id="${c.id}" aria-pressed="${rank>=0}" ${busy || (selection.length===3 && rank<0)?'disabled':''}><span class="pick-number">${rank>=0?rank+1:'+'}</span>${artwork(c)}<strong>${c.name}</strong><small>${c.type} · ${c.maxHp} HP</small><small>${c.move} · ${c.power} power</small></button>`;
  }).join('');
  $('team-options').querySelectorAll('button').forEach(button=>button.onclick=()=>{
    const id=button.dataset.id; selection=selection.includes(id)?selection.filter(c=>c!==id):[...selection,id];
    renderChoices(); $('team-options').querySelector(`[data-id="${id}"]`).focus();
  });
  $('start-battle').disabled=busy || disconnected || selection.length!==3;
  $('start-battle').textContent=busy?'Starting…':`Enter arena · ${selection.length} / 3`;
}
function openTeamPicker() {
  if (busy) return;
  $('switch-dialog').close();hideDetails();
  selection=state?state.teams[0].map(c=>c.id):selection;
  $('team-cancel').hidden=!state;
  renderChoices();
  if (!$('team-dialog').open) $('team-dialog').showModal();
}
async function startBattle() {
  if (busy || selection.length!==3 || disconnected) return;
  busy=true;setError();renderChoices();render();
  try {
    state=(await request('/api/battle',{roster:selection})).state;
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
$('team-dialog').addEventListener('cancel',e=>{if(!state || busy)e.preventDefault();});
$('team-cancel').onclick=()=>{if(!busy){$('team-dialog').close();if(state?.replacement===0)openSwitch();}};
$('switch').onclick=()=>openSwitch();$('restart').onclick=openTeamPicker;
$('start-battle').onclick=startBattle;$('retry').onclick=connect;$('team-retry').onclick=connect;
document.addEventListener('keydown',e=>{if(e.key==='Escape')hideDetails();});
window.addEventListener('resize',hideDetails);
connect();
