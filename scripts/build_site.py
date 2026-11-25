#!/usr/bin/env python3
"""Static site generator for PracticalUtility (practical-utility.com).
Generates:
- guides/<id>.html (dedicated SEO pages with Article JSON-LD, Top Pick verdict, Related Guides, Author bio)
- about.html (E-E-A-T About & Affiliate Disclosure page)
- index.html (lightweight homepage with crawlable <a href="./guides/..."> links, Categories drawer, & World News)
- sitemap.xml & robots.txt
"""
import datetime
import html
import json
import os
from pathlib import Path

BASE_URL = "https://practical-utility.com"
ROOT = Path(__file__).resolve().parent.parent
GUIDES_DIR = ROOT / "guides"
GUIDES_DIR.mkdir(exist_ok=True)


def esc(s):
    return html.escape(str(s or ""), quote=True)


def default_image_for(article):
    img = article.get("image") or ""
    if img.startswith("images/") and (ROOT / img).exists():
        return img
    aid = (article.get("id") or "").lower()
    cat = (article.get("category") or "").lower()
    if any(k in aid for k in ("dehumidifier", "mini-split")):
        return "images/dehumidifier-basement.jpg"
    if any(k in aid for k in ("tankless", "softener", "sediment")):
        return "images/tankless-water-heater.jpg"
    if any(k in aid for k in ("invoic", "billing", "accounting", "job-costing")):
        return "images/invoicing-desk.jpg"
    if any(k in aid for k in ("hvac", "merv", "filter-pressure")) or "home" in cat:
        return "images/hvac-air.jpg"
    if any(k in aid for k in ("water", "pfas", "countertop")) or "water" in cat:
        return "images/water-filter.jpg"
    return "images/trades-finance.jpg"


