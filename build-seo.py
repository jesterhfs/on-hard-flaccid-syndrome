#!/usr/bin/env python3
"""Rebuild every page head with full SEO metadata + JSON-LD structured data.

Change SITE below and re-run to re-point the whole site at a different domain.
"""
import io, re, json, os, html

SITE   = 'https://jesterhfs.github.io'
AUTHOR = 'Jesterhfs'
HANDLE = '@jesterhfs'
BRAND  = 'On Hard Flaccid Syndrome'
IMG    = f'{SITE}/jester.png'
IMG_W, IMG_H = 460, 460
PUBLISHED = '2026-08-08'
MODIFIED  = '2026-08-08'

BASE_KW = 'hard flaccid, hard flaccid syndrome, HFS, jesterhfs'

# file: (title, description, keywords-extra, shelf, priority)
P = {
'index.html': (
  'On Hard Flaccid Syndrome (HFS) | Jesterhfs',
  'An open reference on hard flaccid syndrome (HFS): symptoms, causes, '
  'mechanism, every treatment ever tried, and what is still unknown.',
  'hard flaccid research, hard flaccid syndrome treatment, hard flaccid syndrome cure, '
  'hard flaccid reddit, hard flaccid syndrome reddit, hard flaccid syndrome discord, '
  'irwin goldstein, hard flaccid syndrome symptoms, what is hard flaccid syndrome',
  None, '1.0'),

'article.html': (
  'What Is Hard Flaccid Syndrome? Symptoms, Causes, Evidence',
  'Hard flaccid syndrome explained: what the condition is, how it presents, what is known '
  'about the cause, and how strong the evidence for each claim actually is.',
  'what is hard flaccid syndrome, hard flaccid meaning, hard flaccid syndrome definition, '
  'hard flaccid syndrome causes, hard flaccid syndrome symptoms, HFS condition',
  'Start here', '0.9'),

'article-symptoms.html': (
  'Hard Flaccid Syndrome Symptoms: The Complete List',
  'Every symptom reported in hard flaccid syndrome, from the semi-rigid flaccid penis to '
  'cold glans and numbness, each graded by how well it is documented.',
  'hard flaccid syndrome symptoms, hard flaccid symptoms, semi-rigid flaccid penis, '
  'cold glans, penile numbness, hard flaccid pain, testicular retraction',
  'Start here', '0.9'),

'article-self-assessment.html': (
  'Do I Have Hard Flaccid Syndrome? A Self-Assessment',
  'How to tell whether your symptoms fit hard flaccid syndrome, which conditions must be '
  'ruled out first, and why to see a sexual medicine practitioner.',
  'do i have hard flaccid syndrome, hard flaccid syndrome diagnosis, hard flaccid test, '
  'hard flaccid or pelvic floor dysfunction, sexual medicine practitioner',
  'Start here', '0.9'),

'article-news.html': (
  'Hard Flaccid Syndrome News and Research Updates',
  'The latest hard flaccid syndrome research and developments, newest first: FLIR thermal '
  'imaging as a diagnostic, Goldstein’s warming gel, and new treatment data.',
  'hard flaccid syndrome news, hard flaccid research updates, hard flaccid FLIR, '
  'irwin goldstein warming gel, hard flaccid syndrome 2026',
  'Start here', '0.8'),

'article-foundations.html': (
  'Hard Flaccid Syndrome Anatomy: Nerves and Muscles',
  'The muscles, nerves and reflexes involved in hard flaccid syndrome, and why the usual '
  'explanations — pelvic floor, posture, hip mobility — do not hold up.',
  'hard flaccid anatomy, cavernosal smooth muscle, pudendal nerve, hypogastric nerve, '
  'pelvic floor dysfunction hard flaccid, hard flaccid syndrome physiology',
  'Mechanism', '0.75'),

'article-goldstein-theory.html': (
  'Irwin Goldstein’s Hard Flaccid Syndrome Theory Explained',
  'The pelvic/pudendal-hypogastric reflex theory from Irwin Goldstein and San Diego Sexual '
  'Medicine, set out in full, with an honest assessment of the evidence.',
  'irwin goldstein, san diego sexual medicine, goldstein hard flaccid, '
  'pudendal hypogastric reflex, hard flaccid syndrome cause, PGAD, GPD, phentolamine',
  'Mechanism', '0.85'),

'article-conjectures.html': (
  'Hard Flaccid Syndrome Mechanism: Fourteen Conjectures',
  'Fourteen original conjectures on what drives hard flaccid syndrome, organized around '
  'whether the lesion is now neural, in the smooth muscle, or structural.',
  'hard flaccid syndrome mechanism, hard flaccid syndrome cause, what causes hard flaccid, '
  'hard flaccid pathophysiology, RhoA Rho-kinase, sympathetic overactivity',
  'Mechanism', '0.8'),

'article-treatment.html': (
  'Hard Flaccid Syndrome Treatment: What Works',
  'Can hard flaccid syndrome be cured? Every treatment reported in the literature, what the '
  'evidence actually shows, and twelve conjectures for what to try next.',
  'hard flaccid syndrome treatment, hard flaccid syndrome cure, how to cure hard flaccid '
  'syndrome, hard flaccid cure, hard flaccid treatment, tadalafil hard flaccid, '
  'botox hard flaccid, shockwave therapy hard flaccid, hard flaccid recovery',
  'Treatment', '0.95'),

'article-faq.html': (
  'Hard Flaccid Syndrome FAQ: 81 Questions Answered',
  'Direct answers to 81 questions about hard flaccid syndrome — will it go away, can it be '
  'cured, is it permanent, what causes it — with the evidence for each answer.',
  'hard flaccid syndrome questions, does hard flaccid go away, is hard flaccid permanent, '
  'can hard flaccid be cured, hard flaccid syndrome faq, hard flaccid recovery time',
  'Common questions', '0.9'),

'article-glossary.html': (
  'Hard Flaccid Syndrome Glossary: 177 Terms Defined',
  'A glossary of the anatomy, physiology, pharmacology and evidence terminology used to '
  'discuss hard flaccid syndrome, each term in plain language.',
  'hard flaccid glossary, hard flaccid terms, hard flaccid syndrome terminology, '
  'edging, gooning, jelqing, hard flaccid dictionary',
  'Reference', '0.7'),

'article-literature.html': (
  'Hard Flaccid Research: Every Study, Indexed',
  'An annotated index of all hard flaccid syndrome research — every paper, abstract and '
  'preprint, year by year, with what each found and how much weight it carries.',
  'hard flaccid research, hard flaccid syndrome research, hard flaccid syndrome studies, '
  'hard flaccid papers, hard flaccid syndrome literature review, hard flaccid systematic review',
  'Reference', '0.85'),

'article-community.html': (
  'Hard Flaccid Reddit and Discord: Where to Find Help',
  'The hard flaccid syndrome subreddits and Discord servers, and the community members '
  'whose posts and research have shaped what patients believe about the condition.',
  'hard flaccid reddit, hard flaccid syndrome reddit, hard flaccid syndrome discord, '
  'hard flaccid discord, r/hardflaccidresearch, hard flaccid community, hard flaccid forum',
  'Community', '0.85'),

'article-community-surveys.html': (
  'Hard Flaccid Syndrome Surveys: Community Data',
  'Full results of the hard flaccid syndrome community surveys — 153 respondents on '
  'symptoms, 154 on onset — with a precise account of what the numbers can support.',
  'hard flaccid syndrome survey, hard flaccid statistics, how do people get hard flaccid, '
  'hard flaccid syndrome causes survey, hard flaccid data',
  'Community', '0.75'),

'article-thoughts.html': (
  'Some Thoughts on Hard Flaccid Syndrome | Jesterhfs',
  'Forty-one observations on hard flaccid syndrome and the patient community around it, '
  'written from inside that community. Opinion, not evidence.',
  'jesterhfs, hard flaccid community, hard flaccid cure claims, hard flaccid opinion, '
  'hard flaccid reddit drama, hard flaccid activism',
  'Jesterhfs', '0.6'),

'article-case-report.html': (
  'Hard Flaccid Syndrome Case Report | Jesterhfs',
  'A first-person hard flaccid syndrome case report: onset, every investigation ordered, '
  'every treatment attempted, and the outcome after 44 months.',
  'hard flaccid syndrome case report, hard flaccid recovery story, jesterhfs case report, '
  'hard flaccid syndrome experience, hard flaccid 4 years',
  'Jesterhfs', '0.7'),

'article-contact.html': (
  'Contact Jesterhfs | Hard Flaccid Syndrome',
  'How to reach Jesterhfs about hard flaccid syndrome, this site or research: on Discord, '
  'on Reddit as u/jesterhfsplebbit.',
  'contact jesterhfs,',
  'Jesterhfs', '0.4'),
}

