# -*- coding: utf-8 -*-
"""
Rebuild strahovkatut21.ru:
- Resolves all 404 errors by creating folder/index.html & .html files for all routes
- Rewrites legacy Nethouse /page/... links to modern clean URLs (/osago/, /kasko/, /ipoteka/, /contacts/, etc.)
- Retains /page/... legacy paths so external/old links never 404
- Wraps all 13 articles in native responsive design matching the main site
- Generates /articles/ catalog
- Injects useful articles block on the homepage
- Updates sitemap.xml
"""

import os
import re
import json
import shutil
from bs4 import BeautifulSoup

REPO_DIR = r"C:\Users\user\Desktop\Projects\repos\strahovkatut21.ru"
SERVICES_DIR = os.path.join(REPO_DIR, "pages", "services")
ARTICLES_DIR = os.path.join(REPO_DIR, "pages", "articles")

SERVICE_ROUTES = {
    "osago": {"file": "osago.html", "legacy": ["1294862"], "title": "Страхование ОСАГО в Чебоксарах – Расчет и оформление"},
    "kasko": {"file": "kasko.html", "legacy": ["1294911"], "title": "Страхование КАСКО в Чебоксарах – Подбор тарифа"},
    "ipoteka": {"file": "ipoteka.html", "legacy": ["1294915"], "title": "Страхование ипотеки – Все аккредитованные банки"},
    "imushchestvo": {"file": "imushchestvo.html", "legacy": ["1294923", "1294974"], "title": "Страхование имущества, дома и квартиры"},
    "inye-vidy": {"file": "inye_strahovanie.html", "legacy": ["1335615"], "title": "Иные виды страхования и защита здоровья"},
    "zelenaya-karta": {"file": "zelenaya_karta.html", "legacy": ["1294924"], "title": "Зеленая карта – Международное автострахование"},
    "kbm": {"file": "kbm_discount.html", "legacy": ["1294916"], "title": "Исправление скидки по ОСАГО – Восстановление КБМ"},
    "kredity": {"file": "kredity_karty.html", "legacy": ["1333771"], "title": "Кредиты и кредитные карты – Выгодные ставки"},
    "vtoroe-med-mnenie": {"file": "vtoroe_med_mnenie.html", "legacy": ["1294984"], "title": "Второе медицинское мнение – Страхование здоровья"},
    "contacts": {"file": "contacts.html", "legacy": [], "title": "Контактная информация – Страхование в Чебоксарах"}
}

NAV_ITEMS = [
    ("/", "О компании"),
    ("/osago/", "ОСАГО"),
    ("/kasko/", "Страхование КАСКО"),
    ("/ipoteka/", "Страхование ипотеки"),
    ("/imushchestvo/", "Страхование имущества"),
    ("/inye-vidy/", "Иные виды страхования"),
    ("/zelenaya-karta/", "Зеленая карта"),
    ("/kbm/", "Исправление скидки по ОСАГО"),
    ("/contacts/", "Контактная информация"),
    ("/kredity/", "Кредиты и карты"),
    ("/articles/", "Полезные статьи")
]

def make_nav_html(active_path=""):
    items = []
    for idx, (path, label) in enumerate(NAV_ITEMS):
        cls = ' class="active"' if path == active_path or (path != "/" and active_path.startswith(path)) else ''
        items.append(f'<li{cls} id="lnk-{idx+1}"><a href="{path}">{label}</a></li>')
    return '<nav id="main-menu"><div class="site-menu"><div class="overlay"></div><ul>' + "".join(items) + '</ul></div></nav>'

URL_REPLACEMENTS = {
    r'https?://strahovkatut21\.ru/contacts#contactssocnet': '/contacts/#contactssocnet',
    r'https?://strahovkatut21\.ru/contacts': '/contacts/',
    r'https?://strahovkatut21\.ru/page/1294862': '/osago/',
    r'https?://strahovkatut21\.ru/': '/',
    r'/page/1294862': '/osago/',
    r'/page/1294911': '/kasko/',
    r'/page/1294915': '/ipoteka/',
    r'/page/1294923': '/imushchestvo/',
    r'/page/1294974': '/inye-vidy/',
    r'/page/1294924': '/zelenaya-karta/',
    r'/page/1294916': '/kbm/',
    r'/page/1333771': '/kredity/',
    r'/page/1335615/?': '/inye-vidy/',
    r'/page/1294984': '/vtoroe-med-mnenie/',
    r'/contacts/?(?=[\"\'\s#])': '/contacts/',
    r'https?://strahovkavsem\.nethouse\.ru/page/1294862': '/osago/',
    r'https?://strahovkavsem\.nethouse\.ru/?': '/'
}

