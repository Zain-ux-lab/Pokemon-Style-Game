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
