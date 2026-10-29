(() => {
  'use strict';
  const dialog = document.getElementById('photo-dialog');
  const expanded = document.getElementById('photo-expanded');
  const download = document.getElementById('photo-download');
  const dialogCounter = document.getElementById('photo-dialog-count');
  const dialogDescription = document.getElementById('photo-dialog-description');
  const dialogTitle = document.getElementById('photo-dialog-title');
  let active = null;
  let returnFocus = null;

  function describe(container, thumb) {
    if (!container) return;
    container.replaceChildren();
    container.hidden = !thumb.dataset.description;
    if (container.hidden) return;
    const title = document.createElement('h3');
    const text = document.createElement('p');
    title.textContent = thumb.dataset.title;
    text.textContent = thumb.dataset.description;
    container.append(title, text);
  }
  function swipe(area, callback) {
    let start = null;
    let swiped = false;
    area.addEventListener('pointerdown', event => {
      swiped = false;
      if (event.pointerType !== 'mouse') start = {x: event.clientX, y: event.clientY};
    });
    area.addEventListener('pointerup', event => {
      if (!start) return;
      const dx = event.clientX - start.x, dy = event.clientY - start.y;
      start = null;
      if (Math.abs(dx) > 50 && Math.abs(dx) > Math.abs(dy) * 1.5) {
        event.preventDefault(); swiped = true; callback(dx < 0 ? 1 : -1);
      }
    });
    area.addEventListener('pointercancel', () => {start = null;});
    return () => {const value = swiped; swiped = false; return value;};
  }
  document.querySelectorAll('[data-gallery]').forEach(gallery => {
    const thumbs = [...gallery.querySelectorAll('.photo-thumb')];
    const image = gallery.querySelector('[data-gallery-main]');
    const full = gallery.querySelector('[data-gallery-full]');
    const counter = gallery.querySelector('[data-gallery-count]');
    const description = gallery.querySelector('[data-gallery-description]');
    let selected = 0;
    function show(index) {
      selected = (index + thumbs.length) % thumbs.length;
      const thumb = thumbs[selected];
      const alt = thumb.querySelector('img').alt;
      const count = `${String(selected + 1).padStart(2, '0')} / ${String(thumbs.length).padStart(2, '0')}`;
      image.src = thumb.href; image.alt = alt; full.href = thumb.href; counter.textContent = count;
      describe(description, thumb);
      thumbs.forEach((item, i) => {
        if (i === selected) item.setAttribute('aria-current', 'true');
        else item.removeAttribute('aria-current');
      });
      if (dialog.open && active === api) {
        expanded.src = thumb.href; expanded.alt = alt; download.href = thumb.href;
        dialogCounter.textContent = count;
        dialogTitle.textContent = gallery.querySelector('h2').textContent;
        describe(dialogDescription, thumb);
      }
    }
    const api = {step: delta => show(selected + delta)};
    thumbs.forEach((thumb, i) => thumb.addEventListener('click', event => {event.preventDefault(); show(i);}));
    gallery.querySelectorAll('[data-photo-step]').forEach(button => {
      button.hidden = false;
      button.addEventListener('click', () => api.step(Number(button.dataset.photoStep)));
    });
    gallery.addEventListener('keydown', event => {
      if (!['ArrowLeft', 'ArrowRight'].includes(event.key)) return;
      event.preventDefault(); api.step(event.key === 'ArrowRight' ? 1 : -1);
    });
    const didSwipe = swipe(full, api.step);
    full.addEventListener('click', event => {
      if (didSwipe()) {event.preventDefault(); return;}
      if (typeof dialog.showModal !== 'function') return;
      event.preventDefault(); returnFocus = document.activeElement; active = api;
      dialog.showModal(); document.body.classList.add('photo-open'); show(selected);
    });
    show(0);
  });
  dialog.querySelectorAll('[data-dialog-step]').forEach(button => button.addEventListener('click', () => active?.step(Number(button.dataset.dialogStep))));
  dialog.addEventListener('keydown', event => {
    if (!['ArrowLeft', 'ArrowRight'].includes(event.key)) return;
    event.preventDefault(); active?.step(event.key === 'ArrowRight' ? 1 : -1);
  });
  swipe(expanded, delta => active?.step(delta));
  document.getElementById('photo-close').addEventListener('click', () => dialog.close());
  dialog.addEventListener('click', event => {if (event.target === dialog) dialog.close();});
  dialog.addEventListener('close', () => {
    document.body.classList.remove('photo-open'); active = null;
    returnFocus?.focus({preventScroll: true});
  });
})();
