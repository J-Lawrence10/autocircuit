/* The original SVG stays unchanged. All zooming is browser presentation only. */
(() => {
  'use strict';
  if (!('HTMLDialogElement' in window)) return; // Full-size SVG links still work.
  const dialog = document.createElement('dialog');
  dialog.className = 'figure-viewer';
  dialog.setAttribute('aria-labelledby', 'figure-viewer-title');
  dialog.innerHTML = `
    <div class="viewer-toolbar">
      <h2 class="viewer-title" id="figure-viewer-title">Figure</h2>
      <div class="viewer-controls" aria-label="Figure magnification">
        <button type="button" data-scale="fit" aria-pressed="true">Fit</button>
        <button type="button" data-scale="1" aria-pressed="false">100%</button>
        <button type="button" data-scale="1.5" aria-pressed="false">150%</button>
        <button type="button" data-scale="2" aria-pressed="false">200%</button>
        <button type="button" class="viewer-close" autofocus>Close</button>
      </div>
    </div>
    <div class="viewer-viewport" tabindex="0" aria-label="Figure; scroll to view enlarged details">
      <img class="viewer-artwork" alt="">
    </div>
    <p class="viewer-hint">Vector artwork stays sharp as you zoom. Scroll to see details; press Escape to close.</p>`;
  document.body.append(dialog);
  const artwork = dialog.querySelector('.viewer-artwork');
  const viewport = dialog.querySelector('.viewer-viewport');
  const title = dialog.querySelector('.viewer-title');
  const scales = [...dialog.querySelectorAll('[data-scale]')];
  let origin;
  let zoom = 'fit';
  let baseline = 1120;

  function resize() {
    if (!dialog.open || !artwork.naturalWidth) return;
    const style = getComputedStyle(viewport);
    const width = viewport.clientWidth - parseFloat(style.paddingLeft) - parseFloat(style.paddingRight);
    const height = viewport.clientHeight - parseFloat(style.paddingTop) - parseFloat(style.paddingBottom);
    const ratio = artwork.naturalWidth / artwork.naturalHeight;
    artwork.style.width = `${zoom === 'fit' ? Math.max(1, Math.min(width, height * ratio)) : baseline * Number(zoom)}px`;
    scales.forEach(button => button.setAttribute('aria-pressed', String(button.dataset.scale === zoom)));
  }

  artwork.addEventListener('load', resize);
  window.addEventListener('resize', resize);
  scales.forEach(button => button.addEventListener('click', () => {
    zoom = button.dataset.scale;
    resize();
    viewport.scrollTo(0, 0);
  }));
  dialog.querySelector('.viewer-close').addEventListener('click', () => dialog.close());
  dialog.addEventListener('click', event => {
    if (event.target !== dialog) return;
    const box = dialog.getBoundingClientRect();
    if (event.clientX < box.left || event.clientX > box.right || event.clientY < box.top || event.clientY > box.bottom) dialog.close();
  });
  dialog.addEventListener('close', () => {
    document.documentElement.classList.remove('figure-viewer-open');
    origin?.focus({preventScroll: true});
  });
  document.querySelectorAll('[data-figure-open]').forEach(link => {
    link.addEventListener('click', event => {
      if (event.button || event.ctrlKey || event.metaKey || event.shiftKey || event.altKey) return;
      const figure = link.closest('.paper-figure');
      const image = figure?.querySelector('.figure-artwork img');
      if (!image) return;
      event.preventDefault();
      origin = link;
      zoom = 'fit';
      baseline = Math.max(1120, image.clientWidth);
      title.textContent = image.alt;
      artwork.alt = image.alt;
      artwork.src = link.href;
      document.documentElement.classList.add('figure-viewer-open');
      dialog.showModal();
      resize();
      viewport.scrollTo(0, 0);
    });
  });
})();