PERSON = {
  '@type': 'Person',
  '@id': f'{SITE}/#jesterhfs',
  'name': AUTHOR,
  'alternateName': 'jesterhfs',
  'description': 'Patient and author of On Hard Flaccid Syndrome.',
  'url': f'{SITE}/',
  'sameAs': ['https://x.com/jesterhfs'],
}

WEBSITE = {
  '@type': 'WebSite',
  '@id': f'{SITE}/#website',
  'name': BRAND,
  'alternateName': ['Hard Flaccid Syndrome Reference', 'jesterhfs'],
  'url': f'{SITE}/',
  'description': 'An open reference on hard flaccid syndrome.',
  'inLanguage': 'en',
  'publisher': {'@id': f'{SITE}/#jesterhfs'},
  'author': {'@id': f'{SITE}/#jesterhfs'},
}

CONDITION = {
  '@type': 'MedicalCondition',
  '@id': f'{SITE}/#hard-flaccid-syndrome',
  'name': 'Hard flaccid syndrome',
  'alternateName': ['Hard flaccid', 'HFS', 'Hard-flaccid syndrome'],
  'description': ('A poorly understood penile condition in which the flaccid penis remains '
    'firm and semi-rigid in the absence of sexual arousal, typically beginning after a '
    'mechanical injury to the erect or semi-erect penis, and usually accompanied by sensory '
    'change, erectile dysfunction and pain.'),
  'signOrSymptom': [{'@type': 'MedicalSymptom', 'name': n} for n in [
    'Semi-rigid flaccid penis', 'Cold glans', 'Penile numbness',
    'Loss of spontaneous and nocturnal erections', 'Erectile dysfunction',
    'Penile and perineal pain', 'Testicular retraction',
    'Penile retraction and shortening', 'Symptoms worsening on standing',
    'Penile discoloration', 'Visible or engorged veins']],
  'associatedAnatomy': [{'@type': 'AnatomicalStructure', 'name': n} for n in [
    'Corpus cavernosum', 'Cavernosal smooth muscle', 'Pudendal nerve',
    'Hypogastric nerve', 'Pelvic floor', 'Tunica albuginea']],
  'possibleTreatment': [{'@type': 'MedicalTherapy', 'name': n} for n in [
    'Phosphodiesterase type 5 inhibitors', 'Alpha-1 adrenoceptor antagonists',
    'Pelvic floor physical therapy', 'Low-intensity shockwave therapy',
    'Pudendal nerve block', 'Multimodal rehabilitation']],
  'riskFactor': [{'@type': 'MedicalRiskFactor', 'name': n} for n in [
    'Vigorous or prolonged masturbation', 'Penile enlargement practice (jelqing, stretching, pumping)',
    'Blunt trauma to the erect penis', 'Rough sexual intercourse']],
  'url': f'{SITE}/article.html',
}