def render_guide_page(article, all_articles):
    aid = article["id"]
    title = article["title"]
    cat = article.get("category", "Home Utility")
    kw = article.get("keyword", "")
    summary = article.get("summary", "")
    read_time = article.get("readTime", "6 min read")
    updated = article.get("updated") or datetime.date.today().isoformat()
    partner = article.get("partner", "")
    partner_url = article.get("partnerUrl", "")
    img = default_image_for(article)
    body = article.get("body", [])
    sources = article.get("sources", [])
    canonical = f"{BASE_URL}/guides/{aid}.html"

    related = [a for a in all_articles if a["id"] != aid and a.get("category") == cat][:3]
    if len(related) < 3:
        for a in all_articles:
            if a["id"] != aid and a not in related:
                related.append(a)
            if len(related) == 3:
                break

    ld_json = json.dumps({
        "@context": "https://schema.org",
        "@type": "Article",
        "headline": title,
        "description": summary,
        "image": f"{BASE_URL}/{img}",
        "dateModified": updated,
        "datePublished": updated,
        "author": {
            "@type": "Person",
            "name": "Puneet Sharma",
            "url": f"{BASE_URL}/about.html"
        },
        "publisher": {
            "@type": "Organization",
            "name": "PracticalUtility",
            "url": BASE_URL
        },
        "mainEntityOfPage": canonical
    }, ensure_ascii=False)

    verdict_html = ""
    if partner and partner_url:
        verdict_html = f"""
      <div class="my-6 p-5 rounded-2xl bg-emerald-50/70 border border-emerald-200 flex flex-col sm:flex-row sm:items-center justify-between gap-4">
        <div>
          <p class="text-sm font-semibold uppercase tracking-wider text-emerald-800">Top Recommended Option</p>
          <p class="text-base font-bold text-slate-900 mt-0.5">{esc(partner)}</p>
        </div>
        <a href="{esc(partner_url)}" target="_blank" rel="noopener noreferrer sponsored"
          class="inline-flex items-center justify-center px-4 py-2.5 rounded-xl bg-emerald-800 text-white text-sm font-semibold hover:bg-emerald-900 transition shrink-0">
          Check Official Offer &nearr;
        </a>
      </div>"""

    body_html = "\n".join(f"<p>{esc(p)}</p>" for p in body)
    sources_html = ""
    if sources:
        items = "".join(
            f'<li><a href="{esc(s["url"])}" target="_blank" rel="noopener noreferrer" class="text-emerald-800 underline hover:text-emerald-950">{esc(s["label"])}</a></li>'
            for s in sources if s.get("url")
        )
        sources_html = f"""
      <section class="mt-8 pt-6 border-t border-stone-200">
        <h2 class="font-serif-editorial text-xl font-bold text-slate-900 mb-3">Verified Sources &amp; Partner Links</h2>
        <ul class="space-y-2 text-sm list-disc pl-5 text-slate-700">{items}</ul>
      </section>"""

    related_cards = "".join(f"""
        <a href="./{esc(r['id'])}.html" class="block bg-white border border-stone-200 rounded-xl p-4 hover:border-emerald-700 transition">
          <span class="text-xs font-semibold text-emerald-800">{esc(r.get('category', ''))}</span>
          <h3 class="font-serif-editorial text-base font-bold text-slate-900 mt-1 leading-snug">{esc(r['title'])}</h3>
        </a>""" for r in related)

    return f"""<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1.0" />
  <title>{esc(title)} | PracticalUtility</title>
  <meta name="description" content="{esc(summary)}" />
  <meta name="keywords" content="{esc(kw)}" />
  <link rel="canonical" href="{esc(canonical)}" />
  <link rel="icon" type="image/svg+xml" href="../images/logo.svg" />
  <link rel="icon" type="image/png" href="../images/logo.png" />
  <meta property="og:title" content="{esc(title)}" />
  <meta property="og:description" content="{esc(summary)}" />
  <meta property="og:type" content="article" />
  <meta property="og:url" content="{esc(canonical)}" />
  <meta property="og:image" content="{BASE_URL}/{esc(img)}" />
  <script type="application/ld+json">{ld_json}</script>
  <script src="https://cdn.tailwindcss.com/3.4.17"></script>
  <link rel="preconnect" href="https://fonts.googleapis.com" />
  <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin />
  <link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&family=Newsreader:opsz,wght@6..72,500;6..72,600;6..72,700&display=swap" rel="stylesheet" />
  <style>
    body {{ font-family: 'Inter', system-ui, -apple-system, sans-serif; }}
    .font-serif-editorial {{ font-family: 'Newsreader', Georgia, serif; }}
  </style>
</head>
<body class="bg-stone-50 text-slate-900 min-h-screen flex flex-col">
  <header class="sticky top-0 z-30 bg-white/95 backdrop-blur border-b border-stone-200">
    <div class="max-w-4xl mx-auto px-4 sm:px-6 h-16 flex items-center justify-between gap-4">
      <a href="../index.html" class="flex items-center gap-2.5">
        <img src="../images/logo.svg" alt="PracticalUtility Logo" class="w-9 h-9 rounded-xl shrink-0 shadow-sm" />
        <span class="font-serif-editorial font-bold text-lg text-slate-900">PracticalUtility</span>
      </a>
      <nav class="flex items-center gap-4 text-sm font-medium">
        <a href="../index.html" class="text-slate-600 hover:text-emerald-800">All Guides</a>
        <a href="../about.html" class="text-slate-600 hover:text-emerald-800">About</a>
      </nav>
    </div>
  </header>

  <main class="flex-1 max-w-4xl w-full mx-auto px-4 sm:px-6 py-8">
    <nav aria-label="Breadcrumb" class="text-sm text-slate-600 mb-4 flex items-center gap-1.5 flex-wrap">
      <a href="../index.html" class="hover:text-emerald-800 underline">Home</a>
      <span>/</span>
      <span>{esc(cat)}</span>
    </nav>

    <article class="bg-white border border-stone-200 rounded-2xl p-6 sm:p-10 shadow-sm">
      <div class="flex flex-wrap items-center gap-2 text-sm text-slate-600 mb-3">
        <span class="px-2.5 py-0.5 rounded-full font-semibold bg-emerald-50 text-emerald-800 border border-emerald-200">{esc(cat)}</span>
        <span>&bull;</span>
        <span>{esc(read_time)}</span>
        <span>&bull;</span>
        <span>Updated {esc(updated)}</span>
      </div>

      <h1 class="font-serif-editorial text-3xl sm:text-4xl font-bold text-slate-900 leading-tight">{esc(title)}</h1>
      <p class="mt-3 text-base sm:text-lg text-slate-600 leading-relaxed">{esc(summary)}</p>

      <div class="w-full overflow-hidden rounded-xl mt-5 bg-stone-100"><img src="../{esc(img)}" alt="{esc(title)}" loading="lazy" onerror="this.parentElement.style.display='none'" class="block w-full h-56 sm:h-72 object-cover" /></div>
      {verdict_html}

      <div class="mt-6 space-y-5 text-slate-700 leading-relaxed text-base">
        {body_html}
      </div>

      {sources_html}

      <aside class="mt-8 pt-6 border-t border-stone-200 flex flex-col sm:flex-row sm:items-center justify-between gap-4 text-sm text-slate-600">
        <div>
          <p class="font-semibold text-slate-900">Reviewed by Puneet Sharma</p>
          <p class="mt-0.5">Operations &amp; Order-to-Cash specialist with 15+ years analyzing business workflows and practical home systems. <a href="../about.html" class="text-emerald-800 underline">Editorial policy</a>.</p>
        </div>
      </aside>
    </article>

    <section class="mt-10">
      <h2 class="font-serif-editorial text-2xl font-bold text-slate-900 mb-4">Related Guides</h2>
      <div class="grid grid-cols-1 sm:grid-cols-3 gap-4">
        {related_cards}
      </div>
    </section>
  </main>

  <footer class="border-t border-stone-200 bg-white py-5 mt-12">
    <div class="max-w-4xl mx-auto px-4 sm:px-6 flex flex-col sm:flex-row items-center justify-between gap-2 text-sm text-slate-600">
      <p>&copy; 2026 PracticalUtility &bull; <a href="../about.html" class="underline">About &amp; Affiliate Disclosure</a></p>
      <p>We may earn a commission from partner links at no extra cost to you.</p>
    </div>
  </footer>
</body>
</html>
"""


