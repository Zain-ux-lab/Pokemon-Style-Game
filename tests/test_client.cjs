// Run: node --test tests/test_client.cjs
const {test} = require('node:test');
const assert = require('node:assert/strict');
const {readFileSync} = require('node:fs');
const vm = require('node:vm');

// Minimal DOM for connection flow only; full battle rendering is browser-tested.
function element() {
  return {open:false, hidden:false, style:{setProperty(){}},
    classList:{add(){},remove(){},toggle(){}},
    addEventListener(){}, replaceChildren(){}, querySelectorAll(){return [];},
    querySelector(){return element();}, showModal(){this.open=true;}, close(){this.open=false;}};
}

test('bot waits after the player animation and controls stay locked through its response', async () => {
  const nodes = new Map();
  const get = id => {if(!nodes.has(id))nodes.set(id,element());return nodes.get(id);};
  const character = {id:'mage',name:'Mage',art:'Mage',type:'Magic',hp:100,maxHp:100,moves:[]};
  const initial = {teams:[[character],[character]],active:[0,0],player:0,replacement:null,winner:null,turn:1,revision:0,actions:[{kind:'move',index:0}],log:[]};
  const human = {...initial, player:1, turn:2, animation:{kind:'attack',actor:0,target:1}};
  const bot = {...initial, turn:3, revision:1, animation:{kind:'attack',actor:1,target:0}};
  const replies = [[],{state:initial},{frames:[human,bot],state:bot}];
  const timers = [];
  const waits = [];
  const tick = () => {const batch=timers.splice(0);batch.forEach(fn=>fn());};
  const context = vm.createContext({
    document:{getElementById:get,querySelector:get,querySelectorAll:()=>[],createElement:element,addEventListener(){}},
    window:{addEventListener(){}},setTimeout:(fn,ms)=>{waits.push(ms);timers.push(fn);return timers.length;},clearTimeout(){},AbortSignal,
    fetch:async()=>({ok:true,json:async()=>replies.shift()}),
  });
  vm.runInContext(readFileSync(new URL('../frontend/script.js',`file://${__filename}`),'utf8'),context);
  await new Promise(setImmediate);
  const action = vm.runInContext('sendAction("move",0)',context);
  await new Promise(setImmediate);
  assert.equal(vm.runInContext('state.turn',context),2);
  assert.equal(vm.runInContext('allowed("move",0)',context),false);
  tick();
  await new Promise(setImmediate);
  assert.equal(vm.runInContext('state.turn',context),2,'Bot must wait after the player animation');
  tick();
  await new Promise(setImmediate);
  assert.equal(vm.runInContext('state.turn',context),3);
  assert.equal(vm.runInContext('allowed("move",0)',context),false,'Bot animation must finish before another action');
  tick();
  await action;
  assert.deepEqual(waits,[460,460,650,460,460]);
  assert.equal(vm.runInContext('allowed("move",0)',context),true);
});

test('retry restores an existing match and dismisses the initial team picker', async () => {
  const nodes = new Map();
  const get = id => {if(!nodes.has(id))nodes.set(id,element());return nodes.get(id);};
  const character = {id:'mage',name:'Mage',art:'Mage',type:'Magic',hp:100,maxHp:100,moves:[]};
  const saved = {teams:[[character],[character]],active:[0,0],player:0,replacement:null,winner:null,turn:3,revision:1,actions:[],log:[]};
  const replies = [new Error('Network unavailable'),[],{state:saved}];
  const context = vm.createContext({
    document:{getElementById:get,querySelector:get,querySelectorAll:()=>[],createElement:element,addEventListener(){}},
    window:{addEventListener(){}},setTimeout,clearTimeout,AbortSignal,
    fetch:async()=>{const data=replies.shift();if(data instanceof Error)throw data;return {ok:true,json:async()=>data};},
  });
  vm.runInContext(readFileSync(new URL('../frontend/script.js',`file://${__filename}`),'utf8'),context);
  await new Promise(setImmediate);
  assert.equal(get('team-dialog').open,true);
  assert.equal(get('team-cancel').hidden,true);
  await vm.runInContext('connect()',context);
  assert.equal(get('turn').textContent,'YOUR TURN');
  assert.equal(get('team-dialog').open,false,'Recovered match should be visible without dismissing team selection');
});

test('move details distinguish healing and guarding from attacks', async () => {
  const nodes = new Map();
  const get = id => {if(!nodes.has(id))nodes.set(id,element());return nodes.get(id);};
  const healer = {id:'glowmire',name:'Glowmire',art:'Glowmire',type:'Spirit',hp:60,maxHp:90,
    moves:[{name:'Ember Beam',effect:'damage',amount:21,description:'Deals damage.',symbol:'✦'},
      {name:'Lantern Flare',effect:'heal',amount:25,description:'Restore up to 25 HP.',symbol:'＋'},
      {name:'Root Snare',effect:'guard',amount:50,description:'Reduce the next hit by 50%.',symbol:'◈'}]};
  const enemy = {id:'mage',name:'Mage',art:'Mage',type:'Magic',hp:100,maxHp:100,moves:[]};
  const saved = {teams:[[healer],[enemy]],active:[0,0],player:0,replacement:null,winner:null,turn:1,revision:0,actions:[],log:[]};
  const replies = [[],{state:saved}];
  const context = vm.createContext({
    document:{getElementById:get,querySelector:get,querySelectorAll:()=>[],createElement:element,addEventListener(){}},
    window:{addEventListener(){}},setTimeout,clearTimeout,AbortSignal,
    fetch:async()=>({ok:true,json:async()=>replies.shift()}),
  });
  vm.runInContext(readFileSync(new URL('../frontend/script.js',`file://${__filename}`),'utf8'),context);
  await new Promise(setImmediate);

  vm.runInContext('preview(1)',context);
  assert.match(get('details').innerHTML,/RECOVERY[\s\S]*25[\s\S]*HP restored/);
  vm.runInContext('preview(2)',context);
  assert.match(get('details').innerHTML,/GUARD[\s\S]*50%[\s\S]*next hit/);
});
