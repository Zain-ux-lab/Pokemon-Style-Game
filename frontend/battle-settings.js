(() => {
 const music=document.getElementById('battle-music'),toggle=document.getElementById('battle-music-toggle'),volume=document.getElementById('battle-volume');
 music.volume=.25;
 toggle.onclick=async()=>{try{if(music.paused){await music.play();toggle.textContent='Pause music';}else{music.pause();toggle.textContent='Play music';}document.getElementById('music-status').textContent='';}catch{document.getElementById('music-status').textContent='Music could not start. Try again.';}};
 volume.oninput=()=>music.volume=Number(volume.value)/100;
 const tabs=['music','interface','guide'];
 function selectTab(id){for(const name of tabs){document.getElementById(name+'-panel').hidden=name!==id;document.getElementById(name+'-tab').setAttribute('aria-selected',String(name===id));document.getElementById(name+'-tab').tabIndex=name===id?0:-1;}}
 for(const name of tabs){const tab=document.getElementById(name+'-tab');tab.onclick=()=>selectTab(name);tab.onkeydown=e=>{if(['ArrowLeft','ArrowRight','Home','End'].includes(e.key)){e.preventDefault();const next=e.key==='Home'?tabs[0]:e.key==='End'?tabs[tabs.length-1]:tabs[(tabs.indexOf(name)+(e.key==='ArrowRight'?1:tabs.length-1))%tabs.length];selectTab(next);document.getElementById(next+'-tab').focus();}};}
 selectTab('music');
 const defaults={motion:matchMedia('(prefers-reduced-motion: reduce)').matches,log:true,tooltips:true};
 let prefs={...defaults};try{const saved=JSON.parse(localStorage.getItem('battlelab-interface')||'{}');for(const key of Object.keys(defaults))if(typeof saved[key]==='boolean')prefs[key]=saved[key];}catch{}
 function apply(){document.body.classList.toggle('reduce-motion',prefs.motion);document.body.classList.toggle('hide-log',!prefs.log);document.body.classList.toggle('hide-tooltips',!prefs.tooltips);document.getElementById('reduce-motion').checked=prefs.motion;document.getElementById('show-log').checked=prefs.log;document.getElementById('show-tooltips').checked=prefs.tooltips;try{localStorage.setItem('battlelab-interface',JSON.stringify(prefs));}catch{}}
 for(const [id,key] of [['reduce-motion','motion'],['show-log','log'],['show-tooltips','tooltips']])document.getElementById(id).onchange=e=>{prefs[key]=e.target.checked;apply();};
 document.getElementById('reset-interface').onclick=()=>{prefs={...defaults};apply();};apply();
 try{const saved=Number(localStorage.getItem('battlelab-volume'));if(localStorage.getItem('battlelab-volume')!==null&&Number.isFinite(saved)){volume.value=Math.min(100,Math.max(0,saved));music.volume=Number(volume.value)/100;}}catch{}
 volume.oninput=()=>{music.volume=Number(volume.value)/100;try{localStorage.setItem('battlelab-volume',volume.value);}catch{}};

 document.getElementById('new-match').onclick=()=>{if(busy)return;document.getElementById('settings-dialog').close();openTeamPicker(true);};
 document.getElementById('restart-match').onclick=async()=>{if(busy||!state||disconnected)return;selection=state.teams[0].map(c=>c.id);for(const c of state.teams[0]){const pool=catalog.find(x=>x.id===c.id).movePool;loadouts[c.id]=c.moves.map(m=>pool.findIndex(x=>x.name===m.name));}document.getElementById('settings-dialog').close();await startBattle();};
 document.addEventListener('visibilitychange',()=>{if(document.hidden){music.pause();toggle.textContent='Play music';}});
})();
