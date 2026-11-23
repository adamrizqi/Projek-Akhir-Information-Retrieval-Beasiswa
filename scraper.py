import os
import re
import csv
import json
import time
import urllib.request
from html import unescape
from urllib import robotparser
from urllib.parse import urljoin, urlparse

HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) Chrome/124.0.0.0 Safari/537.36'
}

DELAY = 0.5

MONTH_MAP = {
    'jan': 1, 'januari': 1, 'january': 1,
    'feb': 2, 'februari': 2, 'february': 2,
    'mar': 3, 'maret': 3, 'march': 3,
    'apr': 4, 'april': 4,
    'mei': 5, 'may': 5,
    'jun': 6, 'juni': 6, 'june': 6,
    'jul': 7, 'juli': 7, 'july': 7,
    'agu': 8, 'agt': 8, 'agustus': 8, 'aug': 8, 'august': 8,
    'sep': 9, 'september': 9,
    'okt': 10, 'oktober': 10, 'oct': 10, 'october': 10,
    'nov': 11, 'november': 11,
    'des': 12, 'desember': 12, 'dec': 12, 'december': 12
}

def check_robots(base_url, target_url):
    try:
        rp = robotparser.RobotFileParser()
        robots_url = urljoin(base_url, "/robots.txt")
        rp.set_url(robots_url)
        rp.read()
        return rp.can_fetch(HEADERS['User-Agent'], target_url)
    except Exception:
        return True

def fetch_page(url):
    req = urllib.request.Request(url, headers=HEADERS)
    try:
        with urllib.request.urlopen(req, timeout=12) as res:
            return res.read().decode('utf-8', errors='ignore')
    except Exception as e:
        print(f"Gagal mengambil {url}: {e}")
        return None

def normalize_url(url):
    parsed = urlparse(url)
    path = parsed.path.rstrip("/") or "/"
    return f"{parsed.scheme}://{parsed.netloc}{path}"

def parse_deadline(text):
    if not text:
        return ""
    matches = list(re.finditer(r'(\d{1,2})\s+([a-zA-Z]+)\s+(\d{4})', text))
    found_dates = []
    for m in matches:
        d = int(m.group(1))
        m_str = m.group(2).lower()
        m_num = MONTH_MAP.get(m_str, MONTH_MAP.get(m_str[:3]))
        y = int(m.group(3))
        if m_num and 1 <= d <= 31 and 2020 <= y <= 2035:
            found_dates.append(f"{y:04d}-{m_num:02d}-{d:02d}")
    return found_dates[-1] if found_dates else ""

def clean_html(raw_html):
    if not raw_html:
        return ""
    text = re.sub(r'<div[^>]*id=["\']rank-math-toc["\'][^>]*>.*?</div>', ' ', raw_html, flags=re.S | re.I)
    text = re.sub(r'<div[^>]*class=["\'][^"\']*toc[^"\']*["\'][^>]*>.*?</div>', ' ', text, flags=re.S | re.I)
    text = re.sub(r'<(script|style|noscript)[^>]*>.*?</\1>', ' ', text, flags=re.S | re.I)
    text = re.sub(r'<div class=["\']sharedaddy[^"\']*["\'].*?</div>', ' ', text, flags=re.S | re.I)
    text = re.sub(r'<(p|br|div|li|h[1-6])[^>]*>', '\n', text, flags=re.I)
    text = re.sub(r'<[^>]+>', ' ', text)
    text = unescape(text)
    lines = [re.sub(r'[ \t]+', ' ', l).strip() for l in text.split('\n')]
    return '\n'.join([l for l in lines if l])

def extract_section(full_text, start_keywords, stop_keywords, min_len=30):
    lower = full_text.lower()
    start_idx = -1
    for kw in start_keywords:
        pos = lower.find(kw.lower())
        if pos != -1:
            if start_idx == -1 or pos < start_idx:
                start_idx = pos
    if start_idx == -1:
        return ""
    
    stop_idx = len(full_text)
    for kw in stop_keywords:
        pos = lower.find(kw.lower(), start_idx + 50)
        if pos != -1 and pos < stop_idx:
            stop_idx = pos
            
    res = full_text[start_idx:stop_idx].strip()
    return res if len(res) >= min_len else ""

def crawl_links(base_categories):
    candidates = []
    seen = set()
    ignored = ['daftar beasiswa', 'info lomba', 'lomba', 'pelatihan', 'workshop', 'tips', 'panduan']

    for cat_url, max_p in base_categories:
        for p in range(1, max_p + 1):
            url = f"{cat_url}?paged={p}" if p > 1 else cat_url
            print(f"Crawl halaman: {url}")
            html = fetch_page(url)
            if not html:
                break

            articles = re.findall(r'<article[^>]*>(.*?)</article>', html, re.S)
            if not articles:
                break

            for art in articles:
                m_link = re.search(r'<h2[^>]*class=["\'][^"\']*(?:beasiswa-card-title|entry-title)[^"\']*["\'][^>]*>\s*<a\s+href=["\']([^"\']+)["\'][^>]*>(.*?)</a>', art, re.S)
                if not m_link:
                    continue

                link = normalize_url(m_link.group(1).strip())
                if link in seen:
                    continue

                title = re.sub(r'<[^>]+>', '', m_link.group(2)).strip()
                t_lower = title.lower()

                if any(x in t_lower for x in ignored) or 'daftar-beasiswa' in link:
                    continue

                seen.add(link)
                status = "Dibuka" if 'beasiswa-status-open' in art else "Ditutup"

                clean_art = re.sub(r'<[^>]+>', ' ', art)
                m_dl = re.search(r'Deadline\s*:\s*([0-9]{1,2}\s+[a-zA-Z]+\s+[0-9]{4})', clean_art)
                card_dl = parse_deadline(m_dl.group(1).strip()) if m_dl else ""

                candidates.append({
                    'url': link,
                    'title': title,
                    'status': status,
                    'deadline': card_dl
                })

            time.sleep(DELAY)

    return candidates