def kwstr(f):
    seen, out = set(), []
    for k in f"{BASE_KW}, {P[f][2]}".split(', '):
        if k.lower() not in seen:
            seen.add(k.lower()); out.append(k)
    return ', '.join(out)


def head_block(f):
    title, desc, kw, shelf, prio = P[f]
    url = f'{SITE}/' if f == 'index.html' else f'{SITE}/{f}'
    is_home = f == 'index.html'
    seen, kws = set(), []
    for k in f'{BASE_KW}, {kw}'.split(', '):
        if k.lower() not in seen:
            seen.add(k.lower()); kws.append(k)
    kws = ', '.join(kws)
    e = html.escape
    L = []
    A = L.append
    A('  <meta charset="UTF-8">')
    A('  <meta name="viewport" content="width=device-width, initial-scale=1.0">')
    A('')
    A(f'  <title>{e(title)}</title>')
    A(f'  <meta name="description" content="{e(desc)}">')
    A(f'  <meta name="keywords" content="{e(kws)}">')
    A(f'  <meta name="author" content="{AUTHOR}">')
    A('  <meta name="robots" content="index, follow, max-snippet:-1, max-image-preview:large, max-video-preview:-1">')
    A(f'  <link rel="canonical" href="{url}">')
    A('')
    A(f'  <meta property="og:type" content="{"website" if is_home else "article"}">')
    A(f'  <meta property="og:site_name" content="{BRAND}">')
    A('  <meta property="og:locale" content="en_US">')
    A(f'  <meta property="og:title" content="{e(title)}">')
    A(f'  <meta property="og:description" content="{e(desc)}">')
    A(f'  <meta property="og:url" content="{url}">')
    A(f'  <meta property="og:image" content="{IMG}">')
    A(f'  <meta property="og:image:width" content="{IMG_W}">')
    A(f'  <meta property="og:image:height" content="{IMG_H}">')
    A('  <meta property="og:image:alt" content="A jester playing card, the mark of On Hard Flaccid Syndrome">')
    if not is_home:
        A(f'  <meta property="article:author" content="{AUTHOR}">')
        A(f'  <meta property="article:published_time" content="{PUBLISHED}">')
        A(f'  <meta property="article:modified_time" content="{MODIFIED}">')
        A(f'  <meta property="article:section" content="{e(shelf)}">')
    A('')
    A('  <meta name="twitter:card" content="summary_large_image">')
    A(f'  <meta name="twitter:site" content="{HANDLE}">')
    A(f'  <meta name="twitter:creator" content="{HANDLE}">')
    A(f'  <meta name="twitter:title" content="{e(title)}">')
    A(f'  <meta name="twitter:description" content="{e(desc)}">')
    A(f'  <meta name="twitter:image" content="{IMG}">')
    A('')
    A('  <meta name="theme-color" content="#000000">')
    A('  <meta name="color-scheme" content="dark">')
    A('')
    A('  <link rel="preconnect" href="https://fonts.googleapis.com">')
    A('  <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>')
    A('  <link href="https://fonts.googleapis.com/css2?family=EB+Garamond:ital,wght@0,400;0,500;0,600;0,700;1,400;1,600&display=swap" rel="stylesheet">')
    A('  <link rel="stylesheet" href="styles.css">')
    A("""  <link rel="icon" href="data:image/svg+xml,<svg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 100 100'><text y='.9em' font-size='90'>\U0001f0cf</text></svg>">""")
    A('')
    A('  <script type="application/ld+json">')
    A(json.dumps(jsonld(f), ensure_ascii=False, indent=2))
    A('  </script>')
    return '\n'.join(L)


