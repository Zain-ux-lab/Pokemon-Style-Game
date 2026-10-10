const test = require('node:test');
const assert = require('node:assert/strict');
const vm = require('node:vm');
const {readFileSync} = require('node:fs');

// Browser dependencies only; each test executes the actual production script.
function presentation(script, saved = {}) {
  const storage = new Map(Object.entries(saved));
  const nodes = new Map();
  function element(id) {
    const attributes = new Map();
    return {
      id, value:25, checked:false, textContent:'', children:[], listeners:{},
      attributes, classList:{toggle(){}},
      setAttribute(name,value){attributes.set(name,value);},
      addEventListener(name,handler){this.listeners[name]=handler;},
      querySelector(selector){return get(id+selector);},
      append(child){this.children.push(child);child.parentElement=this;},
      cloneNode(){return element(id);},
    };
  }
  function get(id) {if(!nodes.has(id))nodes.set(id,element(id));return nodes.get(id);}
  const body=element('body'), guidance=element('orientation');
  body.append(guidance);
  const dialogs=['switch','team','result','settings'].map(element);
  const music=get(script==='audio.js'?'theme-music':'battle-music');
  music.volume=.25;music.paused=true;music.playCount=0;
  music.play=()=>{music.playCount++;music.paused=false;return Promise.resolve();};
  music.pause=()=>{music.paused=true;};
  const context=vm.createContext({
    document:{body,hidden:false,getElementById:get,addEventListener(){},
      querySelector:()=>guidance,querySelectorAll:()=>dialogs},
    window:{}, localStorage:{getItem:key=>storage.get(key)??null,setItem:(key,value)=>storage.set(key,value)},
    matchMedia:()=>({matches:false}), performance:{now:()=>100},
    requestAnimationFrame:()=>1,cancelAnimationFrame(){},setTimeout,clearTimeout,
  });
  vm.runInContext(readFileSync(new URL('../frontend/'+script,`file://${__filename}`),'utf8'),context);
  return {get,storage,music,guidance,dialogs};
}

test('homepage preserves legacy mute and separate sound levels',()=>{
  const {get,music,storage}=presentation('audio.js',{'battlelab-audio':JSON.stringify({enabled:false,music:7,effects:13})});
  assert.equal(music.playCount,0,'An existing explicit mute must prevent autoplay');
  assert.equal(get('sound-toggle').attributes.get('aria-pressed'),'false');
  assert.equal(Number(get('music-volume').value),7);
  assert.equal(Number(get('effects-volume').value),13);
  get('music-volume').value=11;
  get('music-volume').listeners.input();
  assert.deepEqual(JSON.parse(storage.get('clashbound-audio')),{enabled:false,music:11,effects:13});
});

test('homepage uses the current preference ahead of the legacy preference',()=>{
  const {get,music}=presentation('audio.js',{
    'clashbound-audio':JSON.stringify({enabled:false,music:19,effects:23}),
    'battlelab-audio':JSON.stringify({enabled:true,music:99,effects:99}),
  });
  assert.equal(music.playCount,0);
  assert.equal(Number(get('music-volume').value),19);
});

test('fresh homepage visitors have music enabled by default',()=>{
  const {get,music}=presentation('audio.js');
  assert.equal(get('sound-toggle').attributes.get('aria-pressed'),'true');
  assert.equal(music.playCount,1);
});

test('battle preserves legacy mute, interface settings and volume',()=>{
  const {get,music,storage}=presentation('battle-settings.js',{
    'battlelab-audio':JSON.stringify({enabled:false}),
    'battlelab-interface':JSON.stringify({motion:true,log:false,tooltips:false}),
    'battlelab-volume':'42',
  });
  assert.equal(music.playCount,0);
  assert.equal(get('battle-music-toggle').attributes.get('aria-pressed'),'false');
  assert.equal(music.volume,.42);
  assert.equal(get('reduce-motion').checked,true);
  assert.equal(get('show-log').checked,false);
  assert.equal(get('show-tooltips').checked,false);
  get('battle-music-toggle').onclick();
  assert.equal(JSON.parse(storage.get('clashbound-audio')).enabled,true);
});

test('current battle preferences win, including a zero volume',()=>{
  const {get,music}=presentation('battle-settings.js',{
    'clashbound-audio':JSON.stringify({enabled:false}),
    'battlelab-audio':JSON.stringify({enabled:true}),
    'clashbound-interface':JSON.stringify({log:true}),
    'battlelab-interface':JSON.stringify({log:false}),
    'clashbound-volume':'0','battlelab-volume':'42',
  });
  assert.equal(music.playCount,0);
  assert.equal(music.volume,0);
  assert.equal(get('show-log').checked,true);
});

test('each battle modal includes its own rotation guidance',()=>{
  const {dialogs,guidance}=presentation('battle-settings.js');
  for(const dialog of dialogs){
    assert.equal(dialog.children.length,1,'The active modal needs an accessible instruction inside it');
    assert.notEqual(dialog.children[0],guidance,'Keep the original guidance available without a modal');
    assert.equal(dialog.children[0].parentElement,dialog);
  }
});