def render_about_page():
    return f"""<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1.0" />
  <title>About &amp; Editorial Disclosure | PracticalUtility</title>
  <meta name="description" content="About PracticalUtility, our research methodology for home systems and small-business software, and our FTC affiliate disclosure." />
  <link rel="canonical" href="{BASE_URL}/about.html" />
  <link rel="icon" type="image/svg+xml" href="./images/logo.svg" />
  <link rel="icon" type="image/png" href="./images/logo.png" />
  <script src="https://cdn.tailwindcss.com/3.4.17"></script>
  <link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&family=Newsreader:opsz,wght@6..72,600;6..72,700&display=swap" rel="stylesheet" />
  <style>
    body {{ font-family: 'Inter', system-ui, sans-serif; }}
    .font-serif-editorial {{ font-family: 'Newsreader', Georgia, serif; }}
  </style>
</head>
<body class="bg-stone-50 text-slate-900 min-h-screen flex flex-col">
  <header class="bg-white border-b border-stone-200">
    <div class="max-w-3xl mx-auto px-4 sm:px-6 h-16 flex items-center justify-between">
      <a href="./index.html" class="flex items-center gap-2.5">
        <img src="./images/logo.svg" alt="PracticalUtility Logo" class="w-9 h-9 rounded-xl shrink-0 shadow-sm" />
        <span class="font-serif-editorial font-bold text-lg text-slate-900">PracticalUtility</span>
      </a>
      <a href="./index.html" class="text-sm font-medium text-emerald-800 hover:underline">&larr; Back to Guides</a>
    </div>
  </header>
  <main class="flex-1 max-w-3xl w-full mx-auto px-4 sm:px-6 py-10">
    <article class="bg-white border border-stone-200 rounded-2xl p-6 sm:p-10 shadow-sm space-y-5">
      <h1 class="font-serif-editorial text-3xl font-bold text-slate-900">About PracticalUtility</h1>
      <p class="text-slate-700 leading-relaxed">
        PracticalUtility publishes concise, specification-driven buying and maintenance guides for essential home systems (HVAC air filtration, mini-splits, dehumidifiers, and drinking water purification) alongside small-business operations software (field-service dispatch and automated invoicing).
      </p>
      <h2 class="font-serif-editorial text-xl font-bold text-slate-900 pt-2">Publisher &amp; Editorial Standards</h2>
      <p class="text-slate-700 leading-relaxed">
        Founded by <strong>Puneet Sharma</strong>, an operations and Order-to-Cash leader with over 15 years of corporate process experience, every guide on PracticalUtility cites official manufacturer specifications, independent certification standards (such as IAPMO/NSF/ANSI 53), or verified regulatory notices.
      </p>
      <h2 class="font-serif-editorial text-xl font-bold text-slate-900 pt-2">FTC Affiliate Disclosure</h2>
      <p class="text-slate-700 leading-relaxed">
        PracticalUtility is reader-supported. When you sign up or buy through partner links on our site (including QuoteIQ, Zoho, Waterdrop, or Filterbuy), we may earn an affiliate commission at no extra cost to you. Commissions never dictate our sizing formulas, certification checks, or technical trade-offs.
      </p>
    </article>
  </main>
</body>
</html>
"""


