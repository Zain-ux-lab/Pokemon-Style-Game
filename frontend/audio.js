(() => {
  const toggle = document.getElementById('sound-toggle');
  const music = document.getElementById('theme-music');
  if (!toggle || !music) return;
  const status = document.getElementById('audio-status');
  const preferences = {music:25, effects:40, enabled:true};
  try {
    const saved = JSON.parse(localStorage.getItem('clashbound-audio') || '{}');
    for (const kind of ['music','effects']) {
      if (Number.isFinite(saved[kind])) preferences[kind] = Math.min(100, Math.max(0, saved[kind]));
    }
    if (typeof saved.enabled === 'boolean') preferences.enabled = saved.enabled;
  } catch { /* Sound remains usable when browser storage is unavailable. */ }
  let enabled = false, context, fadeFrame, loading = false;
  const save = () => {
    try { localStorage.setItem('clashbound-audio', JSON.stringify(preferences)); } catch {}
  };
  const render = () => {
    toggle.setAttribute('aria-pressed', String(preferences.enabled));
    toggle.querySelector('span').textContent = preferences.enabled ? 'Sound on' : 'Sound off';
    toggle.setAttribute('aria-label', preferences.enabled ? 'Turn sound off' : 'Turn sound on');
  };
  function fadeMusic(target, duration = 350, pause = false) {
    cancelAnimationFrame(fadeFrame);
    const start = performance.now(), initial = music.volume;
    function frame(now) {
      const progress = Math.max(0, Math.min(1, (now - start) / duration));
      music.volume = initial + (target - initial) * progress;
      if (progress < 1) fadeFrame = requestAnimationFrame(frame);
      else if (pause) music.pause();
    }
    fadeFrame = requestAnimationFrame(frame);
  }
  function playClick(enter = false) {
    if (!enabled || !context || context.state !== 'running' || !preferences.effects) return;
    const notes = enter ? [523.25,659.25,783.99] : [783.99,1174.66];
    notes.forEach((frequency, index) => {
      const start = context.currentTime + index * (enter ? .035 : .006);
      const oscillator = context.createOscillator(), gain = context.createGain();
      oscillator.type = 'sine'; oscillator.frequency.setValueAtTime(frequency, start);
      gain.gain.setValueAtTime(.0001, start);
      gain.gain.exponentialRampToValueAtTime(.035 * preferences.effects / 100, start + .004);
      gain.gain.exponentialRampToValueAtTime(.0001, start + (enter ? .24 : .075));
      oscillator.connect(gain); gain.connect(context.destination);
      oscillator.start(start); oscillator.stop(start + .28);
    });
  }
  async function enableSound() {
    if (loading || !preferences.enabled || (enabled && context?.state === 'running')) return;
    loading = true; toggle.disabled = true;
    cancelAnimationFrame(fadeFrame);
    try {
      const AudioContext = window.AudioContext || window.webkitAudioContext;
      let resume;
      try {
        if (!context && AudioContext) context = new AudioContext();
        resume = context ? context.resume() : Promise.reject(new Error('Click sounds unavailable'));
      } catch (error) { resume = Promise.reject(error); }
      music.volume = 0;
      // Both requests are made during the user gesture, including on Safari.
      const results = await Promise.allSettled([resume, music.play()]);
      if (!preferences.enabled) { music.pause(); return; }
      const effectsReady = results[0].status === 'fulfilled';
      const musicReady = results[1].status === 'fulfilled';
      enabled = effectsReady || musicReady;
      if (musicReady) fadeMusic(preferences.music / 100, 800);
      status.textContent = musicReady && effectsReady ? 'Music and click sounds enabled.'
        : musicReady ? 'Music enabled. Click sounds are unavailable in this browser.'
        : effectsReady ? 'Click sounds enabled. Music could not start; toggle sound to retry.'
        : 'Music is enabled. Click or tap to start playback.';
      render(); playClick();
    } catch {
      enabled = false; render();
      status.textContent = 'Sound could not start. Toggle sound to try again.';
    } finally {
      loading = false; toggle.disabled = false;
    }
  }
  toggle.addEventListener('click', () => {
    preferences.enabled = !preferences.enabled;
    save(); render();
    if (preferences.enabled) { enableSound(); return; }
    enabled = false; fadeMusic(0, 250, true);
    status.textContent = 'Sound is muted.';
  });
  for (const kind of ['music','effects']) {
    const input = document.getElementById(`${kind}-volume`);
    const output = document.getElementById(`${kind}-value`);
    if (!input || !output) continue;
    input.value = preferences[kind]; output.textContent = preferences[kind] + '%';
    input.addEventListener('input', () => {
      preferences[kind] = Number(input.value); output.textContent = input.value + '%'; save();
      if (kind === 'music' && enabled) fadeMusic(preferences.music / 100, 150);
    });
  }
  function startOnInteraction(event) {
    if (!preferences.enabled || event.target.closest('#sound-toggle')) return;
    enableSound();
  }
  document.addEventListener('pointerdown', startOnInteraction);
  document.addEventListener('keydown', event => {
    if (!event.repeat && !event.ctrlKey && !event.metaKey && !event.altKey) startOnInteraction(event);
  });
  if (preferences.enabled) {
    music.volume = preferences.music / 100;
    music.play().then(() => {
      if (!preferences.enabled || document.hidden) { music.pause(); return; }
      enabled = true; render(); status.textContent = 'Music enabled.';
    }).catch(() => {
      if (preferences.enabled) status.textContent = 'Music is enabled. Click or tap to start playback.';
    });
  } else status.textContent = 'Sound is muted.';
  document.addEventListener('click', event => {
    const control = event.target.closest('button, a, summary');
    if (!control || control === toggle || control.disabled) return;
    playClick(control.hasAttribute('data-play'));
    const anchor = control.closest('a[href]');
    if (!enabled || !anchor || event.defaultPrevented || event.metaKey || event.ctrlKey || event.shiftKey || event.altKey || event.button !== 0 || anchor.target) return;
    const url = new URL(anchor.href, location.href);
    if (url.origin !== location.origin || (url.pathname === location.pathname && url.hash) || anchor.hasAttribute('download')) return;
    event.preventDefault(); fadeMusic(0, 170, true);
    window.setTimeout(() => location.assign(anchor.href), 180);
  });
  document.addEventListener('visibilitychange', () => {
    cancelAnimationFrame(fadeFrame);
    if (document.hidden) { music.pause(); if (context) context.suspend().catch(() => {}); }
    else if (preferences.enabled) {
      if (context) context.resume().catch(() => {});
      music.play().then(() => {
        if (!preferences.enabled || document.hidden) { music.pause(); return; }
        fadeMusic(preferences.music / 100, 600);
      }).catch(() => {
        enabled = false; render(); status.textContent = 'Enable sound to resume listening.';
      });
    }
  });
  render();
})();