def balance(t):
    """Drop a quote left dangling by truncation."""
    if t.count('\u201c') > t.count('\u201d'):
        t = t[:t.rfind('\u201c')].rstrip() + '\u2026'
    return t


def strip(s):
    s = re.sub(r'<sup class="cite">.*?</sup>', '', s, flags=re.S)
    s = re.sub(r'<[^>]+>', '', s)
    return re.sub(r'\s+', ' ', html.unescape(s)).strip()


def faq_entities():
    s = io.open('article-faq.html', encoding='utf-8').read()
    out = []
    parts = re.split(r'<h3 id="([^"]+)">(.*?)</h3>', s)
    for i in range(1, len(parts) - 1, 3):
        qid, q, body = parts[i], strip(parts[i + 1]), parts[i + 2]
        body = re.split(r'<h[23]\b|<div class="summary"|<nav class="pager"', body)[0]
        ps = re.findall(r'<p>(.*?)</p>', body, re.S)
        ans = ' '.join(strip(p) for p in ps[:1])
        if not ans:
            continue
        if len(ans) > 320:
            ans = balance(ans[:317].rsplit(' ', 1)[0] + '…')
        out.append({'@type': 'Question', 'name': q,
                    'url': f'{SITE}/article-faq.html#{qid}',
                    'acceptedAnswer': {'@type': 'Answer', 'text': ans}})
    return out