def render_index_page(articles, news):
    # Pre-render static crawlable cards inside #articlesGrid so Googlebot & AI crawlers see all links in raw HTML!
    initial_cards = "\n".join(f"""
        <article class="animate-card bg-white border border-stone-200 rounded-2xl overflow-hidden shadow-sm hover:shadow-md hover:-translate-y-0.5 transition duration-200 flex flex-col">
          <a href="./guides/{esc(a['id'])}.html" class="block">
            <img src="./{esc(default_image_for(a))}" alt="{esc(a['title'])}" loading="lazy" onerror="this.style.display='none'" class="w-full h-40 object-cover bg-stone-100" />
          </a>
          <div class="p-5 sm:p-6 flex-1 flex flex-col justify-between gap-4">
            <div>
              <div class="flex items-center justify-between gap-2 text-sm text-slate-600 mb-2">
                <span class="font-semibold text-emerald-800">{esc(a.get('category', ''))}</span>
                <span>{esc(a.get('readTime', '6 min read'))}</span>
              </div>
              <h3 class="font-serif-editorial text-xl font-bold text-slate-900 leading-snug">
                <a href="./guides/{esc(a['id'])}.html" class="hover:text-emerald-800 transition">{esc(a['title'])}</a>
              </h3>
              <p class="mt-2.5 text-base text-slate-700 leading-relaxed line-clamp-3">{esc(a.get('summary', ''))}</p>
            </div>
            <div class="pt-3 border-t border-stone-100 flex items-center justify-between gap-2">
              <span class="text-sm text-slate-500">Updated {esc(a.get('updated', '2026'))}</span>
              <a href="./guides/{esc(a['id'])}.html" class="text-sm font-semibold text-emerald-800 hover:text-emerald-950 shrink-0">Read Guide &rarr;</a>
            </div>
          </div>
        </article>""" for a in articles)

    articles_json_safe = json.dumps(articles, ensure_ascii=False).replace("</", "<\\/")
    news_json_safe = json.dumps(news, ensure_ascii=False).replace("</", "<\\/")

    return f"""<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1.0" />
  <title>PracticalUtility — Home Systems, Filtration &amp; Small-Business Software Guides</title>
  <meta name="description" content="PracticalUtility publishes search-focused buying and maintenance guides for HVAC air filters, water purification, field-service trades software, and small-business invoicing." />
  <link rel="canonical" href="{BASE_URL}/" />
  <link rel="icon" type="image/svg+xml" href="./images/logo.svg" />
  <link rel="icon" type="image/png" href="./images/logo.png" />
  <meta property="og:title" content="PracticalUtility — Essential Systems &amp; B2B Guides" />
  <meta property="og:description" content="In-depth, high-intent guides covering HVAC filtration, water purification, trades software, and small-business invoicing." />
  <meta property="og:type" content="website" />
  <meta property="og:url" content="{BASE_URL}/" />
  <script src="https://cdn.tailwindcss.com/3.4.17"></script>
  <link rel="preconnect" href="https://fonts.googleapis.com" />
  <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin />
  <link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&family=Newsreader:opsz,wght@6..72,500;6..72,600;6..72,700&display=swap" rel="stylesheet" />
  <style>
    body {{ font-family: 'Inter', system-ui, -apple-system, sans-serif; }}
    .font-serif-editorial {{ font-family: 'Newsreader', Georgia, serif; }}
    .line-clamp-3 {{ display: -webkit-box; -webkit-line-clamp: 3; -webkit-box-orient: vertical; overflow: hidden; }}
    @keyframes fadeSlideUp {{ from {{ opacity: 0; transform: translateY(8px); }} to {{ opacity: 1; transform: translateY(0); }} }}
    .animate-card {{ animation: fadeSlideUp 0.28s ease-out both; }}
    .drawer-panel {{ max-height: 0; opacity: 0; overflow: hidden; transition: max-height 0.3s ease, opacity 0.22s ease; }}
    .drawer-panel.is-open {{ max-height: 420px; opacity: 1; }}
  </style>
</head>
<body class="bg-stone-50 text-slate-900 min-h-screen flex flex-col">
  <header class="sticky top-0 z-30 bg-white/95 backdrop-blur border-b border-stone-200">
    <div class="max-w-6xl mx-auto px-4 sm:px-6 h-16 flex items-center justify-between gap-4">
      <div class="flex items-center gap-3 min-w-0">
        <img src="./images/logo.svg" alt="PracticalUtility Logo" class="w-10 h-10 rounded-xl shrink-0 shadow-sm" />
        <div class="min-w-0">
          <a href="./index.html" id="brandHomeBtn" class="font-serif-editorial font-bold text-xl tracking-tight text-slate-900 hover:text-emerald-800 transition truncate block">PracticalUtility</a>
          <p class="text-xs text-slate-600 hidden sm:block">Everyday Operations, Home Systems &amp; B2B Guides</p>
        </div>
      </div>

      <nav class="flex items-center gap-2 sm:gap-3" aria-label="Primary">
        <a href="./about.html" class="hidden sm:inline-flex px-3 py-1.5 rounded-lg text-sm font-medium text-slate-700 hover:text-emerald-800 hover:bg-stone-100 transition">About</a>
        <button type="button" id="menuToggleBtn" aria-expanded="false" aria-controls="categoryDrawer"
          class="inline-flex items-center gap-2 px-3.5 py-2 rounded-xl border border-stone-300 bg-white hover:bg-stone-100 text-sm font-semibold text-slate-800 transition">
          <svg class="w-4 h-4" fill="none" stroke="currentColor" stroke-width="2" viewBox="0 0 24 24" aria-hidden="true">
            <path stroke-linecap="round" stroke-linejoin="round" d="M4 6h16M4 12h16M4 18h16" />
          </svg>
          <span>Categories</span>
        </button>
      </nav>
    </div>

    <div id="categoryDrawer" class="drawer-panel border-t border-stone-200 bg-stone-50/95">
      <div class="max-w-6xl mx-auto px-4 sm:px-6 py-4">
        <div class="flex items-center justify-between mb-3">
          <p class="text-xs font-semibold uppercase tracking-wider text-slate-500">Browse by Category</p>
          <button type="button" id="closeDrawerBtn" class="text-xs font-medium text-slate-600 hover:text-slate-900">Close</button>
        </div>
        <div id="drawerCategories" class="grid grid-cols-1 sm:grid-cols-2 md:grid-cols-5 gap-2"></div>
      </div>
    </div>
  </header>

  <main class="flex-1 max-w-6xl w-full mx-auto px-4 sm:px-6 py-6 sm:py-8 space-y-6">
    <!-- Hero & Unified Search -->
    <div class="bg-white border border-stone-200 rounded-2xl p-5 sm:p-7 shadow-sm">
      <div class="flex flex-col lg:flex-row lg:items-end justify-between gap-5">
        <div class="max-w-2xl">
          <span class="inline-flex items-center gap-1.5 px-2.5 py-0.5 rounded-full text-xs font-semibold bg-emerald-50 text-emerald-800 border border-emerald-200 mb-3">
            Independent Buyer &amp; Maintenance Guides
          </span>
          <h1 class="font-serif-editorial text-2xl sm:text-3xl font-bold text-slate-900 leading-tight">
            Practical Buying &amp; Maintenance Guides for Essential Systems
          </h1>
          <p class="mt-2 text-sm sm:text-base text-slate-600">
            Specification-backed guides covering HVAC air filtration, water purification, field-service trades software, and small-business invoicing.
          </p>
        </div>
        <div class="w-full lg:w-80 shrink-0">
          <label for="articleSearch" class="sr-only">Search guides and news</label>
          <input id="articleSearch" type="search" placeholder="Search guides &amp; world news..."
            class="w-full px-3.5 py-2.5 rounded-xl border border-stone-300 bg-stone-50 text-sm focus:outline-none focus:ring-2 focus:ring-emerald-700 focus:bg-white" />
        </div>
      </div>

      <div id="categoryFilters" class="mt-5 pt-4 border-t border-stone-100 flex flex-wrap gap-2">
        <button type="button" data-cat="All" class="cat-pill px-3.5 py-1.5 rounded-full text-sm font-semibold bg-slate-900 text-white">All</button>
        <button type="button" data-cat="Home Utility" class="cat-pill px-3.5 py-1.5 rounded-full text-sm font-semibold bg-stone-100 text-slate-700 hover:bg-stone-200">Home Utility</button>
        <button type="button" data-cat="Water & Air" class="cat-pill px-3.5 py-1.5 rounded-full text-sm font-semibold bg-stone-100 text-slate-700 hover:bg-stone-200">Water &amp; Air</button>
        <button type="button" data-cat="Trades & B2B SaaS" class="cat-pill px-3.5 py-1.5 rounded-full text-sm font-semibold bg-stone-100 text-slate-700 hover:bg-stone-200">Trades &amp; B2B SaaS</button>
        <button type="button" data-cat="Finance & Ops" class="cat-pill px-3.5 py-1.5 rounded-full text-sm font-semibold bg-stone-100 text-slate-700 hover:bg-stone-200">Finance &amp; Ops</button>
      </div>
    </div>

    <!-- Full-Width Guides | World News Toggle -->
    <div class="flex items-center gap-2 bg-white p-1.5 rounded-xl border border-stone-200 shadow-sm lg:max-w-md">
      <button type="button" id="tabGuidesBtn" class="flex-1 py-2.5 px-3 rounded-lg text-sm font-semibold bg-emerald-800 text-white transition">
        Guides (<span id="guidesTabCount">{len(articles)}</span>)
      </button>
      <button type="button" id="tabNewsBtn" class="flex-1 py-2.5 px-3 rounded-lg text-sm font-semibold text-slate-600 hover:bg-stone-100 transition">
        World News (<span id="newsTabCount">{len(news)}</span>)
      </button>
    </div>

    <!-- SECTION 1: PRACTICAL GUIDES (Pre-rendered for crawlers) -->
    <section id="guides-section" class="space-y-4">
      <div class="flex items-baseline justify-between gap-2">
        <h2 class="font-serif-editorial text-2xl font-bold text-slate-900">Practical Guides</h2>
        <span id="guidesCountLabel" class="text-sm text-slate-600">{len(articles)} guides</span>
      </div>
      <div id="articlesGrid" class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
        {initial_cards}
      </div>
      <div id="emptyArticles" class="hidden bg-white border border-stone-200 rounded-2xl p-10 text-center">
        <p class="text-slate-600 text-sm">No guides match your current search or category.</p>
      </div>
    </section>

    <!-- SECTION 2: WORLD & INDUSTRY NEWS -->
    <section id="news-section" class="hidden space-y-4">
      <div class="flex items-baseline justify-between gap-2">
        <h2 class="font-serif-editorial text-2xl font-bold text-slate-900">World &amp; Industry News</h2>
        <span id="newsCountLabel" class="text-sm text-slate-600">{len(news)} stories</span>
      </div>
      <div id="newsGrid" class="grid grid-cols-1 md:grid-cols-2 gap-5"></div>
      <div id="emptyNews" class="hidden bg-white border border-stone-200 rounded-2xl p-8 text-center">
        <p class="text-slate-600 text-sm">No news stories match your current search.</p>
      </div>
    </section>
  </main>

  <!-- News Detail Modal -->
  <div id="newsModal" class="fixed inset-0 z-40 hidden bg-slate-900/60 backdrop-blur-sm flex items-center justify-center p-4">
    <div class="bg-white rounded-2xl max-w-2xl w-full max-h-[90vh] overflow-y-auto shadow-2xl border border-stone-200">
      <div class="sticky top-0 bg-white/95 backdrop-blur border-b border-stone-200 px-6 py-4 flex items-center justify-between gap-4">
        <span id="modalCategory" class="text-xs font-semibold uppercase tracking-wider text-emerald-800"></span>
        <button type="button" id="closeModalBtn" class="px-3 py-1 rounded-lg text-sm font-medium text-slate-600 hover:bg-stone-100">Close</button>
      </div>
      <div id="modalContent" class="p-6 sm:p-8 space-y-5"></div>
    </div>
  </div>

  <footer class="border-t border-stone-200 bg-white py-5 mt-10">
    <div class="max-w-6xl mx-auto px-4 sm:px-6 flex flex-col sm:flex-row items-center justify-between gap-2 text-sm text-slate-600">
      <p>&copy; 2026 PracticalUtility &bull; <a href="./about.html" class="underline hover:text-emerald-800">About &amp; Editorial Policy</a></p>
      <p>Affiliate Disclosure: Guides may include verified partner links that earn commissions at no extra cost to readers.</p>
    </div>
  </footer>

  <script>
    const CATEGORY_LIST = ['All', 'Home Utility', 'Water & Air', 'Trades & B2B SaaS', 'Finance & Ops'];
    let articles = {articles_json_safe};
    let worldNews = {news_json_safe};
    let activeCategory = 'All';
    let searchQuery = '';

    function setActiveTab(view) {{
      const gSec = document.getElementById('guides-section');
      const nSec = document.getElementById('news-section');
      const gBtn = document.getElementById('tabGuidesBtn');
      const nBtn = document.getElementById('tabNewsBtn');
      if (view === 'guides') {{
        gSec.classList.remove('hidden');
        nSec.classList.add('hidden');
        gBtn.className = 'flex-1 py-2.5 px-3 rounded-lg text-sm font-semibold bg-emerald-800 text-white transition';
        nBtn.className = 'flex-1 py-2.5 px-3 rounded-lg text-sm font-semibold text-slate-600 hover:bg-stone-100 transition';
      }} else {{
        gSec.classList.add('hidden');
        nSec.classList.remove('hidden');
        nBtn.className = 'flex-1 py-2.5 px-3 rounded-lg text-sm font-semibold bg-emerald-800 text-white transition';
        gBtn.className = 'flex-1 py-2.5 px-3 rounded-lg text-sm font-semibold text-slate-600 hover:bg-stone-100 transition';
      }}
    }}

    function articleImage(a) {{
      if (a.image && a.image.startsWith('images/')) return a.image;
      const s = `${{a.id || ''}} ${{a.category || ''}}`.toLowerCase();
      if (s.includes('water') || s.includes('pfas') || s.includes('softener')) return 'images/water-filter.jpg';
      if (s.includes('trade') || s.includes('saas') || s.includes('finance') || s.includes('invoic')) return 'images/trades-finance.jpg';
      return 'images/hvac-air.jpg';
    }}

    function renderArticles() {{
      const grid = document.getElementById('articlesGrid');
      const empty = document.getElementById('emptyArticles');
      const q = searchQuery.trim().toLowerCase();
      const filtered = articles.filter(a => {{
        const catMatch = activeCategory === 'All' || a.category === activeCategory;
        const textMatch = !q || [a.title, a.keyword, a.summary, a.partner, a.category].join(' ').toLowerCase().includes(q);
        return catMatch && textMatch;
      }});
      document.getElementById('guidesCountLabel').textContent = `${{filtered.length}} guide${{filtered.length === 1 ? '' : 's'}}`;
      document.getElementById('guidesTabCount').textContent = String(filtered.length);
      if (filtered.length === 0) {{
        grid.innerHTML = '';
        empty.classList.remove('hidden');
        return;
      }}
      empty.classList.add('hidden');
      grid.innerHTML = filtered.map(a => `
        <article class="animate-card bg-white border border-stone-200 rounded-2xl overflow-hidden shadow-sm hover:shadow-md hover:-translate-y-0.5 transition duration-200 flex flex-col">
          <a href="./guides/${{a.id}}.html" class="block">
            <img src="./${{articleImage(a)}}" alt="${{a.title}}" loading="lazy" onerror="this.style.display='none'" class="w-full h-40 object-cover bg-stone-100" />
          </a>
          <div class="p-5 sm:p-6 flex-1 flex flex-col justify-between gap-4">
            <div>
              <div class="flex items-center justify-between gap-2 text-sm text-slate-600 mb-2">
                <span class="font-semibold text-emerald-800">${{a.category}}</span>
                <span>${{a.readTime || '6 min read'}}</span>
              </div>
              <h3 class="font-serif-editorial text-xl font-bold text-slate-900 leading-snug">
                <a href="./guides/${{a.id}}.html" class="hover:text-emerald-800 transition">${{a.title}}</a>
              </h3>
              <p class="mt-2.5 text-base text-slate-700 leading-relaxed line-clamp-3">${{a.summary}}</p>
            </div>
            <div class="pt-3 border-t border-stone-100 flex items-center justify-between gap-2">
              <span class="text-sm text-slate-500">Updated ${{a.updated || '2026'}}</span>
              <a href="./guides/${{a.id}}.html" class="text-sm font-semibold text-emerald-800 hover:text-emerald-950 shrink-0">Read Guide &rarr;</a>
            </div>
          </div>
        </article>`).join('');
    }}

    function renderNewsCards() {{
      const grid = document.getElementById('newsGrid');
      const empty = document.getElementById('emptyNews');
      const q = searchQuery.trim().toLowerCase();
      const filtered = worldNews.filter(n => {{
        const catMatch = activeCategory === 'All' || n.category === activeCategory;
        const textMatch = !q || [n.title, n.summary, n.source, n.category].join(' ').toLowerCase().includes(q);
        return catMatch && textMatch;
      }});
      document.getElementById('newsCountLabel').textContent = `${{filtered.length}} stor${{filtered.length === 1 ? 'y' : 'ies'}}`;
      document.getElementById('newsTabCount').textContent = String(filtered.length);
      if (filtered.length === 0) {{
        grid.innerHTML = '';
        empty.classList.remove('hidden');
        return;
      }}
      empty.classList.add('hidden');
      grid.innerHTML = filtered.map(n => `
        <article class="animate-card bg-white border border-stone-200 rounded-2xl p-5 shadow-sm hover:shadow-md transition flex flex-col justify-between gap-3">
          <div class="space-y-2">
            <div class="flex flex-wrap items-center justify-between gap-1.5 text-xs sm:text-sm">
              <span class="px-2 py-0.5 rounded-full font-semibold bg-emerald-50 text-emerald-800 border border-emerald-200">${{n.category}}</span>
              <span class="text-slate-500 font-medium">${{n.source}} &bull; ${{n.date || '2026'}}</span>
            </div>
            <h3 class="font-serif-editorial text-lg font-bold text-slate-900 leading-snug">${{n.title}}</h3>
            <p class="text-sm sm:text-base text-slate-700 leading-relaxed">${{n.summary}}</p>
          </div>
          <div class="pt-2.5 border-t border-stone-100 flex items-center justify-between gap-2">
            ${{n.relatedGuideId ? `<a href="./guides/${{n.relatedGuideId}}.html" class="text-sm font-semibold text-slate-700 hover:text-emerald-800 transition">See Guide &rarr;</a>` : '<span></span>'}}
            <button type="button" data-news-idx="${{worldNews.indexOf(n)}}" class="read-news-btn text-sm font-semibold text-emerald-800 hover:text-emerald-950 shrink-0">Read &rarr;</button>
          </div>
        </article>`).join('');
    }}

    function renderDrawerCategories() {{
      const container = document.getElementById('drawerCategories');
      container.innerHTML = CATEGORY_LIST.map(cat => {{
        const count = cat === 'All' ? articles.length : articles.filter(a => a.category === cat).length;
        const active = activeCategory === cat;
        return `<button type="button" data-drawer-cat="${{cat}}" class="drawer-cat-btn flex items-center justify-between px-3.5 py-2.5 rounded-xl text-sm font-medium border transition ${{active ? 'bg-emerald-800 text-white border-emerald-800' : 'bg-white text-slate-800 border-stone-200 hover:border-emerald-700'}}">
          <span>${{cat === 'All' ? 'All Guides' : cat}}</span>
          <span class="text-xs px-2 py-0.5 rounded-full ${{active ? 'bg-emerald-700 text-white' : 'bg-stone-100 text-slate-600'}}">${{count}}</span>
        </button>`;
      }}).join('');
    }}

    function setCategory(cat) {{
      activeCategory = cat;
      document.querySelectorAll('.cat-pill').forEach(p => {{
        const active = p.dataset.cat === activeCategory;
        p.className = active
          ? 'cat-pill px-3.5 py-1.5 rounded-full text-sm font-semibold bg-slate-900 text-white'
          : 'cat-pill px-3.5 py-1.5 rounded-full text-sm font-semibold bg-stone-100 text-slate-700 hover:bg-stone-200';
      }});
      renderArticles();
      renderNewsCards();
      renderDrawerCategories();
    }}

    function toggleDrawer(forceOpen) {{
      const drawer = document.getElementById('categoryDrawer');
      const btn = document.getElementById('menuToggleBtn');
      const isOpen = drawer.classList.contains('is-open');
      const shouldOpen = typeof forceOpen === 'boolean' ? forceOpen : !isOpen;
      drawer.classList.toggle('is-open', shouldOpen);
      btn.setAttribute('aria-expanded', String(shouldOpen));
    }}

    function openNewsModal(idx) {{
      const n = worldNews[idx];
      if (!n) return;
      document.getElementById('modalCategory').textContent = `World News • ${{n.category}} • ${{n.source}}`;
      const paragraphs = Array.isArray(n.detail) && n.detail.length ? n.detail : [n.summary];
      document.getElementById('modalContent').innerHTML = `
        <h2 class="font-serif-editorial text-2xl sm:text-3xl font-bold text-slate-900 leading-tight">${{n.title}}</h2>
        <div class="text-xs font-medium text-slate-500">Verified Source: <span class="text-slate-800 font-semibold">${{n.source}}</span> &bull; ${{n.date || '2026'}}</div>
        <div class="space-y-4 text-slate-800 leading-relaxed text-base">
          <p class="font-medium text-slate-800">${{n.summary}}</p>
          ${{paragraphs.map(p => `<p>${{p}}</p>`).join('')}}
        </div>
        <div class="pt-4 border-t border-stone-200 flex flex-wrap gap-3">
          <a href="${{n.url}}" target="_blank" rel="noopener noreferrer" class="inline-flex items-center gap-1.5 px-4 py-2 rounded-xl bg-emerald-800 text-white text-sm font-semibold hover:bg-emerald-900 transition">Read Full Report at ${{n.source}} &nearr;</a>
          ${{n.relatedGuideId ? `<a href="./guides/${{n.relatedGuideId}}.html" class="px-4 py-2 rounded-xl border border-stone-300 text-slate-800 text-sm font-semibold hover:bg-stone-100 transition">Open Related Guide &rarr;</a>` : ''}}
        </div>`;
      document.getElementById('newsModal').classList.remove('hidden');
    }}

    document.getElementById('tabGuidesBtn').addEventListener('click', () => setActiveTab('guides'));
    document.getElementById('tabNewsBtn').addEventListener('click', () => setActiveTab('news'));
    document.getElementById('menuToggleBtn').addEventListener('click', () => toggleDrawer());
    document.getElementById('closeDrawerBtn').addEventListener('click', () => toggleDrawer(false));
    document.getElementById('categoryFilters').addEventListener('click', e => {{
      const btn = e.target.closest('.cat-pill');
      if (btn) setCategory(btn.dataset.cat);
    }});
    document.getElementById('drawerCategories').addEventListener('click', e => {{
      const btn = e.target.closest('.drawer-cat-btn');
      if (!btn) return;
      setCategory(btn.dataset.drawerCat);
      toggleDrawer(false);
    }});
    document.getElementById('articleSearch').addEventListener('input', e => {{
      searchQuery = e.target.value;
      renderArticles();
      renderNewsCards();
    }});
    document.getElementById('newsGrid').addEventListener('click', e => {{
      const btn = e.target.closest('.read-news-btn');
      if (btn) openNewsModal(Number(btn.dataset.newsIdx));
    }});
    document.getElementById('closeModalBtn').addEventListener('click', () => document.getElementById('newsModal').classList.add('hidden'));
    document.getElementById('newsModal').addEventListener('click', e => {{
      if (e.target.id === 'newsModal') document.getElementById('newsModal').classList.add('hidden');
    }});

    renderDrawerCategories();
    renderNewsCards();

    // Dynamically refresh articles & news from live JSON files when hosted over HTTP/HTTPS
    (async function syncLiveContent() {{
      if (window.location.protocol === 'file:') return;
      try {{
        const ts = Date.now();
        const [aRes, nRes] = await Promise.all([
          fetch(`./articles.json?v=${{ts}}`, {{ cache: 'no-cache' }}),
          fetch(`./news.json?v=${{ts}}`, {{ cache: 'no-cache' }})
        ]);
        let changed = false;
        if (aRes.ok) {{
          const liveArticles = await aRes.json();
          if (Array.isArray(liveArticles) && liveArticles.length > 0) {{
            articles = liveArticles;
            changed = true;
          }}
        }}
        if (nRes.ok) {{
          const liveNews = await nRes.json();
          if (Array.isArray(liveNews) && liveNews.length > 0) {{
            worldNews = liveNews;
            changed = true;
          }}
        }}
        if (changed) {{
          renderDrawerCategories();
          renderArticles();
          renderNewsCards();
        }}
      }} catch (_) {{
        // Keep pre-rendered static content as fallback
      }}
    }})();
  </script>
</body>
</html>
"""


