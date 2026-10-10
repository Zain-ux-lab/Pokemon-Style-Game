(() => {
 const guidance=document.querySelector('.battle-orientation');
 if(guidance)for(const dialog of document.querySelectorAll('dialog'))dialog.append(guidance.cloneNode(true));
 const music=document.getElementById('battle-music'),toggle=document.getElementById('battle-music-toggle'),volume=document.getElementById('battle-volume');
 const musicStatus=document.getElementById('music-status');
 let musicWanted=true, audioPrefs={};
 try{audioPrefs=JSON.parse(localStorage.getItem('clashbound-audio')??localStorage.getItem('battlelab-audio')??'{}');if(typeof audioPrefs.enabled==='boolean')musicWanted=audioPrefs.enabled;}catch{}
 music.volume=.25;
 function musicLabel(){toggle.textContent=musicWanted?'Mute music':'Play music';toggle.setAttribute('aria-pressed',String(musicWanted));}
 async function startMusic(){
   if(!musicWanted||document.hidden)return;
   try{await music.play();if(!musicWanted||document.hidden){music.pause();return;}musicStatus.textContent='';}
   catch{if(musicWanted)musicStatus.textContent='Music is enabled. Click or tap to start playback.';}
 }
 toggle.onclick=()=>{
   musicWanted=!musicWanted;musicLabel();
   try{audioPrefs=JSON.parse(localStorage.getItem('clashbound-audio')??localStorage.getItem('battlelab-audio')??'{}');audioPrefs.enabled=musicWanted;localStorage.setItem('clashbound-audio',JSON.stringify(audioPrefs));}catch{}
   if(musicWanted)startMusic();else{music.pause();musicStatus.textContent='Music is muted.';}
 };
 function musicInteraction(event){if(musicWanted&&music.paused&&!event.target.closest('#battle-music-toggle'))startMusic();}
 document.addEventListener('pointerdown',musicInteraction);
 document.addEventListener('keydown',event=>{if(!event.repeat&&!event.ctrlKey&&!event.metaKey&&!event.altKey)musicInteraction(event);});
 musicLabel();
 const tabs=['music','interface','guide'];
 function selectTab(id){for(const name of tabs){document.getElementById(name+'-panel').hidden=name!==id;document.getElementById(name+'-tab').setAttribute('aria-selected',String(name===id));document.getElementById(name+'-tab').tabIndex=name===id?0:-1;}}
 for(const name of tabs){const tab=document.getElementById(name+'-tab');tab.onclick=()=>selectTab(name);tab.onkeydown=e=>{if(['ArrowLeft','ArrowRight','Home','End'].includes(e.key)){e.preventDefault();const next=e.key==='Home'?tabs[0]:e.key==='End'?tabs[tabs.length-1]:tabs[(tabs.indexOf(name)+(e.key==='ArrowRight'?1:tabs.length-1))%tabs.length];selectTab(next);document.getElementById(next+'-tab').focus();}};}
 selectTab('music');
 const defaults={motion:matchMedia('(prefers-reduced-motion: reduce)').matches,log:true,tooltips:true};
 let prefs={...defaults};try{const saved=JSON.parse(localStorage.getItem('clashbound-interface')??localStorage.getItem('battlelab-interface')??'{}');for(const key of Object.keys(defaults))if(typeof saved[key]==='boolean')prefs[key]=saved[key];}catch{}
 function apply(){document.body.classList.toggle('reduce-motion',prefs.motion);document.body.classList.toggle('hide-log',!prefs.log);document.body.classList.toggle('hide-tooltips',!prefs.tooltips);document.getElementById('reduce-motion').checked=prefs.motion;document.getElementById('show-log').checked=prefs.log;document.getElementById('show-tooltips').checked=prefs.tooltips;try{localStorage.setItem('clashbound-interface',JSON.stringify(prefs));}catch{}}
 for(const [id,key] of [['reduce-motion','motion'],['show-log','log'],['show-tooltips','tooltips']])document.getElementById(id).onchange=e=>{prefs[key]=e.target.checked;apply();};
 document.getElementById('reset-interface').onclick=()=>{prefs={...defaults};apply();};apply();
 try{const raw=localStorage.getItem('clashbound-volume')??localStorage.getItem('battlelab-volume');const saved=Number(raw);if(raw!==null&&Number.isFinite(saved)){volume.value=Math.min(100,Math.max(0,saved));music.volume=Number(volume.value)/100;}}catch{}
 volume.oninput=()=>{music.volume=Number(volume.value)/100;try{localStorage.setItem('clashbound-volume',volume.value);}catch{}};

 document.getElementById('new-match').onclick=()=>{if(busy)return;document.getElementById('settings-dialog').close();openTeamPicker(true);};
 document.getElementById('restart-match').onclick=async()=>{if(busy||!state||disconnected)return;selection=state.teams[0].map(c=>c.id);for(const c of state.teams[0]){const pool=catalog.find(x=>x.id===c.id).movePool;loadouts[c.id]=c.moves.map(m=>pool.findIndex(x=>x.name===m.name));}document.getElementById('settings-dialog').close();await startBattle();};
 document.addEventListener('visibilitychange',()=>{if(document.hidden)music.pause();else startMusic();});
 startMusic();
})();
