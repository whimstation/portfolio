/* Тема: по системе, пока посетитель сам не переключит. Язык: ?lang=en|ru или сохранённый. */
(function () {
  var d = document.documentElement;
  function store(k, v) { try { localStorage.setItem(k, v); } catch (e) {} }
  function stored(k) { try { return localStorage.getItem(k); } catch (e) { return null; } }

  // тема
  var mq = window.matchMedia ? matchMedia('(prefers-color-scheme: dark)') : null;
  document.getElementById('themeToggle').addEventListener('click', function () {
    store('nt-theme', d.classList.toggle('dark') ? 'dark' : 'light');
  });
  if (mq && mq.addEventListener) mq.addEventListener('change', function (e) {
    if (!stored('nt-theme')) d.classList.toggle('dark', e.matches);
  });
  requestAnimationFrame(function () { document.body.classList.add('ready'); });

  // язык
  function setLang(l) {
    d.setAttribute('lang', l);
    document.querySelectorAll('.lang-btn').forEach(function (b) { b.classList.toggle('active', b.dataset.lang === l); });
  }
  setLang(d.getAttribute('lang') || 'ru');
  document.querySelectorAll('.lang-btn').forEach(function (b) {
    b.addEventListener('click', function () { setLang(b.dataset.lang); store('nt-lang', b.dataset.lang); });
  });

  // мобильное меню
  var burger = document.getElementById('burger'), nav = document.getElementById('sideNav');
  burger.addEventListener('click', function () { burger.classList.toggle('open'); nav.classList.toggle('open'); });
  nav.querySelectorAll('a').forEach(function (a) {
    a.addEventListener('click', function () { burger.classList.remove('open'); nav.classList.remove('open'); });
  });

  // подсветка раздела в меню при прокрутке (главная)
  var links = {};
  nav.querySelectorAll('a[href^="#"]').forEach(function (a) { links[a.getAttribute('href').slice(1)] = a; });
  if ('IntersectionObserver' in window && Object.keys(links).length) {
    var io = new IntersectionObserver(function (es) {
      es.forEach(function (e) {
        if (e.isIntersecting && links[e.target.id]) {
          Object.keys(links).forEach(function (k) { links[k].classList.remove('active'); });
          links[e.target.id].classList.add('active');
        }
      });
    }, { rootMargin: '-30% 0px -60% 0px' });
    Object.keys(links).forEach(function (id) { var s = document.getElementById(id); if (s) io.observe(s); });
  }

  // видео: один играет — остальные на паузе
  function stopOthers(except) {
    document.querySelectorAll('video.vid').forEach(function (v) { if (v !== except && !v.paused) v.pause(); });
  }
  document.querySelectorAll('.vid-cover').forEach(function (btn) {
    btn.addEventListener('click', function () {
      var box = btn.parentNode, v = box.querySelector('video.vid');
      if (v) {
        v.controls = true; box.classList.add('playing'); stopOthers(v); v.play();
        v.addEventListener('play', function () { stopOthers(v); });
        return;
      }
      var src = btn.getAttribute('data-embed');
      if (!src) return;
      var f = document.createElement('iframe');
      f.src = src; f.allow = 'autoplay; fullscreen; picture-in-picture'; f.allowFullscreen = true;
      box.appendChild(f); box.classList.add('playing');
      var p = box.querySelector('.vid-poster'); if (p) p.remove();
    });
  });

  document.querySelectorAll('.to-top').forEach(function (a) {
    a.addEventListener('click', function (e) { e.preventDefault(); window.scrollTo({ top: 0, behavior: 'smooth' }); });
  });
})();