def scrape_detail(item):
    html = fetch_page(item['url'])
    if not html:
        return None

    m_title = re.search(r'<h1[^>]*class=["\'][^"\']*entry-title[^"\']*["\'][^>]*>(.*?)</h1>', html, re.I | re.S)
    title = clean_html(m_title.group(1)).strip() if m_title else item['title']

    m_content = re.search(r'<div[^>]*class=["\'][^"\']*entry-content[^"\']*["\'][^>]*>(.*?)(?:<div class=["\'](?:sharedaddy|code-block)|<footer|<div id=["\']comments["\'])', html, re.I | re.S)
    clean_content = clean_html(m_content.group(1) if m_content else html)

    deadline = item.get('deadline', '')
    if not deadline:
        matches = re.findall(r'(?:deadline|batas waktu|paling lambat)[^\n.]{0,60}', clean_content, re.I)
        for m in matches:
            d = parse_deadline(m)
            if d:
                deadline = d
                break
    if not deadline:
        deadline = "TBA"

    # ekstrak syarat
    requirements = extract_section(
        clean_content,
        start_keywords=["PERSYARATAN BEASISWA", "PERSYARATAN UMUM", "PERSYARATAN", "SYARAT PENDAFTARAN", "KRITERIA", "KETENTUAN"],
        stop_keywords=["CARA MENDAFTAR", "BERKAS DOKUMEN", "DOKUMEN YANG DIBUTUHKAN", "TAHAPAN SELEKSI", "TIMELINE", "CAKUPAN", "KONTAK"]
    )
    if not requirements:
        paras = clean_content.split('\n')
        rel = [p for p in paras if any(k in p.lower() for k in ['syarat', 'ipk', 'semester', 'kriteria', 'd3', 'd4', 's1', 'kurang mampu'])]
        requirements = '\n'.join(rel[:12]) if rel else clean_content[:1000]

    if not requirements or len(requirements.strip()) < 25:
        return None

    # ekstrak berkas dokumen
    documents = extract_section(
        clean_content,
        start_keywords=["BERKAS DOKUMEN", "DOKUMEN YANG DIBUTUHKAN", "BERKAS YANG DIPERLUKAN", "PERSYARATAN BERKAS"],
        stop_keywords=["CARA MENDAFTAR", "TAHAPAN SELEKSI", "TIMELINE", "KONTAK"]
    )

    # ekstrak cakupan
    coverage = extract_section(
        clean_content,
        start_keywords=["CAKUPAN BEASISWA", "BIAYA YANG DITANGGUNG", "BENEFIT", "FASILITAS"],
        stop_keywords=["PERSYARATAN", "CARA MENDAFTAR", "TIMELINE", "BERKAS", "KONTAK"]
    )

    return {
        "title": title,
        "url": item['url'],
        "status": item.get('status', 'Dibuka'),
        "deadline": deadline,
        "requirements": requirements,
        "documents": documents,
        "coverage": coverage,
        "full_content": clean_content
    }

def main():
    os.makedirs("data", exist_ok=True)
    categories = [
        ('https://indbeasiswa.com/beasiswa-s1/', 25),
        ('https://indbeasiswa.com/beasiswa-diploma/', 15)
    ]

    candidates = crawl_links(categories)
    print(f"Total link beasiswa ditemukan: {len(candidates)}")

    results = []
    counter = 1
    for c in candidates:
        detail = scrape_detail(c)
        if not detail:
            continue
        results.append({
            "id": f"IND-{counter:03d}",
            "title": detail["title"],
            "source": "Indbeasiswa",
            "url": detail["url"],
            "status": detail["status"],
            "deadline": detail["deadline"],
            "requirements": detail["requirements"],
            "documents": detail["documents"],
            "coverage": detail["coverage"],
            "full_content": detail["full_content"]
        })
        counter += 1
        time.sleep(DELAY)

    # simpan json
    with open("data/scholarships.json", "w", encoding="utf-8") as f:
        json.dump(results, f, ensure_ascii=False, indent=2)

    # simpan csv
    with open("data/scholarships.csv", "w", encoding="utf-8", newline="") as f:
        fieldnames = ["id", "title", "source", "url", "status", "deadline", "requirements", "documents", "coverage"]
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        for d in results:
            writer.writerow({
                "id": d["id"],
                "title": d["title"],
                "source": d["source"],
                "url": d["url"],
                "status": d.get("status", "Dibuka"),
                "deadline": d.get("deadline", "TBA"),
                "requirements": d.get("requirements", "").replace("\n", " "),
                "documents": d.get("documents", "").replace("\n", " "),
                "coverage": d.get("coverage", "").replace("\n", " ")
            })

    print(f"Total beasiswa tersimpan: {len(results)}")

if __name__ == "__main__":
    main()