def glossary_terms():
    s = io.open('article-glossary.html', encoding='utf-8').read()
    out = []
    for m in re.finditer(r'<dt>(.*?)</dt>\s*<dd>(.*?)</dd>', s, re.S):
        t, d = strip(m.group(1)), strip(m.group(2))
        if not t or not d:
            continue
        if len(d) > 180:
            d = balance(d[:177].rsplit(' ', 1)[0] + '…')
        out.append({'@type': 'DefinedTerm', 'name': t, 'description': d,
                    'inDefinedTermSet': f'{SITE}/article-glossary.html'})
    return out


def crumbs(f):
    title, desc, kw, shelf, prio = P[f]
    items = [{'@type': 'ListItem', 'position': 1, 'name': 'Home', 'item': f'{SITE}/'}]
    if shelf:
        items.append({'@type': 'ListItem', 'position': 2, 'name': shelf,
                      'item': f'{SITE}/#library'})
        h1 = H1[f]
        items.append({'@type': 'ListItem', 'position': 3, 'name': h1,
                      'item': f'{SITE}/{f}'})
    return {'@type': 'BreadcrumbList', '@id': f'{SITE}/{"" if f=="index.html" else f}#breadcrumb',
            'itemListElement': items}


H1 = {}


def jsonld(f):
    title, desc, kw, shelf, prio = P[f]
    url = f'{SITE}/' if f == 'index.html' else f'{SITE}/{f}'
    g = [PERSON, WEBSITE]

    if f == 'index.html':
        g.append(CONDITION)
        g.append({
            '@type': ['WebPage', 'MedicalWebPage'],
            '@id': url + '#webpage',
            'url': url, 'name': title, 'description': desc,
            'isPartOf': {'@id': f'{SITE}/#website'},
            'about': {'@id': f'{SITE}/#hard-flaccid-syndrome'},
            'inLanguage': 'en',
            'datePublished': PUBLISHED, 'dateModified': MODIFIED,
            'author': {'@id': f'{SITE}/#jesterhfs'},
            'audience': [{'@type': 'MedicalAudience', 'audienceType': 'Patient'},
                         {'@type': 'MedicalAudience', 'audienceType': 'Clinician'}],
        })
        g.append({
            '@type': 'ItemList',
            '@id': url + '#articles',
            'name': 'Articles on hard flaccid syndrome',
            'itemListElement': [
                {'@type': 'ListItem', 'position': i + 1,
                 'url': f'{SITE}/{k}', 'name': P[k][0]}
                for i, k in enumerate(ORDER)],
        })
        return {'@context': 'https://schema.org', '@graph': g}

    page = {
        '@type': ['MedicalWebPage', 'Article'],
        '@id': url + '#webpage',
        'url': url,
        'name': title,
        'headline': H1[f],
        'description': desc,
        'isPartOf': {'@id': f'{SITE}/#website'},
        'about': {'@id': f'{SITE}/#hard-flaccid-syndrome'},
        'inLanguage': 'en',
        'datePublished': PUBLISHED,
        'dateModified': MODIFIED,
        'author': {'@id': f'{SITE}/#jesterhfs'},
        'publisher': {'@id': f'{SITE}/#jesterhfs'},
        'articleSection': shelf,
        'breadcrumb': {'@id': url + '#breadcrumb'},
        'audience': [{'@type': 'MedicalAudience', 'audienceType': 'Patient'},
                     {'@type': 'MedicalAudience', 'audienceType': 'Clinician'}],
        'keywords': kwstr(f),
    }
    if f == 'article-treatment.html':
        page['medicalAudience'] = ['Patient', 'Clinician']
        page['aspect'] = 'Treatment'
    elif f == 'article-symptoms.html':
        page['aspect'] = 'Symptoms'
    elif f == 'article-self-assessment.html':
        page['aspect'] = 'Diagnosis'
    elif f in ('article-conjectures.html', 'article-goldstein-theory.html',
               'article-foundations.html'):
        page['aspect'] = 'Causes'
    g.append(page)
    g.append(crumbs(f))

    if f == 'article-faq.html':
        qs = faq_entities()
        g.append({'@type': 'FAQPage', '@id': url + '#faq',
                  'url': url, 'name': title, 'mainEntity': qs})
    if f == 'article-glossary.html':
        g.append({'@type': 'DefinedTermSet', '@id': url + '#glossary',
                  'url': url, 'name': 'Hard flaccid syndrome glossary',
                  'description': desc, 'hasDefinedTerm': glossary_terms()})
    return {'@context': 'https://schema.org', '@graph': g}


