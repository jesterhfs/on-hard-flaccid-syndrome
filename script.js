/* =========================================================
   On Hard Flaccid Syndrome — shared behavior
   Loaded by both index.html and article.html; every block
   guards on the elements it needs, so nothing breaks when a
   page doesn't have them.
   ========================================================= */

const $  = (sel, root = document) => root.querySelector(sel);
const $$ = (sel, root = document) => Array.from(root.querySelectorAll(sel));

/* ---------- Footer year ---------- */

const yearSlot = $('#year');
if (yearSlot) yearSlot.textContent = new Date().getFullYear();

/* ---------- Mobile navigation ---------- */

const navToggle = $('#nav-toggle');
const navList = $('#nav-list');

if (navToggle && navList) {
  const closeNav = () => {
    navList.classList.remove('open');
    navToggle.setAttribute('aria-expanded', 'false');
  };

  navToggle.addEventListener('click', () => {
    const open = navList.classList.toggle('open');
    navToggle.setAttribute('aria-expanded', String(open));
  });

  navList.addEventListener('click', (e) => {
    if (e.target.closest('a')) closeNav();
  });

  document.addEventListener('keydown', (e) => {
    if (e.key === 'Escape') closeNav();
  });
}

/* ---------- Hairline under the masthead once scrolled ---------- */

const masthead = $('#masthead');

if (masthead) {
  const syncMasthead = () => masthead.classList.toggle('scrolled', window.scrollY > 6);
  syncMasthead();
  window.addEventListener('scroll', syncMasthead, { passive: true });
}

/* ---------- Full-text search (home page) ----------
   Searches the text of every section of every article, using the index in
   search-index.js. Results link straight to the section they matched.
   Regenerate the index with: python3 build-search-index.py
*/

const search = $('#search');

if (search) {
  const libraryList = $('#library-list');
  const resultsBox = $('#results');
  const countSlot = $('#search-count');
  const noResults = $('#no-results');
  const index = window.SEARCH_INDEX || [];

  const MAX_RESULTS = 40;
  const SNIPPET = 170;

  const escapeHTML = (s) => s.replace(/[&<>"']/g, (c) => (
    { '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#39;' }[c]
  ));

  const escapeRegExp = (s) => s.replace(/[.*+?^${}()|[\]\\]/g, '\\$&');

  // Highlight every search term inside an already-escaped string.
  const highlight = (escaped, terms) => {
    if (!terms.length) return escaped;
    const pattern = new RegExp(`(${terms.map(escapeRegExp).join('|')})`, 'gi');
    return escaped.replace(pattern, '<mark>$1</mark>');
  };

  // A window of text centred on the first term that appears in it.
  const snippet = (text, terms) => {
    let at = -1;
    const lower = text.toLowerCase();
    terms.forEach((term) => {
      const found = lower.indexOf(term);
      if (found !== -1 && (at === -1 || found < at)) at = found;
    });

    if (at === -1) {
      return text.length > SNIPPET ? `${text.slice(0, SNIPPET).trim()}…` : text;
    }

    const start = Math.max(0, at - Math.floor(SNIPPET / 3));
    const end = Math.min(text.length, start + SNIPPET);
    return (start > 0 ? '…' : '') + text.slice(start, end).trim() + (end < text.length ? '…' : '');
  };

  // Heading matches beat title matches, which beat body matches.
  const score = (record, terms) => {
    const heading = record.h.toLowerCase();
    const title = record.t.toLowerCase();
    const body = record.x.toLowerCase();
    let total = 0;

    for (const term of terms) {
      if (!heading.includes(term) && !title.includes(term) && !body.includes(term)) return 0;
      if (heading.includes(term)) total += 60;
      if (heading.startsWith(term)) total += 25;
      if (title.includes(term)) total += 15;
      total += Math.min(body.split(term).length - 1, 8) * 3;
    }

    // Reference lists match a lot of terms without explaining anything, so
    // they sit below prose that actually discusses the subject.
    if (record.a === 'references') total *= 0.35;

    return total;
  };

  const render = (matches, terms) => {
    resultsBox.innerHTML = matches.map(({ r }) => {
      const parts = [r.c, r.t, r.s].filter(Boolean).filter((v, i, a) => a.indexOf(v) === i);
      const crumb = parts.map(escapeHTML).join(' <span aria-hidden="true">·</span> ');
      const heading = highlight(escapeHTML(r.h), terms);
      const text = highlight(escapeHTML(snippet(r.x, terms)), terms);
      return `<a class="result" href="${r.f}#${r.a}">`
        + `<span class="result-crumb">${crumb}</span>`
        + `<span class="result-heading">${heading}</span>`
        + `<span class="result-snippet">${text}</span>`
        + '</a>';
    }).join('');
  };

  const run = () => {
    const query = search.value.trim();
    const terms = query.toLowerCase().split(/\s+/).filter(Boolean);

    if (!terms.length) {
      resultsBox.hidden = true;
      resultsBox.innerHTML = '';
      if (libraryList) libraryList.hidden = false;
      if (noResults) noResults.hidden = true;
      if (countSlot) countSlot.textContent = '';
      return;
    }

    const matches = index
      .map((r) => ({ r, s: score(r, terms) }))
      .filter((m) => m.s > 0)
      .sort((a, b) => b.s - a.s)
      .slice(0, MAX_RESULTS);

    if (libraryList) libraryList.hidden = true;
    resultsBox.hidden = matches.length === 0;
    if (noResults) noResults.hidden = matches.length > 0;

    if (matches.length) render(matches, terms);

    if (countSlot) {
      const articles = new Set(matches.map((m) => m.r.f)).size;
      const capped = matches.length === MAX_RESULTS ? 'top ' : '';
      countSlot.textContent = matches.length
        ? `${capped}${matches.length} result${matches.length === 1 ? '' : 's'} in ${articles} article${articles === 1 ? '' : 's'}`
        : 'no matches';
    }
  };

  if (!index.length) {
    search.placeholder = 'Search unavailable — run build-search-index.py';
    search.disabled = true;
  } else {
    search.addEventListener('input', run);

    // Escape clears the field rather than just closing the mobile nav.
    search.addEventListener('keydown', (e) => {
      if (e.key === 'Escape' && search.value) {
        e.stopPropagation();
        search.value = '';
        run();
      }
    });
  }
}

