/* =========================================================================
   FRIZZA Refrigerantes — scripts compartilhados
   Bibliotecas (via CDN, carregadas com defer): GSAP + ScrollTrigger, Lenis,
   SplitType. Tudo aqui funciona com degradação elegante: se uma biblioteca
   não carregar, ou se o usuário pedir menos movimento, o conteúdo continua
   visível e utilizável.
   ========================================================================= */
(() => {
  'use strict';
  window.__frizzaReady = true;

  const d = document;
  const html = d.documentElement;
  const reduce = window.matchMedia('(prefers-reduced-motion: reduce)').matches;
  const finePointer = window.matchMedia('(hover: hover) and (pointer: fine)').matches;
  const hasGSAP = !!(window.gsap && window.ScrollTrigger);
  const motion = hasGSAP && !reduce;

  if (hasGSAP) gsap.registerPlugin(ScrollTrigger);
  if (!motion) html.classList.remove('js-motion');

  const $ = (s, c = d) => c.querySelector(s);
  const $$ = (s, c = d) => Array.from(c.querySelectorAll(s));
  const safe = (name, fn) => { try { return fn(); } catch (err) { console.warn('[FRIZZA] ' + name, err); } };

  /* Cores da cortina de transição por página de destino */
  const PAGE_COLORS = {
    'index.html': '#FF6B2B',
    'sabores.html': '#FFD23F',
    'sabor-laranja-bahia.html': '#FF8C42',
    'sabor-acai-guarana.html': '#5B2C6F',
    'sabor-limao-hortela.html': '#00BFA6',
    'sabor-pessego-gengibre.html': '#FFAB76',
    'sabor-uva-rose.html': '#4A2135',
    'historia.html': '#2EC4B6',
    'onde-encontrar.html': '#FF6B2B',
    'frizzalovers.html': '#7B2D8E',
    'contato.html': '#FFD23F',
    'checkout.html': '#FFD23F'
  };

  let lenis = null;
  let menuOpen = false;

  /* ---------------------------------------------------------------------
     1. SLOTS DE IMAGEM
     Cada elemento com [data-img] tenta carregar o arquivo indicado. Se o
     arquivo existir em /assets/img/, a imagem aparece e o placeholder some.
     ------------------------------------------------------------------- */
  function loadSlot(el) {
    if (el.dataset.loading) return;
    el.dataset.loading = '1';
    const img = new Image();
    img.decoding = 'async';
    img.onload = () => {
      img.alt = el.dataset.alt || el.getAttribute('aria-label') || '';
      if (el.closest('.logo')) img.alt = ''; // o link do logo já tem aria-label
      if (el.closest('[aria-hidden="true"]')) img.alt = '';
      el.removeAttribute('role');
      el.removeAttribute('aria-label');
      el.appendChild(img);
      requestAnimationFrame(() => el.classList.add('is-loaded'));
    };
    img.onerror = () => { el.dataset.missing = '1'; };
    img.src = el.dataset.img;
  }

  function initImageSlots() {
    const slots = $$('[data-img]');
    if (!('IntersectionObserver' in window)) { slots.forEach(loadSlot); return; }
    const io = new IntersectionObserver((entries) => {
      entries.forEach((e) => {
        if (e.isIntersecting) { io.unobserve(e.target); loadSlot(e.target); }
      });
    }, { rootMargin: '600px 0px' });
    slots.forEach((s) => {
      // logos e itens fora do fluxo (menu/lightbox) carregam direto
      if (s.closest('.logo, .preloader')) loadSlot(s); else io.observe(s);
    });
  }

  /* ---------------------------------------------------------------------
     2. PRELOADER (somente na primeira visita da sessão)
     ------------------------------------------------------------------- */
  function initPreloader() {
    const pl = $('.preloader');
    try { sessionStorage.setItem('frizza-visited', '1'); } catch (e) { /* modo privado */ }
    if (!pl || !html.classList.contains('has-preloader')) return Promise.resolve();

    return new Promise((resolve) => {
      const start = performance.now();
      let finished = false;
      const finish = () => {
        if (finished) return;
        finished = true;
        const wait = Math.max(0, 1700 - (performance.now() - start));
        setTimeout(() => {
          pl.classList.add('is-done');
          resolve();
          setTimeout(() => html.classList.remove('has-preloader'), 1100);
        }, wait);
      };
      if (d.readyState === 'complete') finish();
      else window.addEventListener('load', finish, { once: true });
      setTimeout(finish, 4200); // nunca prender o usuário
    });
  }

  /* ---------------------------------------------------------------------
     3. TRANSIÇÃO ENTRE PÁGINAS (onda colorida + bolhas, via sessionStorage)
     ------------------------------------------------------------------- */
  function pageName(pathname) {
    const last = pathname.split('/').pop();
    return last === '' ? 'index.html' : last;
  }

  function initPageTransition() {
    const pt = $('.page-transition');
    if (!pt) return Promise.resolve();

    window.addEventListener('pageshow', (e) => {
      if (e.persisted) {
        pt.classList.remove('is-covering', 'is-leaving');
        html.classList.remove('pt-enter');
      }
    });

    if (!reduce) {
      d.addEventListener('click', (e) => {
        const a = e.target.closest('a[href]');
        if (!a || e.defaultPrevented || e.button !== 0 || e.metaKey || e.ctrlKey || e.shiftKey || e.altKey) return;
        if ((a.target && a.target !== '_self') || a.hasAttribute('download') || a.dataset.demo !== undefined) return;
        const url = new URL(a.getAttribute('href'), location.href);
        if (url.protocol !== location.protocol || url.host !== location.host) return;
        if (!/\.html$|\/$/.test(url.pathname)) return;
        if (url.pathname === location.pathname && url.hash) return; // âncora na mesma página
        e.preventDefault();
        const color = PAGE_COLORS[pageName(url.pathname)] || '#FF6B2B';
        pt.style.setProperty('--pt-color', color);
        try { sessionStorage.setItem('frizza-pt', color); } catch (err) { /* ignora */ }
        if (menuOpen) closeMenu && closeMenu(false);
        pt.classList.add('is-covering');
        setTimeout(() => { location.href = url.href; }, 720);
      });
    }

    if (!html.classList.contains('pt-enter')) return Promise.resolve();
    try { sessionStorage.removeItem('frizza-pt'); } catch (e) { /* ignora */ }
    return new Promise((resolve) => {
      requestAnimationFrame(() => requestAnimationFrame(() => {
        pt.classList.add('is-leaving');
        html.classList.remove('pt-enter');
        setTimeout(resolve, 250);
        setTimeout(() => pt.classList.remove('is-leaving'), 950);
      }));
    });
  }

  /* ---------------------------------------------------------------------
     4. SCROLL SUAVE (Lenis) + âncoras
     ------------------------------------------------------------------- */
  function initLenis() {
    if (reduce || !window.Lenis) return;
    lenis = new Lenis({ duration: 1.15, easing: (t) => Math.min(1, 1.001 - Math.pow(2, -10 * t)), smoothWheel: true });
    if (hasGSAP) {
      lenis.on('scroll', ScrollTrigger.update);
      gsap.ticker.add((time) => lenis.raf(time * 1000));
      gsap.ticker.lagSmoothing(0);
    } else {
      const raf = (t) => { lenis.raf(t); requestAnimationFrame(raf); };
      requestAnimationFrame(raf);
    }
  }

  function initAnchors() {
    d.addEventListener('click', (e) => {
      const a = e.target.closest('a[href^="#"]');
      if (!a) return;
      const id = a.getAttribute('href');
      if (id.length < 2) return;
      const target = d.getElementById(id.slice(1));
      if (!target) return;
      e.preventDefault();
      if (lenis) lenis.scrollTo(target, { offset: -90 });
      else target.scrollIntoView({ behavior: reduce ? 'auto' : 'smooth' });
      if (!target.hasAttribute('tabindex')) target.setAttribute('tabindex', '-1');
      target.focus({ preventScroll: true });
      history.replaceState(null, '', id);
    });
  }

  /* ---------------------------------------------------------------------
     5. HEADER (blur ao rolar, esconde/mostra) e MENU MOBILE
     ------------------------------------------------------------------- */
  function initHeader() {
    const h = $('.site-header');
    if (!h) return;
    let last = window.scrollY;
    const onScroll = () => {
      const y = window.scrollY;
      h.classList.toggle('is-scrolled', y > 30);
      if (!menuOpen && y > last + 2 && y > 320) h.classList.add('is-hidden');
      else if (y < last - 4 || y <= 320) h.classList.remove('is-hidden');
      last = y;
    };
    window.addEventListener('scroll', onScroll, { passive: true });
    h.addEventListener('focusin', () => h.classList.remove('is-hidden'));
    onScroll();
  }

  let closeMenu = null;
  function initMenu() {
    const btn = $('.menu-toggle');
    const menu = $('#mobile-menu');
    if (!btn || !menu) return;
    const outside = [$('main'), $('.site-footer')].filter(Boolean);
    const set = (open, returnFocus = true) => {
      menuOpen = open;
      btn.setAttribute('aria-expanded', String(open));
      btn.setAttribute('aria-label', open ? 'Fechar menu' : 'Abrir menu');
      menu.classList.toggle('is-open', open);
      menu.inert = !open;
      menu.setAttribute('aria-hidden', String(!open));
      html.classList.toggle('menu-open', open);
      outside.forEach((el) => { el.inert = open; });
      if (lenis) open ? lenis.stop() : lenis.start();
      if (open) {
        $('.site-header').classList.remove('is-hidden');
        setTimeout(() => { const f = menu.querySelector('a'); f && f.focus(); }, 380);
      } else if (returnFocus) btn.focus();
    };
    closeMenu = set;
    menu.inert = true;
    btn.addEventListener('click', () => set(!menuOpen));
    d.addEventListener('keydown', (e) => { if (e.key === 'Escape' && menuOpen) set(false); });
    window.matchMedia('(min-width: 1140px)').addEventListener('change', (e) => { if (e.matches && menuOpen) set(false, false); });
  }

  /* ---------------------------------------------------------------------
     6. CURSOR BOLHA, BOTÕES MAGNÉTICOS, TILT 3D (somente desktop)
     ------------------------------------------------------------------- */
  function initCursor() {
    if (!finePointer || !motion) return;
    const c = d.createElement('div');
    c.className = 'cursor';
    c.setAttribute('aria-hidden', 'true');
    c.innerHTML = '<div class="cursor__dot"><span class="cursor__label">ver</span></div>';
    d.body.appendChild(c);
    html.classList.add('has-cursor');
    const label = $('.cursor__label', c);
    const xTo = gsap.quickTo(c, 'x', { duration: 0.35, ease: 'power3' });
    const yTo = gsap.quickTo(c, 'y', { duration: 0.35, ease: 'power3' });
    window.addEventListener('pointermove', (e) => { xTo(e.clientX); yTo(e.clientY); c.classList.remove('is-hidden'); }, { passive: true });
    d.addEventListener('pointerover', (e) => {
      const t = e.target.closest('[data-cursor], a, button, input, select, textarea, label, summary');
      const view = !!(t && t.dataset.cursor);
      if (view) label.textContent = t.dataset.cursor;
      c.classList.toggle('is-view', view);
      c.classList.toggle('is-link', !!t && !view);
    });
    d.documentElement.addEventListener('pointerleave', () => c.classList.add('is-hidden'));
  }

  function initMagnetic() {
    if (!finePointer || !motion) return;
    $$('[data-magnetic]').forEach((el) => {
      const xTo = gsap.quickTo(el, 'x', { duration: 0.6, ease: 'elastic.out(1, 0.45)' });
      const yTo = gsap.quickTo(el, 'y', { duration: 0.6, ease: 'elastic.out(1, 0.45)' });
      el.addEventListener('pointermove', (e) => {
        const r = el.getBoundingClientRect();
        xTo((e.clientX - (r.left + r.width / 2)) * 0.28);
        yTo((e.clientY - (r.top + r.height / 2)) * 0.4);
      });
      el.addEventListener('pointerleave', () => { xTo(0); yTo(0); });
    });
  }

  function initTilt() {
    if (!finePointer || !motion) return;
    $$('[data-tilt]').forEach((card) => {
      const inner = $('.product-card__inner', card) || card;
      card.addEventListener('pointermove', (e) => {
        const r = card.getBoundingClientRect();
        const px = (e.clientX - r.left) / r.width - 0.5;
        const py = (e.clientY - r.top) / r.height - 0.5;
        gsap.to(inner, { rotateX: -py * 14, rotateY: px * 16, transformPerspective: 900, duration: 0.5, ease: 'power2.out' });
      });
      card.addEventListener('pointerleave', () => gsap.to(inner, { rotateX: 0, rotateY: 0, duration: 0.8, ease: 'elastic.out(1, 0.5)' }));
    });
  }

  /* ---------------------------------------------------------------------
     7. BOLHAS DE GÁS / BRILHO DE ESPUMANTE (canvas leve, pausa fora da tela)
     ------------------------------------------------------------------- */
  function initBubbles() {
    if (reduce) return;
    $$('canvas[data-bubbles]').forEach((cv) => {
      const ctx = cv.getContext('2d');
      if (!ctx) return;
      const sparkle = cv.dataset.bubbles === 'sparkle';
      const base = parseInt(cv.dataset.count || (sparkle ? 70 : 34), 10);
      const color = cv.dataset.color || (sparkle ? '241, 221, 181' : '255, 255, 255');
      let w = 0, h = 0, parts = [], running = false, raf = 0;

      const make = (init) => ({
        x: Math.random() * w,
        y: init ? Math.random() * h : h + 20,
        r: sparkle ? Math.random() * 1.7 + 0.4 : Math.random() * 10 + 3,
        s: sparkle ? Math.random() * 0.45 + 0.15 : Math.random() * 0.9 + 0.35,
        a: Math.random() * Math.PI * 2,
        wob: Math.random() * 0.7 + 0.2,
        o: Math.random() * 0.5 + 0.3
      });
      const resize = () => {
        const dpr = Math.min(window.devicePixelRatio || 1, 2);
        w = cv.clientWidth; h = cv.clientHeight;
        cv.width = Math.round(w * dpr); cv.height = Math.round(h * dpr);
        ctx.setTransform(dpr, 0, 0, dpr, 0, 0);
        const n = Math.round(base * Math.min(1.4, Math.max(0.45, w / 1200)));
        parts = Array.from({ length: n }, () => make(true));
      };
      const tick = () => {
        ctx.clearRect(0, 0, w, h);
        for (const p of parts) {
          p.y -= p.s;
          p.a += 0.02;
          const x = p.x + Math.sin(p.a) * p.wob * 8;
          if (p.y < -20) Object.assign(p, make(false));
          if (sparkle) {
            const tw = 0.5 + Math.sin(p.a * 3) * 0.5;
            ctx.fillStyle = `rgba(${color}, ${p.o * tw + 0.1})`;
            ctx.beginPath(); ctx.arc(x, p.y, p.r, 0, Math.PI * 2); ctx.fill();
          } else {
            ctx.strokeStyle = `rgba(${color}, ${p.o})`;
            ctx.lineWidth = 1.6;
            ctx.beginPath(); ctx.arc(x, p.y, p.r, 0, Math.PI * 2); ctx.stroke();
            ctx.fillStyle = `rgba(${color}, ${p.o * 0.5})`;
            ctx.beginPath(); ctx.arc(x - p.r * 0.35, p.y - p.r * 0.35, p.r * 0.25, 0, Math.PI * 2); ctx.fill();
          }
        }
        raf = requestAnimationFrame(tick);
      };
      const start = () => { if (!running) { running = true; raf = requestAnimationFrame(tick); } };
      const stop = () => { running = false; cancelAnimationFrame(raf); };
      resize();
      if ('ResizeObserver' in window) new ResizeObserver(resize).observe(cv);
      new IntersectionObserver((es) => es.forEach((e) => (e.isIntersecting ? start() : stop()))).observe(cv);
      d.addEventListener('visibilitychange', () => { if (d.hidden) stop(); });
    });
  }

  /* ---------------------------------------------------------------------
     8. TEXTOS ANIMADOS (SplitType) + REVEALS NO SCROLL
     ------------------------------------------------------------------- */
  const introSplits = [];

  function splitHeadings() {
    $$('[data-split]').forEach((el) => {
      if (!motion || !window.SplitType) { el.style.visibility = 'visible'; return; }
      const type = el.dataset.split || 'words';
      el.setAttribute('aria-label', el.textContent.trim().replace(/\s+/g, ' '));
      const st = new SplitType(el, { types: type === 'chars' ? 'words, chars' : 'words', tagName: 'span' });
      (st.words || []).forEach((w) => {
        w.setAttribute('aria-hidden', 'true');
        if (type === 'chars') { w.classList.add('split-line'); }
        else {
          const mask = d.createElement('span');
          mask.className = 'split-line';
          mask.style.display = 'inline-block';
          mask.style.verticalAlign = 'top';
          w.parentNode.insertBefore(mask, w);
          mask.appendChild(w);
        }
      });
      if (type === 'chars') (st.words || []).forEach((w) => { w.style.display = 'inline-block'; });
      const parts = type === 'chars' ? st.chars : st.words;
      gsap.set(el, { visibility: 'visible' });
      const anim = {
        yPercent: 115,
        rotate: type === 'chars' ? 10 : 4,
        duration: type === 'chars' ? 0.9 : 1,
        ease: type === 'chars' ? 'back.out(1.7)' : 'power4.out',
        stagger: type === 'chars' ? 0.035 : 0.07
      };
      if (el.hasAttribute('data-intro')) {
        gsap.set(parts, { yPercent: 115, rotate: anim.rotate });
        introSplits.push({ parts, anim, el });
      } else {
        gsap.from(parts, { ...anim, scrollTrigger: { trigger: el, start: 'top 88%', once: true } });
      }
      if (el.hasAttribute('data-wave')) el._chars = parts;
    });
  }

  function initReveals() {
    // destaque amarelo atrás de palavras
    const hls = $$('.hl');
    if ('IntersectionObserver' in window) {
      const io = new IntersectionObserver((es) => es.forEach((e) => { if (e.isIntersecting) { e.target.classList.add('is-in'); io.unobserve(e.target); } }), { threshold: 0.8 });
      hls.forEach((h) => io.observe(h));
    } else hls.forEach((h) => h.classList.add('is-in'));

    if (!motion) return;

    $$('[data-reveal]').forEach((el) => {
      const type = el.dataset.reveal;
      const delay = parseFloat(el.dataset.delay || 0);
      let from = { y: 60, opacity: 0 };
      let to = { y: 0, opacity: 1 };
      if (type === 'mask') { from = { clipPath: 'inset(100% 0% 0% 0%)', opacity: 1, scale: 1.08 }; to = { clipPath: 'inset(0% 0% 0% 0%)', opacity: 1, scale: 1 }; }
      if (type === 'left') { from = { x: -70, opacity: 0 }; to = { x: 0, opacity: 1 }; }
      if (type === 'right') { from = { x: 70, opacity: 0 }; to = { x: 0, opacity: 1 }; }
      if (type === 'scale') { from = { scale: 0.8, opacity: 0, rotate: -4 }; to = { scale: 1, opacity: 1, rotate: 0 }; }
      if (type === 'fade') { from = { opacity: 0 }; to = { opacity: 1 }; }
      gsap.fromTo(el, from, {
        ...to, delay, duration: type === 'mask' ? 1.4 : 1.1, ease: type === 'scale' ? 'back.out(1.6)' : 'power3.out',
        clearProps: type === 'mask' ? 'clipPath,transform' : 'transform',
        scrollTrigger: { trigger: el, start: 'top 90%', once: true }
      });
      el.classList.add('is-revealed'); // a partir daqui o GSAP controla a opacidade
    });

    $$('[data-stagger]').forEach((box) => {
      const kids = Array.from(box.children);
      gsap.fromTo(kids, { y: 70, opacity: 0, rotate: 1.5 }, {
        y: 0, opacity: 1, rotate: 0, duration: 0.95, ease: 'power3.out', stagger: 0.12,
        clearProps: 'transform',
        scrollTrigger: { trigger: box, start: 'top 88%', once: true }
      });
      box.classList.add('is-revealed');
    });

    $$('[data-parallax]').forEach((el) => {
      const s = parseFloat(el.dataset.parallax) || 0.2;
      gsap.to(el, { yPercent: -s * 100, ease: 'none', scrollTrigger: { trigger: el.closest('section') || el, start: 'top bottom', end: 'bottom top', scrub: true } });
    });

    // divisórias em onda "respiram" com o scroll
    $$('.wave--bottom').forEach((w) => {
      gsap.fromTo(w, { scaleY: 0.4 }, {
        scaleY: 1, ease: 'none',
        scrollTrigger: { trigger: w, start: 'top bottom', end: 'top 60%', scrub: true }
      });
    });
  }

  /* Manifesto: palavras ganham cor conforme o scroll (mantém <span> internos) */
  function initManifesto() {
    const el = $('[data-manifesto]');
    if (!el || !motion) return;
    const words = [];
    const walk = (node) => {
      Array.from(node.childNodes).forEach((n) => {
        if (n.nodeType === 3) {
          const frag = d.createDocumentFragment();
          n.textContent.split(/(\s+)/).forEach((part) => {
            if (!part) return;
            if (/^\s+$/.test(part)) { frag.appendChild(d.createTextNode(part)); return; }
            const s = d.createElement('span'); s.className = 'm-word'; s.textContent = part; words.push(s); frag.appendChild(s);
          });
          n.replaceWith(frag);
        } else if (n.nodeType === 1) walk(n);
      });
    };
    walk(el);
    gsap.fromTo(words, { opacity: 0.13 }, {
      opacity: 1, stagger: 0.1, ease: 'none',
      scrollTrigger: { trigger: el, start: 'top 78%', end: 'bottom 50%', scrub: true }
    });
  }

  /* ---------------------------------------------------------------------
     9. CONTADORES
     ------------------------------------------------------------------- */
  function initCounters() {
    $$('[data-count]').forEach((el) => {
      const end = parseFloat(el.dataset.count);
      const dec = parseInt(el.dataset.decimals || '0', 10);
      const pre = el.dataset.prefix || '';
      const suf = el.dataset.suffix || '';
      const fmt = (v) => pre + v.toLocaleString('pt-BR', { minimumFractionDigits: dec, maximumFractionDigits: dec }) + suf;
      if (!motion) { el.textContent = fmt(end); return; }
      const o = { v: 0 };
      el.textContent = fmt(0);
      ScrollTrigger.create({
        trigger: el, start: 'top 92%', once: true,
        onEnter: () => gsap.to(o, { v: end, duration: 2.2, ease: 'power2.out', onUpdate: () => { el.textContent = fmt(dec ? o.v : Math.round(o.v)); } })
      });
    });
  }

  /* ---------------------------------------------------------------------
     10. HOME — hero com parallax do mouse + vitrine horizontal fixada
     ------------------------------------------------------------------- */
  function initHero() {
    const hero = $('[data-hero]');
    if (!hero || !motion) return;
    const layers = $$('[data-depth]', hero);
    if (finePointer) {
      const setters = layers.map((l) => ({
        x: gsap.quickTo(l, 'x', { duration: 1.1, ease: 'power3' }),
        y: gsap.quickTo(l, 'y', { duration: 1.1, ease: 'power3' }),
        d: parseFloat(l.dataset.depth)
      }));
      hero.addEventListener('pointermove', (e) => {
        const r = hero.getBoundingClientRect();
        const px = (e.clientX - r.left) / r.width - 0.5;
        const py = (e.clientY - r.top) / r.height - 0.5;
        setters.forEach((s) => { s.x(px * s.d * 70); s.y(py * s.d * 45); });
      });
      hero.addEventListener('pointerleave', () => setters.forEach((s) => { s.x(0); s.y(0); }));
    }
    const stage = $('.hero__stage', hero);
    if (stage) gsap.to(stage, { yPercent: 14, ease: 'none', scrollTrigger: { trigger: hero, start: 'top top', end: 'bottom top', scrub: true } });
    gsap.to($('.hero__copy', hero), { yPercent: -18, opacity: 0.2, ease: 'none', scrollTrigger: { trigger: hero, start: 'top top', end: 'bottom top', scrub: true } });
  }

  function initVitrine() {
    const sec = $('[data-vitrine]');
    if (!sec) return;
    const track = $('.vitrine__track', sec);
    const panels = $$('.vitrine__panel', sec);
    const dots = $$('.vitrine__dots span', sec);
    const count = $('.vitrine__count', sec);
    const n = panels.length;
    let current = -1;
    const pad = (v) => String(v).padStart(2, '0');
    const setActive = (i) => {
      if (i === current) return;
      current = i;
      const p = panels[i];
      if (motion) gsap.to(sec, { backgroundColor: p.dataset.color, color: p.dataset.fg, duration: 0.7, ease: 'power2.out', overwrite: true });
      else { sec.style.backgroundColor = p.dataset.color; sec.style.color = p.dataset.fg; }
      dots.forEach((dot, j) => dot.classList.toggle('is-active', j === i));
      if (count) count.textContent = `${pad(i + 1)} / ${pad(n)}`;
    };
    setActive(0);

    if (!motion) {
      track.addEventListener('scroll', () => {
        setActive(Math.max(0, Math.min(n - 1, Math.round(track.scrollLeft / track.clientWidth))));
      }, { passive: true });
      return;
    }

    sec.classList.add('is-pinned');
    const cans = panels.map((p) => $('.vitrine__can', p));
    const dist = () => Math.max(0, track.scrollWidth - window.innerWidth);
    const st = gsap.to(track, {
      x: () => -dist(), ease: 'none',
      scrollTrigger: {
        trigger: sec, start: 'top top', end: () => '+=' + dist(), pin: true, scrub: 0.8,
        invalidateOnRefresh: true, anticipatePin: 1,
        snap: { snapTo: 1 / (n - 1), duration: { min: 0.2, max: 0.6 }, delay: 0.08, ease: 'power1.inOut' },
        onUpdate: (self) => {
          const prog = self.progress * (n - 1);
          setActive(Math.round(prog));
          cans.forEach((c, i) => {
            if (!c) return;
            const off = prog - i;
            gsap.set(c, { rotation: off * -28, y: Math.min(Math.abs(off), 1.2) * 50, scale: 1 - Math.min(Math.abs(off), 1) * 0.18 });
          });
        }
      }
    }).scrollTrigger;

    // acessibilidade: ao focar um link de um painel fora da tela, rola até ele
    panels.forEach((p, i) => p.addEventListener('focusin', () => {
      const y = st.start + (st.end - st.start) * (i / (n - 1));
      if (lenis) lenis.scrollTo(y, { immediate: true }); else window.scrollTo(0, y);
    }));
  }

  /* ---------------------------------------------------------------------
     11. PÁGINA DE SABOR — lata girando, barras e anel de ingredientes
     ------------------------------------------------------------------- */
  function initFlavor() {
    const can = $('[data-spin-can]');
    if (can && motion) {
      gsap.fromTo(can, { rotation: -6, rotateY: -18 }, {
        rotation: 16, rotateY: 28, y: () => window.innerHeight * 0.22, scale: 0.88, ease: 'none',
        scrollTrigger: { trigger: can.closest('section'), start: 'top top', end: 'bottom top', scrub: true }
      });
    }

    $$('.bar__fill').forEach((b) => {
      if (!motion) return;
      const v = parseFloat(getComputedStyle(b).getPropertyValue('--v')) || 1;
      gsap.fromTo(b, { scaleX: 0 }, { scaleX: v, duration: 1.6, ease: 'power3.out', scrollTrigger: { trigger: b, start: 'top 92%', once: true } });
    });

    $$('[data-ring]').forEach((ring) => {
      const fg = $('.ring__fg', ring);
      const c = parseFloat(fg.getAttribute('stroke-dasharray'));
      const final = parseFloat(fg.getAttribute('stroke-dashoffset'));
      if (!motion) return;
      fg.style.strokeDashoffset = c;
      ScrollTrigger.create({ trigger: ring, start: 'top 85%', once: true, onEnter: () => { fg.style.strokeDashoffset = final; } });
    });
  }

  /* ---------------------------------------------------------------------
     12. HISTÓRIA — linha do tempo que se desenha + mapa interativo
     ------------------------------------------------------------------- */
  function initTimeline() {
    const tl = $('[data-timeline]');
    if (!tl) return;
    const items = $$('.timeline__item', tl);
    if (!motion) { items.forEach((i) => i.classList.add('is-active')); return; }
    gsap.fromTo($('.timeline__line i', tl), { scaleY: 0 }, { scaleY: 1, ease: 'none', scrollTrigger: { trigger: tl, start: 'top 62%', end: 'bottom 62%', scrub: true } });
    items.forEach((it) => ScrollTrigger.create({
      trigger: it, start: 'top 62%',
      onEnter: () => it.classList.add('is-active'),
      onLeaveBack: () => it.classList.remove('is-active')
    }));
  }

  function initMap() {
    const map = $('[data-map]');
    if (!map) return;
    const points = $$('.map-point', map);
    const origins = $$('[data-origin]');
    const activate = (key) => {
      origins.forEach((o) => o.classList.toggle('is-active', o.dataset.origin === key));
      points.forEach((p) => { const core = $('.core', p); core && core.setAttribute('r', p.dataset.key === key ? 11 : 8); });
    };
    points.forEach((p) => {
      ['pointerenter', 'focus'].forEach((ev) => p.addEventListener(ev, () => activate(p.dataset.key)));
    });
    origins.forEach((o) => o.addEventListener('pointerenter', () => activate(o.dataset.origin)));
    if (motion) {
      gsap.from(points, { scale: 0, transformOrigin: 'center', stagger: 0.18, duration: 0.8, ease: 'back.out(2)', scrollTrigger: { trigger: map, start: 'top 75%', once: true } });
      const routes = $$('.route', map);
      routes.forEach((r) => {
        const len = r.getTotalLength();
        gsap.fromTo(r, { strokeDashoffset: len, strokeDasharray: `6 7` }, { strokeDashoffset: 0, duration: 2, ease: 'power2.out', scrollTrigger: { trigger: map, start: 'top 70%', once: true } });
      });
    }
  }

  /* ---------------------------------------------------------------------
     13. FILTRO DE SABORES e BUSCA DE PONTOS DE VENDA
     ------------------------------------------------------------------- */
  function initFilters() {
    const group = $('[data-filters]');
    if (!group) return;
    const items = $$(group.dataset.filters);
    const status = $('#filter-status');
    group.addEventListener('click', (e) => {
      const b = e.target.closest('button[data-filter]');
      if (!b) return;
      $$('button[data-filter]', group).forEach((x) => x.setAttribute('aria-pressed', String(x === b)));
      const f = b.dataset.filter;
      const show = items.filter((i) => f === 'todos' || i.dataset.cat.split(' ').includes(f));
      const hide = items.filter((i) => !show.includes(i));
      const apply = () => {
        hide.forEach((i) => i.classList.add('is-hidden'));
        show.forEach((i) => i.classList.remove('is-hidden'));
        if (motion) gsap.fromTo(show, { y: 40, opacity: 0, scale: 0.9 }, { y: 0, opacity: 1, scale: 1, stagger: 0.08, duration: 0.6, ease: 'back.out(1.5)', clearProps: 'transform,opacity' });
        if (status) status.textContent = `${show.length} ${show.length === 1 ? 'sabor encontrado' : 'sabores encontrados'}`;
        if (hasGSAP) ScrollTrigger.refresh();
      };
      const leaving = hide.filter((i) => !i.classList.contains('is-hidden'));
      if (motion && leaving.length) gsap.to(leaving, { scale: 0.85, opacity: 0, duration: 0.28, ease: 'power2.in', onComplete: apply });
      else apply();
    });
  }

  function initStores() {
    const root = $('[data-store-finder]');
    if (!root) return;
    const input = $('#busca-cidade', root);
    const chips = $$('button[data-uf]', root);
    const stores = $$('.store');
    const status = $('#stores-status');
    const empty = $('.stores-empty');
    let uf = 'todos';
    const norm = (s) => s.normalize('NFD').replace(/[̀-ͯ]/g, '').toLowerCase().trim();
    const run = () => {
      const q = norm(input.value);
      const shown = [];
      stores.forEach((s) => {
        const ok = (uf === 'todos' || s.dataset.uf === uf) && (!q || norm(s.dataset.search).includes(q));
        s.classList.toggle('is-hidden', !ok);
        if (ok) shown.push(s);
      });
      status.textContent = shown.length
        ? `${shown.length} ${shown.length === 1 ? 'ponto de venda encontrado' : 'pontos de venda encontrados'}`
        : 'Nenhum ponto de venda encontrado';
      empty.classList.toggle('is-visible', !shown.length);
      if (motion && shown.length) gsap.fromTo(shown, { y: 26, opacity: 0 }, { y: 0, opacity: 1, stagger: 0.04, duration: 0.45, ease: 'power2.out', clearProps: 'transform,opacity' });
      if (hasGSAP) ScrollTrigger.refresh();
    };
    let t = 0;
    input.addEventListener('input', () => { clearTimeout(t); t = setTimeout(run, 160); });
    const form = input.closest('form');
    form && form.addEventListener('submit', (e) => { e.preventDefault(); run(); });
    chips.forEach((c) => c.addEventListener('click', () => {
      uf = c.dataset.uf;
      chips.forEach((x) => x.setAttribute('aria-pressed', String(x === c)));
      run();
    }));
  }

  /* Mapa do ponto de venda: clique no cartão mostra a localização ao lado */
  function initStoreMap() {
    const fig = $('#stores-map');
    if (!fig) return;
    const iframe = $('iframe', fig);
    const nameEl = $('.stores-map__name', fig);
    const addrEl = $('.stores-map__address', fig);
    const link = $('.stores-map__link', fig);
    const stores = $$('.store[data-maps-q]');
    const select = (store, scroll) => {
      const q = encodeURIComponent(store.dataset.mapsQ);
      stores.forEach((s) => {
        s.classList.toggle('is-active', s === store);
        const b = $('.store__select', s);
        if (b) b.setAttribute('aria-pressed', String(s === store));
      });
      fig.classList.add('is-loading');
      iframe.onload = () => fig.classList.remove('is-loading');
      setTimeout(() => fig.classList.remove('is-loading'), 2500);
      iframe.src = `https://www.google.com/maps?q=${q}&z=15&output=embed`;
      iframe.title = 'Mapa do ponto de venda selecionado: ' + store.dataset.name;
      nameEl.textContent = store.dataset.name;
      addrEl.textContent = store.dataset.address;
      link.href = 'https://www.google.com/maps/search/?api=1&query=' + q;
      link.setAttribute('aria-label', `Abrir ${store.dataset.name} no Google Maps (nova aba)`);
      if (motion) gsap.fromTo(fig, { scale: 0.98 }, { scale: 1, duration: 0.5, ease: 'back.out(2)', clearProps: 'transform' });
      // no celular o mapa fica abaixo da lista: leva a pessoa até ele
      if (scroll && window.matchMedia('(max-width: 999px)').matches) {
        const y = fig.getBoundingClientRect().top + window.scrollY - 90;
        if (lenis) lenis.scrollTo(y, { force: true });
        else window.scrollTo({ top: y, behavior: reduce ? 'auto' : 'smooth' });
      }
    };
    stores.forEach((store) => $('.store__select', store).addEventListener('click', () => select(store, true)));
  }

  /* ---------------------------------------------------------------------
     14. LIGHTBOX (#FRIZZALOVERS)
     ------------------------------------------------------------------- */
  function initLightbox() {
    const dlg = $('#lightbox');
    if (!dlg || typeof dlg.showModal !== 'function') return;
    const items = $$('[data-lightbox]');
    const media = $('.lightbox__media', dlg);
    const user = $('.lightbox__user', dlg);
    const cap = $('.lightbox__caption', dlg);
    const counter = $('.lightbox__count', dlg);
    let idx = 0;
    const show = (i) => {
      idx = (i + items.length) % items.length;
      const it = items[idx];
      const slot = $('.img-slot', it).cloneNode(true);
      slot.removeAttribute('data-loading');
      media.replaceChildren(slot);
      if (!slot.classList.contains('is-loaded')) loadSlot(slot);
      user.textContent = it.dataset.user;
      cap.textContent = it.dataset.caption;
      if (counter) counter.textContent = `${idx + 1} de ${items.length}`;
      if (motion) gsap.fromTo(slot, { opacity: 0, scale: 0.96 }, { opacity: 1, scale: 1, duration: 0.45, ease: 'power3.out' });
    };
    items.forEach((it, i) => it.addEventListener('click', () => { show(i); dlg.showModal(); lenis && lenis.stop(); }));
    $('.lightbox__btn--prev', dlg).addEventListener('click', () => show(idx - 1));
    $('.lightbox__btn--next', dlg).addEventListener('click', () => show(idx + 1));
    $('.lightbox__close', dlg).addEventListener('click', () => dlg.close());
    dlg.addEventListener('click', (e) => { if (e.target === dlg) dlg.close(); });
    dlg.addEventListener('keydown', (e) => {
      if (e.key === 'ArrowRight') show(idx + 1);
      if (e.key === 'ArrowLeft') show(idx - 1);
    });
    dlg.addEventListener('close', () => { lenis && lenis.start(); items[idx] && items[idx].focus(); });
  }

  /* ---------------------------------------------------------------------
     15. FAQ (acordeão acessível)
     ------------------------------------------------------------------- */
  function initFaq() {
    $$('.faq__q').forEach((q) => {
      const panel = d.getElementById(q.getAttribute('aria-controls'));
      if (panel) panel.inert = q.getAttribute('aria-expanded') !== 'true';
      q.addEventListener('click', () => {
        const item = q.closest('.faq__item');
        const open = !item.classList.contains('is-open');
        item.classList.toggle('is-open', open);
        q.setAttribute('aria-expanded', String(open));
        if (panel) panel.inert = !open;
        if (hasGSAP) setTimeout(() => ScrollTrigger.refresh(), 520);
      });
    });
  }

  /* ---------------------------------------------------------------------
     16. FORMULÁRIOS (validação amigável, só front-end)
     ------------------------------------------------------------------- */
  function checkField(f) {
    const inp = f.querySelector('input, select, textarea');
    const err = f.querySelector('.field__error span:not(.icon)');
    let ok = true;
    let msg = '';
    if (inp.type === 'radio') {
      ok = !!f.querySelector('input:checked');
      msg = f.dataset.msgEmpty || 'Escolha uma opção.';
    } else if (inp.type === 'checkbox') {
      ok = inp.checked;
      msg = f.dataset.msgEmpty || 'Marque esta opção para continuar.';
    } else if (!inp.value.trim()) {
      ok = false; msg = f.dataset.msgEmpty || 'Preencha este campo.';
    } else if (inp.type === 'email' && !/^[^\s@]+@[^\s@]+\.[^\s@]{2,}$/.test(inp.value.trim())) {
      ok = false; msg = f.dataset.msgInvalid || 'Confira o e-mail: ele precisa ter @ e um domínio, como nome@email.com.';
    } else if (inp.minLength > 0 && inp.value.trim().length < inp.minLength) {
      ok = false; msg = f.dataset.msgShort || f.dataset.msgEmpty || `Escreva pelo menos ${inp.minLength} caracteres.`;
    }
    f.classList.toggle('is-invalid', !ok);
    f.classList.toggle('is-valid', ok);
    f.querySelectorAll('input, select, textarea').forEach((i) => i.setAttribute('aria-invalid', String(!ok)));
    if (err) err.textContent = ok ? '' : msg;
    return ok;
  }

  function initForms() {
    $$('form[data-validate]').forEach((form) => {
      form.noValidate = true;
      const fields = $$('.field', form).filter((f) => f.querySelector('[required]'));
      const msgBox = $('[data-form-msg]', form);

      const check = checkField;

      fields.forEach((f) => {
        f.querySelectorAll('input, select, textarea').forEach((inp) => {
          inp.addEventListener('blur', () => { if (inp.value && inp.type !== 'radio') check(f); });
          inp.addEventListener('input', () => { if (f.classList.contains('is-invalid')) check(f); });
          inp.addEventListener('change', () => { if (inp.type === 'radio' || inp.type === 'checkbox') check(f); });
        });
      });

      form.addEventListener('submit', (e) => {
        e.preventDefault();
        const bad = fields.filter((f) => !check(f));
        if (bad.length) {
          const first = bad[0].querySelector('input, select, textarea');
          first && first.focus();
          if (msgBox) msgBox.textContent = bad.length === 1 ? 'Falta só um detalhe: confira o campo destacado.' : `Faltam ${bad.length} detalhes: confira os campos destacados.`;
          return;
        }
        const success = $('.form-success', form);
        if (success) {
          success.classList.add('is-visible');
          success.setAttribute('tabindex', '-1');
          success.focus();
        } else if (msgBox) {
          msgBox.textContent = 'Oba! Inscrição confirmada. Logo, logo chega novidade borbulhante no seu e-mail. 🫧';
          if (motion) gsap.fromTo(msgBox, { y: 10, opacity: 0 }, { y: 0, opacity: 1, duration: 0.5, ease: 'back.out(2)' });
        }
        form.reset();
        fields.forEach((f) => f.classList.remove('is-valid'));
      });

      const again = $('[data-form-again]', form);
      again && again.addEventListener('click', () => {
        $('.form-success', form).classList.remove('is-visible');
        const f = form.querySelector('input, textarea');
        f && f.focus();
        if (msgBox) msgBox.textContent = '';
      });
    });
  }

  /* ---------------------------------------------------------------------
     17. LINKS DE DEMONSTRAÇÃO (redes, loja, WhatsApp — marca fictícia)
     ------------------------------------------------------------------- */
  let toastTimer = 0;
  function toast(text, action) {
    let t = $('.toast');
    if (!t) {
      t = d.createElement('div');
      t.className = 'toast';
      t.setAttribute('role', 'status');
      t.setAttribute('aria-live', 'polite');
      d.body.appendChild(t);
    }
    const msg = d.createElement('span');
    msg.textContent = text;
    t.replaceChildren(msg);
    if (action) {
      const b = d.createElement('button');
      b.type = 'button';
      b.className = 'toast__action';
      b.textContent = action.label;
      b.addEventListener('click', () => { t.classList.remove('is-visible'); action.onClick(); });
      t.appendChild(b);
    }
    requestAnimationFrame(() => t.classList.add('is-visible'));
    clearTimeout(toastTimer);
    toastTimer = setTimeout(() => t.classList.remove('is-visible'), 3800);
  }
  function initDemoLinks() {
    d.addEventListener('click', (e) => {
      const a = e.target.closest('[data-demo]');
      if (!a) return;
      e.preventDefault();
      toast(a.dataset.demo || 'Link ilustrativo: a FRIZZA é uma marca fictícia criada para um projeto acadêmico.');
    });
  }

  /* ---------------------------------------------------------------------
     18. INTRODUÇÕES (rodam quando o preloader/cortina libera a página)
     ------------------------------------------------------------------- */
  function playIntro() {
    if (!motion) return;
    const tl = gsap.timeline({ defaults: { ease: 'power4.out' } });
    introSplits.forEach(({ parts, anim }, i) => {
      tl.to(parts, { yPercent: 0, rotate: 0, duration: anim.duration, ease: anim.ease, stagger: anim.stagger }, i === 0 ? 0.05 : '-=0.7');
    });
    const intro = $$('[data-intro-fade]');
    if (intro.length) {
      tl.fromTo(intro, { y: 30, opacity: 0 }, { y: 0, opacity: 1, duration: 0.9, stagger: 0.1, clearProps: 'transform' }, 0.35);
      intro.forEach((el) => el.classList.add('is-revealed'));
    }

    const heroCans = $$('.hero__can .png-slot');
    if (heroCans.length) tl.from(heroCans, { y: 360, rotation: () => gsap.utils.random(-30, 30), opacity: 0, duration: 1.4, ease: 'back.out(1.25)', stagger: { each: 0.09, from: 'center' } }, 0.2);
    const fruits = $$('.hero__fruit .png-slot, .hero__drop');
    if (fruits.length) tl.from(fruits, { scale: 0, rotation: -90, duration: 1, ease: 'back.out(2)', stagger: 0.07 }, 0.7);

    const flavorCan = $('[data-spin-can] .png-slot');
    if (flavorCan) tl.from(flavorCan, { y: 260, rotation: -35, opacity: 0, duration: 1.5, ease: 'back.out(1.3)' }, 0.1);
    const flavorFruits = $$('.flavor-hero__fruit .png-slot');
    if (flavorFruits.length) tl.from(flavorFruits, { scale: 0, rotation: 120, duration: 1, ease: 'back.out(2)', stagger: 0.1 }, 0.6);

    const pageCans = $$('.cans-row .png-slot');
    if (pageCans.length) tl.from(pageCans, { y: 200, opacity: 0, rotation: () => gsap.utils.random(-25, 25), duration: 1.2, ease: 'back.out(1.4)', stagger: 0.08 }, 0.3);

    const polaroids = $$('.polaroid');
    if (polaroids.length) tl.from(polaroids, { scale: 0.3, opacity: 0, rotation: () => gsap.utils.random(-40, 40), duration: 1.1, ease: 'back.out(1.6)', stagger: 0.12 }, 0.4);

    // hashtag gigante: onda contínua
    $$('[data-wave]').forEach((el) => {
      if (!el._chars) return;
      tl.add(() => gsap.to(el._chars, { y: -14, duration: 0.7, ease: 'sine.inOut', stagger: { each: 0.07, repeat: -1, yoyo: true } }), '+=0');
    });
  }


  /* ---------------------------------------------------------------------
     19. LOJA ONLINE — carrinho, quiz de sabores e checkout (simulação)
     O carrinho fica salvo no navegador (localStorage) e acompanha a pessoa
     por todas as páginas. Nada é enviado para servidor nenhum.
     ------------------------------------------------------------------- */
  const CART_KEY = 'frizza-cart';
  const FREE_SHIP = 150;
  const brl = (v) => v.toLocaleString('pt-BR', { style: 'currency', currency: 'BRL' });
  const Cart = {
    items: [],
    load() {
      try { this.items = JSON.parse(localStorage.getItem(CART_KEY)) || []; } catch (e) { this.items = []; }
      if (!Array.isArray(this.items)) this.items = [];
      this.items = this.items.filter((i) => i && i.id && i.qty > 0 && isFinite(i.price));
    },
    save() {
      try { localStorage.setItem(CART_KEY, JSON.stringify(this.items)); } catch (e) { /* modo privado */ }
      d.dispatchEvent(new CustomEvent('cart:change'));
    },
    add(prod, qty = 1) {
      const it = this.items.find((i) => i.id === prod.id);
      if (it) it.qty = Math.min(99, it.qty + qty); else this.items.push({ ...prod, qty });
      this.save();
    },
    setQty(id, q) {
      const it = this.items.find((i) => i.id === id);
      if (!it) return;
      it.qty = Math.max(0, Math.min(99, q));
      if (!it.qty) this.items = this.items.filter((i) => i.id !== id);
      this.save();
    },
    remove(id) { this.items = this.items.filter((i) => i.id !== id); this.save(); },
    clear() { this.items = []; this.save(); },
    count() { return this.items.reduce((a, i) => a + i.qty, 0); },
    subtotal() { return this.items.reduce((a, i) => a + i.qty * i.price, 0); }
  };
  Cart.load();
  const productFrom = (el) => ({ id: el.dataset.id, name: el.dataset.name, price: parseFloat(el.dataset.price), color: el.dataset.color, img: el.dataset.img, url: el.dataset.url });
  let openCart = () => {};

  function cartThumb(item) {
    const t = d.createElement('span');
    t.className = 'cart-thumb';
    t.style.setProperty('--c', item.color || '#FF6B2B');
    t.setAttribute('aria-hidden', 'true');
    if (item.img) {
      const img = new Image();
      img.alt = '';
      img.onload = () => t.appendChild(img);
      img.src = item.img;
    }
    return t;
  }

  function initCart() {
    const drawer = $('#cart-drawer');
    if (!drawer) return;
    const panel = $('.cart-drawer__panel', drawer);
    const list = $('[data-cart-items]', drawer);
    const empty = $('[data-cart-empty]', drawer);
    const foot = $('[data-cart-foot]', drawer);
    const sub = $('[data-cart-subtotal]', drawer);
    const ship = $('[data-cart-ship]', drawer);
    const toggles = $$('.cart-toggle');
    const counts = $$('[data-cart-count]');
    let isOpen = false;
    let lastFocus = null;

    const row = (it) => {
      const li = d.createElement('li');
      li.className = 'cart-item';
      li.appendChild(cartThumb(it));
      const info = d.createElement('div');
      info.className = 'cart-item__info';
      const name = d.createElement('a');
      name.className = 'cart-item__name';
      name.href = it.url || 'sabores.html';
      name.textContent = it.name;
      const unit = d.createElement('span');
      unit.className = 'cart-item__unit';
      unit.textContent = `${brl(it.price)} cada`;
      const qty = d.createElement('div');
      qty.className = 'qty';
      qty.setAttribute('role', 'group');
      qty.setAttribute('aria-label', `Quantidade de ${it.name}`);
      qty.innerHTML = '<button type="button" data-qty="-1">−</button><output aria-live="polite"></output><button type="button" data-qty="1">+</button>';
      qty.querySelector('output').textContent = it.qty;
      qty.querySelector('[data-qty="-1"]').setAttribute('aria-label', `Diminuir ${it.name}`);
      qty.querySelector('[data-qty="1"]').setAttribute('aria-label', `Aumentar ${it.name}`);
      info.append(name, unit, qty);
      const side = d.createElement('div');
      side.className = 'cart-item__side';
      const total = d.createElement('strong');
      total.textContent = brl(it.price * it.qty);
      const rm = d.createElement('button');
      rm.type = 'button';
      rm.className = 'cart-item__remove';
      rm.dataset.remove = '';
      rm.textContent = 'Remover';
      rm.setAttribute('aria-label', `Remover ${it.name} do carrinho`);
      side.append(total, rm);
      li.append(info, side);
      li.dataset.id = it.id;
      return li;
    };

    const render = () => {
      const n = Cart.count();
      counts.forEach((c) => { c.textContent = n; c.classList.toggle('is-empty', !n); });
      toggles.forEach((t) => t.setAttribute('aria-label', `Abrir carrinho, ${n} ${n === 1 ? 'item' : 'itens'}`));
      list.replaceChildren(...Cart.items.map(row));
      empty.hidden = Cart.items.length > 0;
      foot.hidden = Cart.items.length === 0;
      const st = Cart.subtotal();
      sub.textContent = brl(st);
      ship.textContent = st >= FREE_SHIP ? 'Oba! Frete grátis para o Sul e Sudeste.' : `Faltam ${brl(FREE_SHIP - st)} para ganhar frete grátis no Sul e Sudeste.`;
    };

    list.addEventListener('click', (e) => {
      const li = e.target.closest('.cart-item');
      if (!li) return;
      const it = Cart.items.find((i) => i.id === li.dataset.id);
      const qb = e.target.closest('[data-qty]');
      if (qb && it) {
        Cart.setQty(it.id, it.qty + parseInt(qb.dataset.qty, 10));
        const again = list.querySelector(`.cart-item[data-id="${it.id}"] [data-qty="${qb.dataset.qty}"]`);
        (again || $('.cart-drawer__close', drawer)).focus();
      }
      if (e.target.closest('[data-remove]') && it) { Cart.remove(it.id); $('.cart-drawer__close', drawer).focus(); }
    });

    const setOpen = (v) => {
      isOpen = v;
      drawer.classList.toggle('is-open', v);
      drawer.setAttribute('aria-hidden', String(!v));
      drawer.inert = !v;
      toggles.forEach((t) => t.setAttribute('aria-expanded', String(v)));
      html.classList.toggle('cart-open', v);
      if (lenis) v ? lenis.stop() : lenis.start();
      if (v) {
        lastFocus = d.activeElement;
        setTimeout(() => $('.cart-drawer__close', drawer).focus(), 60);
      } else if (lastFocus && lastFocus.focus) lastFocus.focus();
    };
    openCart = () => setOpen(true);
    drawer.inert = true;

    d.addEventListener('click', (e) => {
      if (e.target.closest('[data-open-cart]')) {
        e.preventDefault();
        if (menuOpen && closeMenu) closeMenu(false, false);
        setOpen(true);
      } else if (e.target.closest('[data-close-cart]')) setOpen(false);

      const add = e.target.closest('[data-add-cart]');
      if (add) {
        e.preventDefault();
        const prod = productFrom(add);
        Cart.add(prod);
        const label = $('[data-cart-label]', add);
        if (label) {
          if (!label.dataset.orig) label.dataset.orig = label.textContent;
          label.textContent = 'Adicionado!';
          add.classList.add('is-added');
          clearTimeout(add._t);
          add._t = setTimeout(() => { label.textContent = label.dataset.orig; add.classList.remove('is-added'); }, 1600);
        }
        toggles.forEach((t) => { t.classList.remove('is-bump'); void t.offsetWidth; t.classList.add('is-bump'); });
        toast(`${prod.name} foi para o carrinho!`, { label: 'Ver carrinho', onClick: () => setOpen(true) });
      }
    });

    d.addEventListener('keydown', (e) => {
      if (!isOpen) return;
      if (e.key === 'Escape') { setOpen(false); return; }
      if (e.key === 'Tab') { // mantém o foco dentro do carrinho
        const f = $$('a[href], button:not([disabled]), input, select', panel).filter((x) => x.offsetParent !== null);
        if (!f.length) return;
        const first = f[0], last = f[f.length - 1];
        if (e.shiftKey && d.activeElement === first) { e.preventDefault(); last.focus(); }
        else if (!e.shiftKey && d.activeElement === last) { e.preventDefault(); first.focus(); }
      }
    });

    d.addEventListener('cart:change', render);
    window.addEventListener('storage', (e) => { if (e.key === CART_KEY) { Cart.load(); render(); } });
    render();
  }

  /* Quiz "Qual FRIZZA combina com você?" */
  function initQuiz() {
    const q = $('[data-quiz]');
    if (!q) return;
    const steps = $$('.quiz__step', q);
    const back = $('[data-quiz-back]', q);
    const count = $('[data-quiz-count]', q);
    const bar = $('.quiz__bar i', q);
    const form = $('.quiz__form', q);
    const result = $('[data-quiz-result]', q);
    const results = $('[data-quiz-results]', q);
    const answers = new Array(steps.length).fill(null);
    let cur = 0;

    const maxPer = {};
    steps.forEach((st) => {
      const per = {};
      $$('.quiz__opt', st).forEach((o) => Object.entries(JSON.parse(o.dataset.score)).forEach(([k, v]) => { per[k] = Math.max(per[k] || 0, v); }));
      Object.entries(per).forEach(([k, v]) => { maxPer[k] = (maxPer[k] || 0) + v; });
    });

    const show = (i, dir = 1) => {
      cur = i;
      steps.forEach((st, k) => { st.hidden = k !== i; st.classList.toggle('is-current', k === i); });
      back.hidden = i === 0;
      count.textContent = `Pergunta ${i + 1} de ${steps.length}`;
      bar.style.setProperty('--p', (i + 1) / steps.length);
      if (motion) gsap.fromTo(steps[i].querySelectorAll('.quiz__q, .quiz__opt'), { x: 40 * dir, opacity: 0 }, { x: 0, opacity: 1, stagger: 0.05, duration: 0.45, ease: 'power3.out', clearProps: 'transform,opacity' });
    };

    const finish = () => {
      const score = {};
      answers.forEach((a) => a && Object.entries(a).forEach(([k, v]) => { score[k] = (score[k] || 0) + v; }));
      const rank = Object.keys(maxPer)
        .map((k) => ({ k, s: score[k] || 0, pct: Math.round((100 * (score[k] || 0)) / maxPer[k]) }))
        .sort((a, b) => b.s - a.s || b.pct - a.pct);
      const best = rank[0] ? rank[0].s : 0;
      let top = rank.filter((r) => r.s > 0 && r.s >= best * 0.4).slice(0, 3);
      if (!top.length) top = rank.slice(0, 2);
      const title = $('.quiz__result-title', q);
      if (title) title.textContent = top.length === 1 ? 'O sabor com a sua cara' : 'Os sabores com a sua cara';
      const addAll = $('[data-quiz-add-all] span', q);
      if (addAll) addAll.textContent = top.length === 1 ? 'Adicionar ao carrinho' : 'Adicionar os favoritos ao carrinho';
      results.replaceChildren();
      top.forEach((r, idx) => {
        const tpl = q.querySelector(`template[data-quiz-product="${r.k}"]`);
        if (!tpl) return;
        const node = tpl.content.firstElementChild.cloneNode(true);
        $('[data-match]', node).textContent = `${r.pct}%`;
        if (idx === 0) node.classList.add('is-best');
        results.appendChild(node);
        $$('[data-img]', node).forEach(loadSlot);
      });
      form.hidden = true;
      back.hidden = true;
      count.textContent = 'Resultado';
      bar.style.setProperty('--p', 1);
      result.hidden = false;
      result.focus({ preventScroll: true });
      if (motion) gsap.fromTo($$('.quiz-result', results), { y: 40, opacity: 0, scale: 0.95 }, { y: 0, opacity: 1, scale: 1, stagger: 0.12, duration: 0.7, ease: 'back.out(1.5)', clearProps: 'transform,opacity' });
      if (hasGSAP) ScrollTrigger.refresh();
    };

    q.addEventListener('click', (e) => {
      const o = e.target.closest('.quiz__opt');
      if (o) {
        const st = o.closest('.quiz__step');
        const i = parseInt(st.dataset.step, 10);
        $$('.quiz__opt', st).forEach((b) => b.setAttribute('aria-pressed', String(b === o)));
        answers[i] = JSON.parse(o.dataset.score);
        setTimeout(() => {
          if (i < steps.length - 1) {
            show(i + 1);
            const first = steps[i + 1].querySelector('.quiz__opt');
            if (first) first.focus({ preventScroll: true });
          } else finish();
        }, 280);
      }
      if (e.target.closest('[data-quiz-add-all]')) {
        const btns = $$('[data-add-cart]', results);
        btns.forEach((b) => Cart.add(productFrom(b)));
        toast(`${btns.length} ${btns.length === 1 ? 'sabor foi' : 'sabores foram'} para o carrinho!`, { label: 'Ver carrinho', onClick: () => openCart() });
      }
      if (e.target.closest('[data-quiz-restart]')) {
        answers.fill(null);
        $$('.quiz__opt', q).forEach((b) => b.setAttribute('aria-pressed', 'false'));
        result.hidden = true;
        form.hidden = false;
        show(0);
        const first = steps[0].querySelector('.quiz__opt');
        if (first) first.focus({ preventScroll: true });
      }
    });
    back.addEventListener('click', () => {
      show(Math.max(0, cur - 1), -1);
      const sel = steps[cur].querySelector('[aria-pressed="true"]') || steps[cur].querySelector('.quiz__opt');
      if (sel) sel.focus({ preventScroll: true });
    });
  }

  /* Máscaras de digitação (telefone, CPF, CEP, cartão) */
  function initMasks() {
    const fmt = (digits, pattern) => {
      let out = '';
      let i = 0;
      for (const ch of pattern) {
        if (i >= digits.length) break;
        if (ch === '0') out += digits[i++]; else out += ch;
      }
      return out;
    };
    const PAT = {
      tel: (v) => (v.length > 10 ? '(00) 00000-0000' : '(00) 0000-0000'),
      cpf: () => '000.000.000-00',
      cep: () => '00000-000',
      card: () => '0000 0000 0000 0000',
      val: () => '00/00',
      cvv: () => '000'
    };
    d.addEventListener('input', (e) => {
      const el = e.target;
      const m = el.dataset && el.dataset.mask;
      if (!m || !PAT[m]) return;
      const digits = el.value.replace(/\D/g, '');
      const pat = PAT[m](digits);
      el.value = fmt(digits.slice(0, pat.split('0').length - 1), pat);
    });
  }

  /* Checkout: dados → entrega → pagamento → confirmação (simulação) */
  function initCheckout() {
    const root = $('[data-checkout]');
    if (!root) return;
    const form = $('[data-co-form]', root);
    const panels = $$('[data-co-panel]', root);
    const labels = $$('[data-co-step-label]');
    const empty = $('[data-co-empty]', root);
    const success = $('[data-co-success]', root);
    const summary = $('[data-co-summary]', root);
    const itemsEl = $('[data-co-items]', root);
    const subEl = $('[data-co-subtotal]', root);
    const freteEl = $('[data-co-frete]', root);
    const totalEl = $('[data-co-total]', root);
    const discRow = $('[data-co-discount-row]', root);
    const discEl = $('[data-co-discount]', root);
    const parcelas = $('[data-parcelas]', root);
    const errBox = $('[data-co-error]', root);
    const FRETE = { padrao: 19.9, expressa: 34.9, retirada: 0 };
    const SUL_SUDESTE = ['PR', 'SC', 'RS', 'SP', 'RJ', 'MG', 'ES'];
    let step = 0;
    let done = false;
    const val = (name) => { const el = form.querySelector(`[name="${name}"]:checked`); return el ? el.value : ''; };

    const calc = () => {
      const sub = Cart.subtotal();
      const uf = $('#co-uf').value;
      const tipo = val('co-frete') || 'padrao';
      const freeOk = sub >= FREE_SHIP && (!uf || SUL_SUDESTE.includes(uf));
      let fr = FRETE[tipo];
      if (tipo === 'padrao' && freeOk) fr = 0;
      const disc = val('co-pag') === 'pix' ? Math.round(sub * 5) / 100 : 0;
      return { sub, fr, disc, total: sub + fr - disc, freeOk, tipo };
    };

    const render = () => {
      if (done) return;
      const hasItems = Cart.items.length > 0;
      form.hidden = !hasItems;
      summary.hidden = !hasItems;
      empty.hidden = hasItems;
      const c = calc();
      itemsEl.replaceChildren(...Cart.items.map((it) => {
        const li = d.createElement('li');
        li.className = 'co-summary__item';
        li.appendChild(cartThumb(it));
        const n = d.createElement('span');
        n.className = 'co-summary__name';
        n.textContent = `${it.name} × ${it.qty}`;
        const t = d.createElement('strong');
        t.textContent = brl(it.price * it.qty);
        li.append(n, t);
        return li;
      }));
      subEl.textContent = brl(c.sub);
      freteEl.textContent = step === 0 ? 'calculado na próxima etapa' : (c.fr === 0 ? 'Grátis' : brl(c.fr));
      discRow.hidden = !c.disc;
      discEl.textContent = '− ' + brl(c.disc);
      totalEl.textContent = brl(step === 0 ? c.sub - c.disc : c.total);
      $$('[data-frete-price]', root).forEach((el) => {
        const k = el.dataset.fretePrice;
        el.textContent = k === 'retirada' || (k === 'padrao' && c.freeOk) ? 'Grátis' : brl(FRETE[k]);
      });
      if (parcelas) {
        const sel = parcelas.value || '1';
        parcelas.innerHTML = [1, 2, 3].map((k) => `<option value="${k}">${k}x de ${brl(c.total / k)} sem juros</option>`).join('');
        parcelas.value = sel;
      }
    };

    const fieldsOf = (panel) => $$('.field', panel).filter((f) => {
      const inp = f.querySelector('[required], [data-pay-req]');
      return inp && !f.closest('[hidden]');
    });
    const validate = (panel) => {
      const bad = fieldsOf(panel).filter((f) => !checkField(f));
      if (bad.length) {
        const first = bad[0].querySelector('input, select, textarea');
        if (first) first.focus();
      }
      return bad.length === 0;
    };
    form.addEventListener('input', (e) => { const f = e.target.closest('.field'); if (f && f.classList.contains('is-invalid')) checkField(f); });
    form.addEventListener('focusout', (e) => { const f = e.target.closest('.field'); if (f && e.target.value && e.target.type !== 'radio' && (e.target.required || e.target.hasAttribute('data-pay-req'))) checkField(f); });

    const scrollTop = () => {
      const y = root.getBoundingClientRect().top + window.scrollY - 100;
      if (lenis) lenis.scrollTo(y, { force: true }); else window.scrollTo({ top: y, behavior: reduce ? 'auto' : 'smooth' });
    };
    const goTo = (i) => {
      step = i;
      panels.forEach((pn, k) => { pn.hidden = k !== i; pn.classList.toggle('is-current', k === i); });
      labels.forEach((l, k) => { l.classList.toggle('is-current', k === i); l.classList.toggle('is-done', k < i); });
      render();
      scrollTop();
      const legend = $('legend', panels[i]);
      if (legend) { legend.setAttribute('tabindex', '-1'); legend.focus({ preventScroll: true }); }
      if (motion) gsap.fromTo(panels[i], { y: 30, opacity: 0 }, { y: 0, opacity: 1, duration: 0.5, ease: 'power3.out', clearProps: 'transform,opacity' });
      if (hasGSAP) ScrollTrigger.refresh();
    };
    root.addEventListener('click', (e) => {
      if (e.target.closest('[data-co-next]') && validate(panels[step])) goTo(step + 1);
      if (e.target.closest('[data-co-prev]')) goTo(step - 1);
    });
    form.addEventListener('change', (e) => {
      if (e.target.name === 'co-pag') {
        $$('[data-pay-detail]', root).forEach((el) => { el.hidden = el.dataset.payDetail !== e.target.value; });
        $$('[data-pay-detail="cartao"] .field', root).forEach((f) => f.classList.remove('is-invalid'));
      }
      render();
    });

    form.addEventListener('submit', (e) => {
      e.preventDefault();
      if (step !== 2) { if (validate(panels[step])) goTo(step + 1); return; }
      if (!validate(panels[2])) { errBox.textContent = 'Confira os campos destacados para concluir.'; return; }
      errBox.textContent = '';
      const c = calc();
      render();
      done = true;
      const order = 'FRZ-' + String(Date.now()).slice(-6);
      $('[data-co-order]', root).textContent = order;
      const nome = ($('#co-nome').value.trim().split(' ')[0]) || '';
      const email = $('#co-email').value.trim();
      const pag = val('co-pag');
      const entrega = c.tipo === 'retirada'
        ? 'Sua FRIZZA estará esperando na Loja Conceito, em Gramado (RS), em 1 dia útil.'
        : `Entrega em ${$('#co-cidade').value.trim()}/${$('#co-uf').value} em ${c.tipo === 'expressa' ? '2 a 3' : '5 a 8'} dias úteis.`;
      const pagMsg = pag === 'pix' ? `Pague ${brl(c.total)} com o Pix abaixo para liberar o envio.`
        : pag === 'cartao' ? `Pagamento de ${brl(c.total)} aprovado em ${parcelas.value}x sem juros.`
        : `O boleto de ${brl(c.total)} foi enviado para o seu e-mail.`;
      $('[data-co-success-msg]', root).textContent = `Valeu, ${nome}! Enviamos a confirmação para ${email}. ${pagMsg} ${entrega}`;
      $('[data-co-pix]', root).hidden = pag !== 'pix';
      form.hidden = true;
      success.hidden = false;
      labels.forEach((l, k) => { l.classList.toggle('is-current', k === 3); l.classList.toggle('is-done', k < 3); });
      Cart.clear();
      scrollTop();
      success.focus({ preventScroll: true });
      if (motion) gsap.fromTo(success, { y: 30, opacity: 0, scale: 0.97 }, { y: 0, opacity: 1, scale: 1, duration: 0.7, ease: 'back.out(1.5)', clearProps: 'transform,opacity' });
    });

    d.addEventListener('cart:change', render);
    render();
  }

  /* ---------------------------------------------------------------------
     INICIALIZAÇÃO
     ------------------------------------------------------------------- */
  safe('imagens', initImageSlots);
  safe('lenis', initLenis);
  safe('âncoras', initAnchors);
  safe('header', initHeader);
  safe('menu', initMenu);
  safe('cursor', initCursor);
  safe('magnético', initMagnetic);
  safe('tilt', initTilt);
  safe('bolhas', initBubbles);
  safe('demo', initDemoLinks);
  safe('filtros', initFilters);
  safe('lojas', initStores);
  safe('mapa das lojas', initStoreMap);
  safe('lightbox', initLightbox);
  safe('faq', initFaq);
  safe('formulários', initForms);
  safe('carrinho', initCart);
  safe('quiz', initQuiz);
  safe('máscaras', initMasks);
  safe('checkout', initCheckout);
  safe('títulos', splitHeadings);
  safe('reveals', initReveals);
  safe('manifesto', initManifesto);
  safe('contadores', initCounters);
  safe('hero', initHero);
  safe('vitrine', initVitrine);
  safe('sabor', initFlavor);
  safe('linha do tempo', initTimeline);
  safe('mapa', initMap);

  const transitionDone = safe('transição', initPageTransition) || Promise.resolve();
  const preloaderDone = safe('preloader', initPreloader) || Promise.resolve();
  Promise.all([transitionDone, preloaderDone]).then(() => safe('intro', playIntro));

  if (hasGSAP) {
    window.addEventListener('load', () => ScrollTrigger.refresh());
    if (d.fonts && d.fonts.ready) d.fonts.ready.then(() => ScrollTrigger.refresh());
  }
})();
