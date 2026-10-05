(() => {
  const byId = id => document.getElementById(id);
  const menuButton = byId('menu-toggle'), menu = byId('mobile-nav');
  function closeMenu() {
    if (!menu || !menuButton) return;
    menu.hidden = true;
    menuButton.setAttribute('aria-expanded', 'false');
    menuButton.setAttribute('aria-label', 'Open navigation');
  }
  menuButton?.addEventListener('click', () => {
    menu.hidden = !menu.hidden;
    menuButton.setAttribute('aria-expanded', String(!menu.hidden));
    menuButton.setAttribute('aria-label', menu.hidden ? 'Open navigation' : 'Close navigation');
  });
  menu?.addEventListener('click', event => { if (event.target.closest('a')) closeMenu(); });
  document.addEventListener('keydown', event => {
    if (event.key === 'Escape' && menu && !menu.hidden) { closeMenu(); menuButton.focus(); }
  });
  document.addEventListener('click', event => { if (menu && !menu.hidden && !event.target.closest('.site-header')) closeMenu(); });

  const reducedMotion = matchMedia('(prefers-reduced-motion: reduce)');
  const motionButton = byId('motion-toggle');
  const hero = byId('home');
  let motionPaused = reducedMotion.matches, heroVisible = true;
  function updateMotion() {
    document.body.classList.toggle('motion-paused', motionPaused);
    document.body.classList.toggle('page-paused', document.hidden);
    document.body.classList.toggle('hero-offscreen', !heroVisible);
    if (motionButton) {
      motionButton.setAttribute('aria-pressed', String(motionPaused));
      motionButton.setAttribute('aria-label', motionPaused ? 'Resume scene animation' : 'Pause scene animation');
      motionButton.title = motionPaused ? 'Resume animation' : 'Pause animation';
    }
  }
  motionButton?.addEventListener('click', () => { motionPaused = !motionPaused; updateMotion(); });
  reducedMotion.addEventListener('change', () => { motionPaused = reducedMotion.matches; updateMotion(); });
  document.addEventListener('visibilitychange', updateMotion);
  if (hero && 'IntersectionObserver' in window) new IntersectionObserver(entries => {
    heroVisible = entries[0].isIntersecting; updateMotion();
  }).observe(hero);
  updateMotion();

  const arenas = [
    ['01-colosseum.png','Sunstone Colosseum','Golden sandstone, red banners and a sunlit fighting floor.'],
    ['02-forest-ruins.png','Verdant Ruins','An ancient stone court beneath a green forest canopy.'],
    ['03-crystal-cavern.png','Azure Crystal Hollow','Blue crystals light the quiet depths of a cavern.'],
    ['04-moonlit-courtyard.png','Moonveil Courtyard','Moonlight falls across a secluded gothic courtyard.'],
    ['05-volcanic-arena.png','Emberfall Arena','A basalt terrace overlooks a glowing volcanic valley.'],
    ['06-castle-cliff.png','Mistwater Citadel','Dry rocky ground above the lake, castle and waterfalls.'],
    ['07-snowbound-arena.png','Frostpeak Sanctuary','Snow-dusted ruins beneath distant alpine peaks.'],
    ['08-desert-arena.png','Windscar Mesa','Sandstone arches rise above an open desert plateau.']
  ];
  let arenaIndex = 0, requestedArena = 0;
  function changeArena(direction) {
    requestedArena = (requestedArena + direction + arenas.length) % arenas.length;
    const nextIndex = requestedArena;
    const [file,name,description] = arenas[nextIndex];
    const preload = new Image();
    preload.onload = () => {
      if (nextIndex !== requestedArena) return;
      arenaIndex = nextIndex;
      const image = byId('arena-image');
      image.src = preload.src; image.alt = name;
      byId('arena-name').textContent = name; byId('arena-description').textContent = description;
      byId('arena-count').textContent = `${arenaIndex + 1} / ${arenas.length}`;
    };
    preload.onerror = () => { if (nextIndex === requestedArena) requestedArena = arenaIndex; };
    preload.src = 'assets/homepage/arenas/' + file;
  }
  byId('arena-prev')?.addEventListener('click', () => changeArena(-1));
  byId('arena-next')?.addEventListener('click', () => changeArena(1));

  const stage = byId('demo-stage');
  let timers = [];
  function stopDemo() { timers.forEach(clearTimeout); timers = []; }
  function schedule(callback, ms) { timers.push(setTimeout(callback, ms)); }
  function resetDemo() {
    stopDemo(); stage.className = 'demo-stage';
    byId('demo-hp-mage').style.width = '100%';
    byId('demo-hp-coil').style.width = '100%';
    byId('demo-caption').textContent = '';
    byId('demo-play').hidden = false; byId('demo-replay').hidden = true;
  }
  function playDemo() {
    resetDemo();
    byId('demo-play').hidden = true;
    byId('demo-caption').textContent = 'Your turn. Mage is ready.';
    schedule(() => {
      stage.classList.add('is-attacking');
      byId('demo-caption').textContent = 'Mage uses Arcane Bolt.';
    }, 700);
    schedule(() => {
      stage.classList.remove('is-attacking'); stage.classList.add('is-hit');
      byId('demo-hp-coil').style.width = '78%';
      byId('demo-caption').textContent = '22 damage. The bot takes its turn.';
    }, 1550);
    schedule(() => stage.classList.remove('is-hit'), 2050);
    schedule(() => {
      stage.classList.add('is-countering');
      byId('demo-caption').textContent = 'Coil replies with Spark Bolt.';
    }, 2800);
    schedule(() => {
      stage.classList.remove('is-countering'); stage.classList.add('is-counter-hit');
      byId('demo-hp-mage').style.width = '78%';
      byId('demo-caption').textContent = '22 damage. Your turn again.';
    }, 3650);
    schedule(() => stage.classList.remove('is-counter-hit'), 4150);
    schedule(() => {
      byId('demo-caption').textContent = 'Your turn. Make your next move count.';
      byId('demo-replay').hidden = false;
    }, 5200);
  }
  byId('demo-play')?.addEventListener('click', playDemo);
  byId('demo-replay')?.addEventListener('click', playDemo);
  document.addEventListener('visibilitychange', () => {
    if (document.hidden && stage) {
      resetDemo();
    }
  });
  window.addEventListener('pagehide', stopDemo);
})();
