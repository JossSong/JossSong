/* ============================================
   Joss · Home — main.js
   Starfield · parallax · intro transitions
============================================ */

(function () {
  'use strict';

  const reduceMotion = window.matchMedia('(prefers-reduced-motion: reduce)').matches;
  const coarsePointer = window.matchMedia('(pointer: coarse)').matches;

  /* ---------- Starfield (canvas) ---------- */
  const canvas = document.getElementById('starfield');
  if (canvas && canvas.getContext) {
    const ctx = canvas.getContext('2d');
    const dpr = Math.min(window.devicePixelRatio || 1, 2);
    let stars = [];
    const STAR_COUNT = coarsePointer ? 110 : 220;

    function resize () {
      const w = canvas.parentElement.clientWidth;
      const h = canvas.parentElement.clientHeight;
      canvas.width = w * dpr;
      canvas.height = h * dpr;
      ctx.setTransform(dpr, 0, 0, dpr, 0, 0);
      seed(w, h);
      drawW = w; drawH = h;
    }
    let drawW = 0, drawH = 0;

    function rand (min, max) { return min + Math.random() * (max - min); }

    function seed (w, h) {
      stars = [];
      for (let i = 0; i < STAR_COUNT; i++) {
        stars.push({
          x: Math.random() * w,
          y: Math.random() * h * 0.78,           // keep stars in upper sky
          r: rand(0.4, 1.6),
          a: rand(0.3, 0.95),
          tw: rand(0.005, 0.022),                // twinkle speed
          ph: Math.random() * Math.PI * 2,       // phase
          hue: Math.random() < 0.85 ? '#ffffff' : (Math.random() < 0.5 ? '#cfe2ff' : '#ffe9b8'),
        });
      }
    }

    let t = 0;
    function draw () {
      const w = drawW, h = drawH;
      ctx.clearRect(0, 0, w, h);
      t += 1;
      for (let i = 0; i < stars.length; i++) {
        const s = stars[i];
        const a = s.a * (0.6 + 0.4 * Math.sin(s.ph + t * s.tw));
        ctx.globalAlpha = a;
        ctx.fillStyle = s.hue;
        ctx.beginPath();
        ctx.arc(s.x, s.y, s.r, 0, Math.PI * 2);
        ctx.fill();
        // soft glow for bigger stars
        if (s.r > 1.1) {
          ctx.globalAlpha = a * 0.18;
          ctx.beginPath();
          ctx.arc(s.x, s.y, s.r * 3, 0, Math.PI * 2);
          ctx.fill();
        }
      }
      ctx.globalAlpha = 1;
      if (!reduceMotion) requestAnimationFrame(draw);
    }

    resize();
    draw();
    window.addEventListener('resize', resize, { passive: true });
  }

  /* ---------- Mouse parallax ---------- */
  const parallax = document.getElementById('parallax');
  if (parallax && !reduceMotion && !coarsePointer) {
    let raf = null;
    let tx = 0, ty = 0, cx = 0, cy = 0;
    const MAX = 14;

    function onMove (e) {
      const w = window.innerWidth, h = window.innerHeight;
      const nx = (e.clientX / w - 0.5) * 2;       // -1..1
      const ny = (e.clientY / h - 0.5) * 2;
      tx = -nx * MAX;
      ty = -ny * MAX;
      if (!raf) raf = requestAnimationFrame(loop);
    }
    function loop () {
      cx += (tx - cx) * 0.08;
      cy += (ty - cy) * 0.08;
      parallax.style.setProperty('--tx', cx.toFixed(2) + 'px');
      parallax.style.setProperty('--ty', cy.toFixed(2) + 'px');
      if (Math.abs(tx - cx) > 0.05 || Math.abs(ty - cy) > 0.05) {
        raf = requestAnimationFrame(loop);
      } else {
        raf = null;
      }
    }
    window.addEventListener('mousemove', onMove, { passive: true });
  }

  /* ---------- Intro overlay ---------- */
  const intro = document.getElementById('intro');
  const scroller = intro ? intro.querySelector('.intro__inner') : null;   // actual scroll container
  const charBtn = document.getElementById('character');
  const backBtn = intro ? intro.querySelector('.intro__back') : null;
  const introTopBtn = document.getElementById('introTop');

  function updateIntroTopBtn () {
    if (!intro || !introTopBtn || !scroller) return;
    const shown = intro.classList.contains('is-open') && scroller.scrollTop > 320;
    introTopBtn.classList.toggle('is-shown', shown);
  }

  function openIntro () {
    if (!intro) return;
    intro.setAttribute('aria-hidden', 'false');
    intro.classList.add('is-open');
    if (history.pushState) history.pushState({ intro: true }, '', '#about');
    // focus the close button for keyboard users
    setTimeout(() => backBtn && backBtn.focus(), 700);
    updateIntroTopBtn();
  }

  function closeIntro () {
    if (!intro) return;
    intro.classList.remove('is-open');
    intro.setAttribute('aria-hidden', 'true');
    if (history.pushState && location.hash === '#about') history.back();
    updateIntroTopBtn();
  }

  if (charBtn) charBtn.addEventListener('click', openIntro);
  if (backBtn) backBtn.addEventListener('click', closeIntro);
  if (scroller) {
    scroller.addEventListener('scroll', updateIntroTopBtn, { passive: true });
  }
  if (introTopBtn && scroller) {
    introTopBtn.addEventListener('click', () => {
      scroller.scrollTo({ top: 0, behavior: reduceMotion ? 'auto' : 'smooth' });
    });
  }

  document.addEventListener('keydown', (e) => {
    if (e.key === 'Escape' && intro && intro.classList.contains('is-open')) closeIntro();
  });

  // Deep-link: open intro if URL has #about
  if (location.hash === '#about') {
    // wait for layout
    requestAnimationFrame(openIntro);
  }
  window.addEventListener('hashchange', () => {
    if (location.hash === '#about') openIntro();
    else closeIntro();
  });

  /* ---------- Day / Night theme (default follows system) ---------- */
  const root = document.documentElement;
  let lang = 'zh';
  const themeToggle = document.getElementById('themeToggle');
  const metaTheme = document.querySelector('meta[name="theme-color"]');
  const sysLight = window.matchMedia('(prefers-color-scheme: light)');

  function resolveSystemTheme () {
    return sysLight.matches ? 'day' : 'night';
  }

  function applyTheme (theme) {
    root.dataset.theme = theme;
    if (metaTheme) metaTheme.setAttribute('content', theme === 'day' ? '#79bde8' : '#05081a');
    updateThemeLabels();
  }

  function currentMode () {
    const m = root.dataset.mode;
    return (m === 'day' || m === 'night') ? m : 'night';
  }

  function updateThemeLabels () {
    if (!themeToggle) return;
    const mode = currentMode();
    const labels = {
      day:  { zh: '主题：日间（点击切换）', en: 'Theme: day (click to change)' },
      night:{ zh: '主题：夜间（点击切换）', en: 'Theme: night (click to change)' },
    };
    const l = labels[mode][currentLang()];
    themeToggle.setAttribute('aria-label', l);
    themeToggle.setAttribute('title', l);
  }

  // no explicit choice until the user clicks; before that, follow the system live
  let userChose = false;
  try {
    const s = localStorage.getItem('joss-theme');
    userChose = (s === 'day' || s === 'night');
  } catch (e) {}

  function applyMode (mode, explicit) {
    if (explicit) userChose = true;
    root.dataset.mode = mode;
    applyTheme(mode);
  }

  // initial mode was resolved pre-paint by the inline <head> script
  if (!root.dataset.mode) applyMode(resolveSystemTheme());
  else updateThemeLabels();

  // keep tracking the OS until the user makes an explicit choice
  sysLight.addEventListener('change', () => {
    if (!userChose) applyTheme(resolveSystemTheme());
  });

  if (themeToggle) {
    themeToggle.addEventListener('click', () => {
      const order = ['day', 'night'];
      const next = order[(order.indexOf(currentMode()) + 1) % order.length];
      applyMode(next, true);
      try { localStorage.setItem('joss-theme', next); } catch (e) {}
    });
  }

  /* ---------- i18n (中文 / English) ---------- */
  const I18N = {
    zh: {
      'meta.title': '宋京 SONG JING · 仰望星辰 脚踏实地',
      'meta.desc': '宋京（Joss.Song）—— 通识集团创始人兼CEO，宋京工作室，简道奠基人。创业者，投资人，懂点技术，偶尔写作，喜欢喝茶or咖啡，广交好友。',
      'hero.hint': '点我 · about',
      'hero.brandSub': 'Joss.Song',
      'hero.signature': '仰望星辰 · 脚踏实地',
      'hero.characterAria': '打开宋京的个人介绍',
      'intro.backAria': '返回首页',
      'intro.back': '返回首页',
      'intro.topAria': '回到顶部',
      'intro.hi': '通识集团 · 宋京工作室 · 简道奠基人',
      'intro.nameZh': '宋京',
      'intro.nameEn': 'SONG\u00a0JING',
      'intro.k1': '学名', 'intro.v1': '進京',
      'intro.k2': '字', 'intro.v2': '子京',
      'intro.k3': '号', 'intro.v3': '乌莲居士 · 乌莲先生',
      'intro.k4': '英文名', 'intro.v4': 'Joss.Song',
      'intro.k5': '国籍', 'intro.v5': '中国',
      'intro.role': '创业者 · 投资人 · 懂点技术 · 偶尔写作 · 喜欢喝茶 · 广交好友',
      'intro.sub': '金融投资顾问 / 工程师',
      'intro.secContact': '联系我',
      'intro.secSkills': '爱好领域',
      'intro.secWorks': '作品',
      'intro.secTimeline': '详细介绍',
      'chip.1': '教育', 'chip.2': '心理', 'chip.3': '管理', 'chip.4': '历史', 'chip.5': '产品',
      'chip.6': '设计', 'chip.7': '编程', 'chip.8': '文学', 'chip.9': '经济', 'chip.10': '艺术',
      'chip.11': '科普', 'chip.12': '超文明', 'chip.13': '科创', 'chip.14': '文艺', 'chip.15': '美食',
      'chip.16': '旅行', 'chip.17': '健身', 'chip.18': '茶道', 'chip.19': '写作',
      'work.1.title': '《简~道》', 'work.1.sub': '简道奠基之作',
      'work.2.title': '《元宇集》', 'work.2.sub': '元宇宙思辨文集',
      'tl.1.title': '出生于山东菏泽', 'tl.1.desc': '男，汉族，无党派人士。',
      'tl.3.title': '考入天津大学', 'tl.3.desc': '通过自学考入 MEM 专业在职研究生。',
      'tl.4.title': '「中国最杰出的未来主义者」', 'tl.4.desc': '被《时代》周刊评价。',
      'tl.5.title': '一战成名', 'tl.5.desc': '发表学术论文《数字社会及其未来》引发大量关注；结识互联网大佬，共同研发两款超级 APP；同年登上《时代周刊》与《商界》，后《经济学人》《纽约时报》《路透社》争相报道。',
      'tl.6.title': '通识集团香港挂牌', 'tl.6.desc': '通识集团创始人兼首席执行官（CEO）。',
      'tl.7.title': '销声匿迹', 'tl.7.desc': '暂别公众视野，潜心修行。',
      'tl.8.title': '创办宋京基金会 · 出版《简道》', 'tl.8.desc': '同年 9 月出书《简道》。',
      'intro.quote': '当地著名企业家，著名学者。',
      'intro.quoteCite': '—— 地位评价',
      'intro.email': '邮件联系',
      'social.aria': '社交联系方式',
      'map.title': '足迹 · 人生轨迹',
      'map.sub': '先环游中国，再环游世界',
      'map.aria': '宋京人生足迹：先环游中国，再环游世界',
      'map.phase1': '① 环游中国',
      'map.phase2': '② 环游世界',
      'map.c1': '菏泽', 'map.c1y': '1998 · 出生',
      'map.c2': '济南',
      'map.c3': '天津', 'map.c3y': '2024 · 深造',
      'map.c4': '北京',
      'map.c5': '哈尔滨',
      'map.c6': '乌鲁木齐',
      'map.c7': '拉萨',
      'map.c8': '成都',
      'map.c9': '昆明',
      'map.c10': '广州',
      'map.c11': '上海', 'map.c11y': '2026 · 事业',
      'map.c12': '香港', 'map.c12y': '2028 · 挂牌',
      'map.c13': '新加坡', 'map.c13y': '2029 · 远航',
      'map.c14': '东京', 'map.c14y': '2030 · 东渡',
      'map.c15': '悉尼',
      'map.c16': '伦敦', 'map.c16y': '2031 · 讲学',
      'map.c17': '巴黎',
      'map.c18': '纽约', 'map.c18y': '2033 · 时代',
      'map.c19': '旧金山', 'map.c19y': '2034 · 硅谷',
      'map.future': '未来 · 星辰大海',
      'lang.toggleAria': 'Switch to English',
    },
    en: {
      'meta.title': 'Joss Song · Be All You Can Be!',
      'meta.desc': 'Song Jing (Joss.Song) — Founder & CEO of Tongshi Group, Song Jing Studio, founder of Jiandao. Entrepreneur, investor, tech-savvy, occasional writer, tea lover, and a friend to all.',
      'hero.hint': 'Tap me · About',
      'hero.brandSub': 'Joss.Song',
      'hero.signature': 'Reach for the stars · Stand on the ground',
      'hero.characterAria': "Open Song Jing's profile",
      'intro.backAria': 'Back to home',
      'intro.back': 'Back to Home',
      'intro.topAria': 'Back to top',
      'intro.hi': 'Tongshi Group · Song Jing Studio · Founder of Jiandao',
      'intro.nameZh': 'Song Jing',
      'intro.nameEn': '宋京',
      'intro.k1': 'Scholarly name', 'intro.v1': 'Jinjing',
      'intro.k2': 'Courtesy name', 'intro.v2': 'Zijing',
      'intro.k3': 'Art name', 'intro.v3': 'Wulian Jushi · Mr. Wulian',
      'intro.k4': 'English name', 'intro.v4': 'Joss.Song',
      'intro.k5': 'Nationality', 'intro.v5': 'China',
      'intro.role': 'Entrepreneur · Investor · Tech-savvy · Occasional writer · Tea lover · A friend to all',
      'intro.sub': 'Financial Investment Advisor / Engineer',
      'intro.secContact': 'Contact Me',
      'intro.secSkills': 'Fields of Interest',
      'intro.secWorks': 'Works',
      'intro.secTimeline': 'Journey in Detail',
      'chip.1': 'Education', 'chip.2': 'Psychology', 'chip.3': 'Management', 'chip.4': 'History', 'chip.5': 'Product',
      'chip.6': 'Design', 'chip.7': 'Programming', 'chip.8': 'Literature', 'chip.9': 'Economics', 'chip.10': 'Art',
      'chip.11': 'Science', 'chip.12': 'Meta-civilization', 'chip.13': 'Tech Innovation', 'chip.14': 'Arts & Letters', 'chip.15': 'Cuisine',
      'chip.16': 'Travel', 'chip.17': 'Fitness', 'chip.18': 'Tea Ceremony', 'chip.19': 'Writing',
      'work.1.title': 'Jian Dao (《简~道》)', 'work.1.sub': 'The foundational work of Jiandao',
      'work.2.title': 'Yuan Yu Ji (《元宇集》)', 'work.2.sub': 'Essays on the metaverse',
      'tl.1.title': 'Born in Heze, Shandong', 'tl.1.desc': 'Male, Han Chinese, non-partisan.',
      'tl.3.title': 'Admitted to Tianjin University', 'tl.3.desc': 'Entered the part-time MEM graduate program through self-study.',
      'tl.4.title': '"China\u2019s Most Outstanding Futurist"', 'tl.4.desc': 'As named by TIME magazine.',
      'tl.5.title': 'Rise to Fame', 'tl.5.desc': 'Published the academic paper "Digital Society and Its Future" to wide acclaim; co-built two super apps with an internet mogul; featured by TIME and Business that year, followed by The Economist, The New York Times and Reuters.',
      'tl.6.title': 'Tongshi Group Listed in Hong Kong', 'tl.6.desc': 'Founder and Chief Executive Officer (CEO) of Tongshi Group.',
      'tl.7.title': 'Off the Grid', 'tl.7.desc': 'Stepped away from public view for quiet cultivation.',
      'tl.8.title': 'Founded the Song Jing Foundation · Published Jian Dao', 'tl.8.desc': 'Published the book Jian Dao in September of that year.',
      'intro.quote': 'A renowned local entrepreneur and scholar.',
      'intro.quoteCite': '— Recognition',
      'intro.email': 'Email Me',
      'social.aria': 'Social links',
      'map.title': 'Footprints · Life Journey',
      'map.sub': 'First around China, then around the world',
      'map.aria': "Song Jing's footprints: first around China, then around the world",
      'map.phase1': 'I. Around China',
      'map.phase2': 'II. Around the World',
      'map.c1': 'Heze', 'map.c1y': '1998 · Born',
      'map.c2': 'Jinan',
      'map.c3': 'Tianjin', 'map.c3y': '2024 · Grad school',
      'map.c4': 'Beijing',
      'map.c5': 'Harbin',
      'map.c6': 'Urumqi',
      'map.c7': 'Lhasa',
      'map.c8': 'Chengdu',
      'map.c9': 'Kunming',
      'map.c10': 'Guangzhou',
      'map.c11': 'Shanghai', 'map.c11y': '2026 · Career',
      'map.c12': 'Hong Kong', 'map.c12y': '2028 · IPO',
      'map.c13': 'Singapore', 'map.c13y': '2029 · Voyage',
      'map.c14': 'Tokyo', 'map.c14y': '2030 · Eastward',
      'map.c15': 'Sydney',
      'map.c16': 'London', 'map.c16y': '2031 · Lectures',
      'map.c17': 'Paris',
      'map.c18': 'New York', 'map.c18y': '2033 · TIME',
      'map.c19': 'San Francisco', 'map.c19y': '2034 · Silicon',
      'map.future': 'Future · Sea of Stars',
      'lang.toggleAria': '切换到中文',
    },
  };

  function currentLang () { return lang; }

  function detectLang () {
    try {
      const saved = localStorage.getItem('joss-lang');
      if (saved === 'zh' || saved === 'en') return saved;
    } catch (e) {}
    const langs = navigator.languages && navigator.languages.length
      ? navigator.languages
      : [navigator.language || 'en'];
    return langs.some((l) => (l || '').toLowerCase().indexOf('zh') === 0) ? 'zh' : 'en';
  }

  function applyLang (next) {
    lang = next === 'en' ? 'en' : 'zh';
    const dict = I18N[lang];
    document.querySelectorAll('[data-i18n]').forEach((el) => {
      const v = dict[el.dataset.i18n];
      if (typeof v === 'string') el.textContent = v;
    });
    document.querySelectorAll('[data-i18n-aria]').forEach((el) => {
      const v = dict[el.dataset.i18nAria];
      if (typeof v === 'string') {
        el.setAttribute('aria-label', v);
        if (el.hasAttribute('title')) el.setAttribute('title', v);
      }
    });
    document.documentElement.lang = lang === 'en' ? 'en' : 'zh-CN';
    document.title = dict['meta.title'];
    const metaDesc = document.querySelector('meta[name="description"]');
    if (metaDesc) metaDesc.setAttribute('content', dict['meta.desc']);

    const langToggle = document.getElementById('langToggle');
    if (langToggle) {
      const toLabel = lang === 'zh' ? 'EN' : '中';
      langToggle.textContent = toLabel;
      langToggle.setAttribute('aria-label', dict['lang.toggleAria']);
      langToggle.setAttribute('title', dict['lang.toggleAria']);
    }
    // Language-conditional social chips: only show the ones matching the active language
    document.querySelectorAll('[data-show-lang]').forEach((el) => {
      const want = el.dataset.showLang;
      el.classList.toggle('is-hidden', want !== lang);
    });
    updateThemeLabels();
  }

  const langToggle = document.getElementById('langToggle');
  if (langToggle) {
    langToggle.addEventListener('click', () => {
      applyLang(lang === 'zh' ? 'en' : 'zh');
      try { localStorage.setItem('joss-lang', lang); } catch (e) {}
    });
  }

  applyLang(detectLang());

  /* ---------- Subtle entrance ---------- */
  document.body.classList.add('is-ready');
})();