def clean_links(html, active_path=""):
    for pattern, repl in URL_REPLACEMENTS.items():
        html = re.sub(r'href=[\"\']' + pattern + r'[\"\']', f'href="{repl}"', html)
    # Also replace in nav
    soup = BeautifulSoup(html, 'html.parser')
    old_nav = soup.find('nav', id='main-menu') or soup.find('nav')
    if old_nav:
        new_nav_soup = BeautifulSoup(make_nav_html(active_path), 'html.parser')
        old_nav.replace_with(new_nav_soup)
        html = str(soup)
    return html

def save_html_pair(dir_path, filename, html_content):
    os.makedirs(dir_path, exist_ok=True)
    index_file = os.path.join(dir_path, "index.html")
    with open(index_file, "w", encoding="utf-8") as f:
        f.write(html_content)
    # Also save flat html file next to or in root
    flat_file = os.path.join(REPO_DIR, f"{filename}.html")
    with open(flat_file, "w", encoding="utf-8") as f:
        f.write(html_content)

def main():
    print(">>> 1. Processing Homepage (index.html)...")
    with open(os.path.join(REPO_DIR, "index.html"), "r", encoding="utf-8") as f:
        index_html = f.read()

    index_html = clean_links(index_html, active_path="/")

    # Save cleaned index.html
    # Inject articles showcase block before footer
    soup = BeautifulSoup(index_html, 'html.parser')
    footer = soup.find('footer')
    if footer and not soup.find(id='articles-showcase'):
        section_html = '''
<section id="articles-showcase" class="widget-block on-view" style="background: #f8fafc; padding: 45px 20px; border-top: 1px solid #e2e8f0; font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Helvetica, Arial, sans-serif;">
    <div style="max-width: 1140px; margin: 0 auto;">
        <h2 style="text-align: center; font-size: 28px; color: #1a202c; margin-bottom: 10px;">Полезные статьи и автострахование</h2>
        <p style="text-align: center; color: #718096; font-size: 15px; margin-bottom: 30px;">Инструкции, правила оформления и экспертные советы для автовладельцев</p>
        <div style="display: grid; grid-template-columns: repeat(auto-fill, minmax(260px, 1fr)); gap: 20px;">
            <div style="background: #fff; padding: 20px; border-radius: 8px; border: 1px solid #e2e8f0; box-shadow: 0 2px 4px rgba(0,0,0,0.04);">
                <span style="display: inline-block; font-size: 12px; font-weight: 600; color: #3182ce; background: #ebf8ff; padding: 3px 8px; border-radius: 4px; margin-bottom: 10px;">ОСАГО 2026</span>
                <h4 style="font-size: 16px; margin: 0 0 10px 0; line-height: 1.4;"><a href="/articles/kak-oformit-osago-na-avtomobil/" style="color: #2d3748; text-decoration: none;">Как оформить ОСАГО на автомобиль: документы и процедура</a></h4>
                <a href="/articles/kak-oformit-osago-na-avtomobil/" style="color: #3182ce; font-size: 13px; font-weight: 600;">Читать далее &rarr;</a>
            </div>
            <div style="background: #fff; padding: 20px; border-radius: 8px; border: 1px solid #e2e8f0; box-shadow: 0 2px 4px rgba(0,0,0,0.04);">
                <span style="display: inline-block; font-size: 12px; font-weight: 600; color: #38a169; background: #f0fff4; padding: 3px 8px; border-radius: 4px; margin-bottom: 10px;">Страхование</span>
                <h4 style="font-size: 16px; margin: 0 0 10px 0; line-height: 1.4;"><a href="/articles/kak-otkazatsya-ot-strahovaniya-sogaz/" style="color: #2d3748; text-decoration: none;">Как отказаться от страховки по кредиту в СОГАЗ</a></h4>
                <a href="/articles/kak-otkazatsya-ot-strahovaniya-sogaz/" style="color: #3182ce; font-size: 13px; font-weight: 600;">Читать далее &rarr;</a>
            </div>
            <div style="background: #fff; padding: 20px; border-radius: 8px; border: 1px solid #e2e8f0; box-shadow: 0 2px 4px rgba(0,0,0,0.04);">
                <span style="display: inline-block; font-size: 12px; font-weight: 600; color: #805ad5; background: #faf5ff; padding: 3px 8px; border-radius: 4px; margin-bottom: 10px;">Налоги</span>
                <h4 style="font-size: 16px; margin: 0 0 10px 0; line-height: 1.4;"><a href="/articles/imushhestvennyj-nalogovyj-vychet/" style="color: #2d3748; text-decoration: none;">Имущественный налоговый вычет: категории и возврат</a></h4>
                <a href="/articles/imushhestvennyj-nalogovyj-vychet/" style="color: #3182ce; font-size: 13px; font-weight: 600;">Читать далее &rarr;</a>
            </div>
            <div style="background: #fff; padding: 20px; border-radius: 8px; border: 1px solid #e2e8f0; box-shadow: 0 2px 4px rgba(0,0,0,0.04);">
                <span style="display: inline-block; font-size: 12px; font-weight: 600; color: #dd6b20; background: #fffaf0; padding: 3px 8px; border-radius: 4px; margin-bottom: 10px;">Автолизинг</span>
                <h4 style="font-size: 16px; margin: 0 0 10px 0; line-height: 1.4;"><a href="/articles/avto-v-lizing-fizicheskomu-litsu/" style="color: #2d3748; text-decoration: none;">Авто в лизинг для физлица: пошаговая инструкция</a></h4>
                <a href="/articles/avto-v-lizing-fizicheskomu-litsu/" style="color: #3182ce; font-size: 13px; font-weight: 600;">Читать далее &rarr;</a>
            </div>
        </div>
        <div style="text-align: center; margin-top: 25px;">
            <a href="/articles/" style="display: inline-block; padding: 10px 24px; background: #3182ce; color: #fff; text-decoration: none; border-radius: 6px; font-weight: 600; font-size: 14px;">Все полезные статьи &rarr;</a>
        </div>
    </div>
</section>
'''
        footer.insert_before(BeautifulSoup(section_html, 'html.parser'))
        index_html = str(soup)

    with open(os.path.join(REPO_DIR, "index.html"), "w", encoding="utf-8") as f:
        f.write(index_html)
    print("   [OK] index.html updated")

    print(">>> 2. Processing Service Pages...")
    for route_name, meta in SERVICE_ROUTES.items():
        src_file = os.path.join(SERVICES_DIR, meta["file"])
        if not os.path.exists(src_file):
            print(f"   [WARN] Source file {src_file} missing, skipping")
            continue
        with open(src_file, "r", encoding="utf-8") as f:
            content = f.read()

        active_path = f"/{route_name}/"
        cleaned_content = clean_links(content, active_path=active_path)

        # Update source in pages/services
        with open(src_file, "w", encoding="utf-8") as f:
            f.write(cleaned_content)

        # Save to /<route_name>/index.html and /<route_name>.html
        save_html_pair(os.path.join(REPO_DIR, route_name), route_name, cleaned_content)
        print(f"   [OK] Created /{route_name}/ and /{route_name}.html")

        # Also create legacy aliases /page/<id>/index.html and .html
        for leg_id in meta["legacy"]:
            leg_dir = os.path.join(REPO_DIR, "page", leg_id)
            save_html_pair(leg_dir, f"page/{leg_id}", cleaned_content)
            print(f"      [OK] Legacy alias: /page/{leg_id}/ -> {route_name}")

    print(">>> 3. Processing 13 Articles...")
    article_files = [f for f in os.listdir(ARTICLES_DIR) if f.endswith(".html")]
    articles_meta = []

    # Read base layout template from osago.html
    with open(os.path.join(REPO_DIR, "osago", "index.html"), "r", encoding="utf-8") as f:
        base_template = f.read()

    for af in article_files:
        slug = af.replace(".html", "")
        af_path = os.path.join(ARTICLES_DIR, af)
        with open(af_path, "r", encoding="utf-8") as f:
            art_raw = f.read()

        art_soup = BeautifulSoup(art_raw, "html.parser")
        h1 = art_soup.find("h1")
        h1_text = h1.get_text(strip=True) if h1 else slug.replace("-", " ").capitalize()

        title_tag = art_soup.find("title")
        title_text = title_tag.get_text(strip=True) if title_tag else h1_text

        meta_desc = ""
        desc_tag = art_soup.find("meta", attrs={"name": "description"})
        if desc_tag and desc_tag.get("content"):
            meta_desc = desc_tag["content"]

        entry = art_soup.find("div", class_="entry-content") or art_soup.find("article")
        if not entry:
            entry_html = f"<h1>{h1_text}</h1><p>Материал готовится к публикации.</p>"
        else:
            # Strip all third-party spam / scraper links
            for a_tag in entry.find_all("a"):
                href = a_tag.get("href", "")
                if "polishelp.ru" in href or href.startswith("/") or href.startswith("#"):
                    continue
                if "youtube.com" in href or "youtu.be" in href or "dzen.ru" in href:
                    a_tag.decompose()
                else:
                    a_tag.unwrap()

            # Contextual PBN injection for specific target articles
            raw_entry_str = str(entry)
            if slug == "kak-oformit-osago-na-avtomobil":
                if "polishelp.ru" not in raw_entry_str:
                    raw_entry_str = raw_entry_str.replace(
                        "проверке полиса",
                        '<a href="https://polishelp.ru/osago/check/" target="_blank" rel="noopener" style="color: #2563eb; font-weight: 600; text-decoration: underline;">проверке полиса ОСАГО по единой базе РСА</a>'
                    ).replace(
                        "электронного полиса",
                        '<a href="https://polishelp.ru/osago/check/" target="_blank" rel="noopener" style="color: #2563eb; font-weight: 600; text-decoration: underline;">электронного полиса ОСАГО</a>'
                    )
            elif slug in ["imushhestvennyj-nalogovyj-vychet", "nalog-s-prodazhi-doma"]:
                if "polishelp.ru" not in raw_entry_str:
                    raw_entry_str = raw_entry_str.replace(
                        "ипотеке",
                        '<a href="https://polishelp.ru/ipoteka/vtb/" target="_blank" rel="noopener" style="color: #2563eb; font-weight: 600; text-decoration: underline;">страховании ипотеки ВТБ</a>'
                    )
            entry_html = raw_entry_str

        # Excerpt for catalogue
        p_tag = art_soup.find("p")
        excerpt = p_tag.get_text(strip=True)[:180] + "..." if p_tag else meta_desc[:180]

        articles_meta.append({
            "slug": slug,
            "title": h1_text,
            "desc": excerpt,
            "url": f"/articles/{slug}/"
        })

        # Inject article content into base site layout
        t_soup = BeautifulSoup(base_template, "html.parser")
        if t_soup.title:
            t_soup.title.string = f"{h1_text} – СтраховкаТут21"

        # Update meta description
        if meta_desc:
            desc_elem = t_soup.find("meta", attrs={"name": "description"})
            if desc_elem:
                desc_elem["content"] = meta_desc

        # Replace main content area
        content_sec = t_soup.find("section", id="content") or t_soup.find("div", class_="site-content")
        article_card_html = f"""
        <div class="content-block" style="max-width: 960px; margin: 30px auto; padding: 25px 35px; background: #fff; border-radius: 8px; box-shadow: 0 4px 15px rgba(0,0,0,0.06); font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Helvetica, Arial, sans-serif; line-height: 1.7; color: #2d3748;">
            <div style="font-size: 13px; color: #718096; margin-bottom: 15px;">
                <a href="/" style="color: #3182ce; text-decoration: none;">Главная</a> &gt; 
                <a href="/articles/" style="color: #3182ce; text-decoration: none;">Полезные статьи</a> &gt; 
                <span>{h1_text}</span>
            </div>
            <h1 style="font-size: 28px; line-height: 1.3; color: #1a202c; margin-bottom: 25px; border-bottom: 2px solid #edf2f7; padding-bottom: 15px;">{h1_text}</h1>
            <div class="article-body-text" style="font-size: 16px;">
                {entry_html}
            </div>
            <div style="margin-top: 40px; padding: 20px; background: #ebf8ff; border-left: 4px solid #3182ce; border-radius: 4px;">
                <h4 style="margin: 0 0 10px 0; color: #2b6cb0; font-size: 17px;">Нужна консультация или расчет полиса?</h4>
                <p style="margin: 0 0 12px 0; font-size: 14px; color: #4a5568;">Сравните актуальные предложения страховых компаний и проверьте статус полиса по единой базе:</p>
                <div style="display: flex; gap: 15px; flex-wrap: wrap;">
                    <a href="/osago/" style="display: inline-block; padding: 8px 18px; background: #3182ce; color: #fff; text-decoration: none; border-radius: 4px; font-weight: 500; font-size: 14px;">Расчет ОСАГО</a>
                    <a href="https://polishelp.ru/osago/check/" target="_blank" rel="noopener" style="display: inline-block; padding: 8px 18px; background: #38a169; color: #fff; text-decoration: none; border-radius: 4px; font-weight: 500; font-size: 14px;">Проверка полиса в РСА</a>
                </div>
            </div>
        </div>
        """
        if content_sec:
            content_sec.clear()
            content_sec.append(BeautifulSoup(article_card_html, "html.parser"))

        styled_art_html = clean_links(str(t_soup), active_path="/articles/")

        # Save to /articles/<slug>/index.html and /articles/<slug>.html
        art_dir = os.path.join(REPO_DIR, "articles", slug)
        save_html_pair(art_dir, f"articles/{slug}", styled_art_html)
        # Also update pages/articles/<af>
        with open(af_path, "w", encoding="utf-8") as f:
            f.write(styled_art_html)

    print(f"   [OK] Processed and styled {len(article_files)} articles")

    print(">>> 4. Creating /articles/ Catalog Hub...")
    articles_list_cards = ""
    for a in articles_meta:
        articles_list_cards += f"""
        <div style="background: #fff; border: 1px solid #e2e8f0; border-radius: 8px; padding: 20px; transition: transform 0.2s, box-shadow 0.2s; box-shadow: 0 2px 5px rgba(0,0,0,0.04);">
            <h3 style="font-size: 19px; margin: 0 0 10px 0; line-height: 1.4;">
                <a href="{a['url']}" style="color: #2b6cb0; text-decoration: none;">{a['title']}</a>
            </h3>
            <p style="font-size: 14px; color: #718096; line-height: 1.6; margin: 0 0 15px 0;">{a['desc']}</p>
            <a href="{a['url']}" style="color: #3182ce; font-weight: 600; font-size: 14px; text-decoration: underline;">Читать статью &rarr;</a>
        </div>
        """

    hub_content_html = f"""
    <div class="content-block" style="max-width: 1040px; margin: 30px auto; padding: 25px; font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Helvetica, Arial, sans-serif;">
        <h1 style="font-size: 32px; color: #1a202c; margin-bottom: 10px; text-align: center;">База знаний и полезные статьи</h1>
        <p style="text-align: center; color: #718096; font-size: 16px; margin-bottom: 35px;">Актуальные материалы по ОСАГО, КАСКО, налоговым вычетам, автокредитованию и страхованию</p>
        <div style="display: grid; grid-template-columns: repeat(auto-fill, minmax(320px, 1fr)); gap: 20px;">
            {articles_list_cards}
        </div>
    </div>
    """

    hub_soup = BeautifulSoup(base_template, "html.parser")
    if hub_soup.title:
        hub_soup.title.string = "Полезные статьи и обзоры по страхованию – СтраховкаТут21"
    hub_content_sec = hub_soup.find("section", id="content") or hub_soup.find("div", class_="site-content")
    if hub_content_sec:
        hub_content_sec.clear()
        hub_content_sec.append(BeautifulSoup(hub_content_html, "html.parser"))

    hub_html = clean_links(str(hub_soup), active_path="/articles/")
    save_html_pair(os.path.join(REPO_DIR, "articles"), "articles", hub_html)
    print("   [OK] Created /articles/ hub")

    print(">>> 5. Generating sitemap.xml...")
    all_urls = [
        "https://strahovkatut21.ru/",
        "https://strahovkatut21.ru/osago/",
        "https://strahovkatut21.ru/kasko/",
        "https://strahovkatut21.ru/ipoteka/",
        "https://strahovkatut21.ru/imushchestvo/",
        "https://strahovkatut21.ru/inye-vidy/",
        "https://strahovkatut21.ru/zelenaya-karta/",
        "https://strahovkatut21.ru/kbm/",
        "https://strahovkatut21.ru/contacts/",
        "https://strahovkatut21.ru/kredity/",
        "https://strahovkatut21.ru/vtoroe-med-mnenie/",
        "https://strahovkatut21.ru/articles/"
    ]
    for a in articles_meta:
        all_urls.append(f"https://strahovkatut21.ru{a['url']}")

    sitemap_xml = ['<?xml version="1.0" encoding="UTF-8"?>', '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">']
    for url in all_urls:
        pri = "1.0" if url == "https://strahovkatut21.ru/" else ("0.9" if "/osago/" in url or "/ipoteka/" in url else "0.8")
        sitemap_xml.append(f"  <url><loc>{url}</loc><lastmod>2026-11-15</lastmod><changefreq>weekly</changefreq><priority>{pri}</priority></url>")
    sitemap_xml.append("</urlset>")

    with open(os.path.join(REPO_DIR, "sitemap.xml"), "w", encoding="utf-8") as f:
        f.write("\n".join(sitemap_xml))
    print(f"   [OK] Generated sitemap.xml with {len(all_urls)} URLs")

    print("\n>>> ALL TASKS COMPLETED SUCCESSFULLY! <<<")

if __name__ == "__main__":
    main()