def build():
    articles = json.loads((ROOT / "articles.json").read_text(encoding="utf-8"))
    news = json.loads((ROOT / "news.json").read_text(encoding="utf-8"))

    for a in articles:
        (GUIDES_DIR / f"{a['id']}.html").write_text(render_guide_page(a, articles), encoding="utf-8")

    (ROOT / "about.html").write_text(render_about_page(), encoding="utf-8")
    (ROOT / "index.html").write_text(render_index_page(articles, news), encoding="utf-8")

    today = datetime.date.today().isoformat()
    urls = [f"{BASE_URL}/", f"{BASE_URL}/about.html"] + [f"{BASE_URL}/guides/{a['id']}.html" for a in articles]
    sitemap = '<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n'
    for u in urls:
        sitemap += f"  <url><loc>{esc(u)}</loc><lastmod>{today}</lastmod></url>\n"
    sitemap += "</urlset>\n"
    (ROOT / "sitemap.xml").write_text(sitemap, encoding="utf-8")

    (ROOT / "robots.txt").write_text(f"User-agent: *\nAllow: /\nSitemap: {BASE_URL}/sitemap.xml\n", encoding="utf-8")
    print(f"Built {len(articles)} static guide pages, index.html, about.html, sitemap.xml, and robots.txt.")


if __name__ == "__main__":
    build()
