/* Theme/lang via URL params + localStorage lock */

(function(){
  var savedTheme=localStorage.getItem('nt-theme')||'light';
  document.documentElement.classList.toggle('dark',savedTheme==='dark');
  document.getElementById('themeToggle').addEventListener('click',function(){
    var isDark=document.documentElement.classList.toggle('dark');
    localStorage.setItem('nt-theme',isDark?'dark':'light');
  });

  var savedLang=localStorage.getItem('nt-lang')||'ru';
  document.documentElement.setAttribute('lang',savedLang);
  document.querySelectorAll('.lang-btn').forEach(function(btn){
    btn.classList.toggle('active',btn.dataset.lang===savedLang);
    btn.addEventListener('click',function(){
      var lang=this.dataset.lang;
      document.documentElement.setAttribute('lang',lang);
      localStorage.setItem('nt-lang',lang);
      document.querySelectorAll('.lang-btn').forEach(function(b){
        b.classList.toggle('active',b.dataset.lang===lang);
      });
    });
  });

  var burger=document.getElementById('burger');
  var sideNav=document.getElementById('sideNav');
  burger.addEventListener('click',function(){
    burger.classList.toggle('open');
    sideNav.classList.toggle('open');
  });
  document.querySelectorAll('.nav-link').forEach(function(link){
    link.addEventListener('click',function(){
      burger.classList.remove('open');
      sideNav.classList.remove('open');
    });
  });

  function ntSyncLinks(){
    var theme = document.documentElement.classList.contains('dark') ? 'dark' : 'light';
    var lang  = document.documentElement.getAttribute('lang') || 'ru';
    document.querySelectorAll('a[href]').forEach(function(a){
      var href = a.getAttribute('href');
      if (!href) return;
      if (href.indexOf('http://')===0 || href.indexOf('https://')===0) return;
      if (href.indexOf('mailto:')===0 || href.indexOf('tel:')===0) return;
      if (href.indexOf('#')===0) return;
      var hashIdx = href.indexOf('#');
      var hash = hashIdx >= 0 ? href.substring(hashIdx) : '';
      var pq = hashIdx >= 0 ? href.substring(0, hashIdx) : href;
      var qIdx = pq.indexOf('?');
      var path = qIdx >= 0 ? pq.substring(0, qIdx) : pq;
      var existing = qIdx >= 0 ? pq.substring(qIdx+1) : '';
      var params = new URLSearchParams(existing);
      params.set('theme', theme);
      params.set('lang', lang);
      a.setAttribute('href', path + '?' + params.toString() + hash);
    });
  }
  ntSyncLinks();
  document.querySelectorAll('.theme-toggle, .lang-toggle, .lang-btn, #themeToggle').forEach(function(b){
    b.addEventListener('click', function(){ setTimeout(ntSyncLinks, 0); });
  });

})();
