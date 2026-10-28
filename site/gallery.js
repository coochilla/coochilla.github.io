(() => {
  'use strict';
  const gallery = document.getElementById('photos');
  const thumbs = [...gallery.querySelectorAll('.photo-thumb')];
  const image = document.getElementById('photo-main');
  const full = document.getElementById('photo-full');
  const counter = document.getElementById('photo-count');
  const caption = document.getElementById('photo-caption');
  const dialog = document.getElementById('photo-dialog');
  const expanded = document.getElementById('photo-expanded');
  const download = document.getElementById('photo-download');
  const dialogCaption = document.getElementById('photo-dialog-caption');
  let selected = 0;
  let touchStart = null;
  let returnFocus = null;
  let swiped = false;

  function show(index) {
    selected = (index + thumbs.length) % thumbs.length;
    const thumb = thumbs[selected];
    const description = thumb.querySelector('img').alt;
    const count = `${String(selected + 1).padStart(2, '0')} / ${String(thumbs.length).padStart(2, '0')}`;
    image.src = thumb.href;
    image.alt = description;
    full.href = thumb.href;
    counter.textContent = count;
    caption.textContent = thumb.dataset.caption;
    thumbs.forEach((item, i) => {
      if (i === selected) item.setAttribute('aria-current', 'true');
      else item.removeAttribute('aria-current');
    });
    if (dialog.open) {
      expanded.src = thumb.href;
      expanded.alt = description;
      download.href = thumb.href;
      dialogCaption.textContent = `${count} — ${thumb.dataset.caption}`;
    }
  }

  thumbs.forEach((thumb, i) => thumb.addEventListener('click', event => {
    event.preventDefault();
    show(i);
  }));
  for (const button of document.querySelectorAll('[data-photo-step]')) {
    button.hidden = false;
    button.addEventListener('click', () => show(selected + Number(button.dataset.photoStep)));
  }
  function keyboard(event) {
    if (event.key !== 'ArrowLeft' && event.key !== 'ArrowRight') return;
    event.preventDefault();
    show(selected + (event.key === 'ArrowRight' ? 1 : -1));
  }
  gallery.addEventListener('keydown', keyboard);
  dialog.addEventListener('keydown', keyboard);
  function swipeArea(area) {
    area.addEventListener('pointerdown', event => {
      swiped = false;
      if (event.pointerType !== 'mouse') touchStart = { x: event.clientX, y: event.clientY };
    });
    area.addEventListener('pointerup', event => {
      if (!touchStart) return;
      const dx = event.clientX - touchStart.x;
      const dy = event.clientY - touchStart.y;
      touchStart = null;
      if (Math.abs(dx) > 50 && Math.abs(dx) > Math.abs(dy) * 1.5) {
        event.preventDefault();
        swiped = true;
        show(selected + (dx < 0 ? 1 : -1));
      }
    });
    area.addEventListener('pointercancel', () => { touchStart = null; });
  }
  swipeArea(full);
  swipeArea(expanded);
  full.addEventListener('click', event => {
    if (swiped) { event.preventDefault(); swiped = false; return; }
    if (typeof dialog.showModal !== 'function') return;
    event.preventDefault();
    returnFocus = document.activeElement;
    dialog.showModal();
    document.body.classList.add('photo-open');
    show(selected);
  });
  document.getElementById('photo-close').addEventListener('click', () => dialog.close());
  dialog.addEventListener('click', event => { if (event.target === dialog) dialog.close(); });
  dialog.addEventListener('close', () => {
    document.body.classList.remove('photo-open');
    returnFocus?.focus({ preventScroll: true });
  });
  show(0);
})();