# ---- order from the index shelves ----
idx = io.open('index.html', encoding='utf-8').read()
ORDER = re.findall(r'<a class="entry" href="([^"]+)"', idx)

for f in list(P):
    s = io.open(f, encoding='utf-8').read()
    m = re.search(r'<h1>(.*?)</h1>', s, re.S)
    H1[f] = strip(m.group(1)) if m else P[f][0]
H1['index.html'] = 'Hard flaccid syndrome, as far as the evidence goes.'

assert set(ORDER) | {'index.html'} == set(P), set(ORDER) ^ set(P)

for f in list(P):
    s = io.open(f, encoding='utf-8').read()
    new = re.sub(r'(?s)<head>\n.*?\n</head>',
                 lambda m: '<head>\n' + head_block(f) + '\n</head>', s, count=1)
    assert '<link rel="canonical"' in new, f
    io.open(f, 'w', encoding='utf-8').write(new)
    print(f'  head rebuilt: {f}')

# ---- sitemap.xml ----
sm = ['<?xml version="1.0" encoding="UTF-8"?>',
      '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">']
for f in ['index.html'] + ORDER:
    loc = f'{SITE}/' if f == 'index.html' else f'{SITE}/{f}'
    sm.append('  <url>')
    sm.append(f'    <loc>{loc}</loc>')
    sm.append(f'    <lastmod>{MODIFIED}</lastmod>')
    sm.append('    <changefreq>monthly</changefreq>')
    sm.append(f'    <priority>{P[f][4]}</priority>')
    sm.append('  </url>')
sm.append('</urlset>')
io.open('sitemap.xml', 'w', encoding='utf-8').write('\n'.join(sm) + '\n')
print('  wrote sitemap.xml')

# ---- robots.txt ----
io.open('robots.txt', 'w', encoding='utf-8').write(
f"""# On Hard Flaccid Syndrome — {SITE}
User-agent: *
Allow: /

Sitemap: {SITE}/sitemap.xml
""")
print('  wrote robots.txt')
