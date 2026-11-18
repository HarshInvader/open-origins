/* Open Origins site script: theme switch, phone menu, news detail level. No dependencies; works from file://. */
(function () {
  var root = document.documentElement;

  // Theme: Auto -> Light -> Dark. Saved per browser; works without storage.
  var btn = document.getElementById('theme'), label = document.getElementById('theme-label');
  function current() { return root.getAttribute('data-theme') || 'auto'; }
  function show() {
    var t = current(), name = t === 'auto' ? 'Auto' : t === 'light' ? 'Light' : 'Dark';
    if (label) label.textContent = name;
    if (btn) btn.setAttribute('aria-label', 'Colour theme: ' + name.toLowerCase() + '. Press to change.');
  }
  if (btn) btn.addEventListener('click', function () {
    var next = { auto: 'light', light: 'dark', dark: 'auto' }[current()];
    if (next === 'auto') root.removeAttribute('data-theme'); else root.setAttribute('data-theme', next);
    try { if (next === 'auto') localStorage.removeItem('oo-theme'); else localStorage.setItem('oo-theme', next); } catch (e) {}
    show();
  });
  show();

  // Phone menu: the button toggles the list; Escape closes it and returns focus; a click outside the header closes it.
  var head = document.getElementById('site-head'), menu = document.getElementById('menu-btn');
  function setMenu(open, refocus) {
    if (!head || !menu) return;
    head.classList.toggle('open', open);
    menu.setAttribute('aria-expanded', String(open));
    if (!open && refocus) menu.focus();
  }
  if (menu) {
    menu.addEventListener('click', function () { setMenu(menu.getAttribute('aria-expanded') !== 'true'); });
    document.addEventListener('keydown', function (e) { if (e.key === 'Escape' && menu.getAttribute('aria-expanded') === 'true') setMenu(false, true); });
    document.addEventListener('click', function (e) { if (!head.contains(e.target)) setMenu(false); });
    window.matchMedia('(min-width: 901px)').addEventListener('change', function (m) { if (m.matches) setMenu(false); });
  }

  // Grouped menus (Research, Resources): open on hover (CSS) or a tap; one open at a time; Escape or a tap elsewhere closes.
  var dds = [].slice.call(document.querySelectorAll('.site-nav .dd'));
  function ddClose(d) { d.classList.remove('open'); d.querySelector('button').setAttribute('aria-expanded', 'false'); }
  dds.forEach(function (d) {
    var b = d.querySelector('button');
    b.addEventListener('click', function (e) {
      e.stopPropagation(); var on = !d.classList.contains('open'); dds.forEach(ddClose);
      if (on) { d.classList.add('open'); b.setAttribute('aria-expanded', 'true'); }
    });
  });
  document.addEventListener('click', function (e) { dds.forEach(function (d) { if (!d.contains(e.target)) ddClose(d); }); });
  document.addEventListener('keydown', function (e) { if (e.key === 'Escape') dds.forEach(ddClose); });

  // News: one detail level for the whole feed (a sentence, plain words, technical); remembered per viewer.
  var zb = [].slice.call(document.querySelectorAll('.zoombar button'));
  if (zb.length) {
    var feeds = [].slice.call(document.querySelectorAll('.news-feed'));
    var setZoom = function (z) {
      feeds.forEach(function (f) { f.setAttribute('data-zoom', z); });
      zb.forEach(function (b) { b.setAttribute('aria-pressed', String(b.getAttribute('data-zoom') === z)); });
      try { localStorage.setItem('oo-zoom', z); } catch (e) {}
    };
    zb.forEach(function (b) { b.addEventListener('click', function () { setZoom(b.getAttribute('data-zoom')); }); });
    try { var z0 = localStorage.getItem('oo-zoom'); if (z0) setZoom(z0); } catch (e) {}
  }
})();