/* ---------- Reading progress (article page) ---------- */

const progress = $('#progress i');

if (progress) {
  const updateProgress = () => {
    const scrollable = document.documentElement.scrollHeight - window.innerHeight;
    const ratio = scrollable > 0 ? window.scrollY / scrollable : 0;
    progress.style.width = `${Math.min(Math.max(ratio, 0), 1) * 100}%`;
  };

  updateProgress();
  window.addEventListener('scroll', updateProgress, { passive: true });
  window.addEventListener('resize', updateProgress);
}

/* ---------- Table of contents, built from the article's headings ---------- */

const tocList = $('#toc-list');
const articleBody = $('#article-body');

if (tocList && articleBody) {
  const headings = $$('h2[id]', articleBody);

  headings.forEach((h) => {
    // Strip evidence badges so the contents list reads as plain section titles.
    const label = Array.from(h.childNodes)
      .filter((n) => !(n.nodeType === 1 && n.classList.contains('tag')))
      .map((n) => n.textContent)
      .join('')
      .trim();

    const li = document.createElement('li');
    const a = document.createElement('a');
    a.href = `#${h.id}`;
    a.textContent = label;
    li.append(a);
    tocList.append(li);
  });

  const links = new Map(headings.map((h, i) => [h.id, tocList.children[i].firstChild]));

  // Highlight the heading nearest the top of the viewport.
  const spy = new IntersectionObserver((entries) => {
    entries.forEach((entry) => {
      const link = links.get(entry.target.id);
      if (!link) return;
      if (entry.isIntersecting) {
        links.forEach((l) => l.classList.remove('active'));
        link.classList.add('active');
      }
    });
  }, { rootMargin: '-90px 0px -70% 0px', threshold: 0 });

  headings.forEach((h) => spy.observe(h));
}

/* ---------- Share button ---------- */

const shareBtn = $('#share');

if (shareBtn) {
  shareBtn.addEventListener('click', async () => {
    const payload = {
      title: document.title,
      url: location.href,
    };

    try {
      if (navigator.share) {
        await navigator.share(payload);
        return;
      }
      await navigator.clipboard.writeText(payload.url);
      const original = shareBtn.textContent;
      shareBtn.textContent = 'Link copied';
      setTimeout(() => { shareBtn.textContent = original; }, 1800);
    } catch {
      // Cancelled share or blocked clipboard — nothing to report.
    }
  });
}

/* ---------- Subscribe form ---------- */
//
// NOTE: this validates the address but does not send it anywhere. There is no
// backend. To make it live, POST from `subscribeEmail` below to Buttondown,
// Mailchimp, Formspree, or your own endpoint.

const subForm = $('#subscribe-form');

if (subForm) {
  const input = $('#sub-email', subForm);
  const status = $('#sub-status');

  async function subscribeEmail(email) {
    console.log('Subscribe requested (not sent anywhere yet):', email);
    throw new Error('not-wired');
  }

  subForm.addEventListener('submit', async (e) => {
    e.preventDefault();
    const email = input.value.trim();
    const valid = /^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(email);

    input.setAttribute('aria-invalid', String(!valid));

    if (!valid) {
      status.textContent = 'That email address doesn’t look right.';
      input.focus();
      return;
    }

    try {
      await subscribeEmail(email);
      subForm.reset();
      status.textContent = 'Thanks — you’re on the list.';
    } catch {
      status.textContent = 'Not connected to a mailing list yet — see subscribeEmail() in script.js.';
    }
  });
}
