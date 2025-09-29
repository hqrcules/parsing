import re
import json
from pprint import pprint
import requests
from bs4 import BeautifulSoup

headers = {"User-Agent": "Mozilla/5.0"}
url = "https://brain.com.ua/ukr/Mobilniy_telefon_Apple_iPhone_16_Pro_Max_256GB_Black_Titanium-p1145443.html"

def try_json_load(s: str):
    try:
        return json.loads(s)
    except Exception:
        s2 = re.sub(r",\s*}", "}", s)
        s2 = re.sub(r",\s*\]", "]", s2)
        try:
            return json.loads(s2)
        except Exception:
            return None

def extract_ld_json(soup):
    for script in soup.find_all("script", type="application/ld+json"):
        if not script.string:
            continue
        data = try_json_load(script.string.strip())
        if not data:
            continue
        if isinstance(data, list):
            for item in data:
                if isinstance(item, dict) and item.get("@type") in ("Product", "Offer"):
                    return item
        if isinstance(data, dict) and data.get("@type") == "Product":
            return data
    return None

def extract_specs_from_soup(soup: BeautifulSoup) -> dict:
    specs = {}
    char_lines = soup.find_all("div", class_="char-line")
    if char_lines:
        for line in char_lines:
            title_elem = line.find(class_=re.compile(r"title|name|key", re.I))
            value_elem = line.find(class_=re.compile(r"value|content|data", re.I))
            if title_elem and value_elem:
                key = title_elem.get_text(" ", strip=True)
                value = value_elem.get_text(" ", strip=True)
                if key and value:
                    specs[key] = value
            else:
                text = line.get_text(" ", strip=True)
                match = re.match(r"^([^::\-]+)[::\-]\s*(.+)$", text)
                if match:
                    key, value = match.groups()
                    key = key.strip()
                    value = value.strip()
                    if key and value and len(key) < 100:
                        specs[key] = value
    if not specs:
        specs_container = soup.find("div", id="specification")
        if not specs_container:
            specs_container = soup.find("div", class_="br-pp-spec-cont")
        if specs_container:
            for line in specs_container.find_all("dl", class_="char-line"):
                key_tag = line.find("dt", class_="char-line__title")
                value_tag = line.find("dd", class_="char-line__value")
                if key_tag and value_tag:
                    key = key_tag.get_text(" ", strip=True)
                    value = value_tag.get_text(" ", strip=True)
                    if key and value:
                        specs[key] = value
    if not specs:
        tables = soup.find_all("table")
        for table in tables:
            rows = table.find_all("tr")
            for row in rows:
                cells = row.find_all(["td", "th"])
                if len(cells) >= 2:
                    key = cells[0].get_text(" ", strip=True)
                    value = cells[1].get_text(" ", strip=True)
                    if key and value and key != value and len(key) < 100:
                        specs[key] = value
    if not specs:
        spec_containers = soup.find_all(["div", "section"], class_=re.compile(r"(spec|char|feature|detail)", re.I))
        for container in spec_containers:
            container_text = container.get_text(" ", strip=True)
            if len(container_text) > 300:
                continue
            items = container.find_all(["div", "p", "li", "span"])
            for item in items:
                text = item.get_text(" ", strip=True)
                if len(text) > 200:
                    continue
                match = re.match(r"^([^::\-]+)[::\-]\s*(.+)$", text)
                if match:
                    key, value = match.groups()
                    key = key.strip()
                    value = value.strip()
                    if key and value and len(key) < 100 and len(value) < 200:
                        specs[key] = value
    if not specs:
        dl_lists = soup.find_all("dl")
        for dl in dl_lists:
            dt_tags = dl.find_all("dt")
            dd_tags = dl.find_all("dd")
            if len(dt_tags) == len(dd_tags):
                for dt, dd in zip(dt_tags, dd_tags):
                    key = dt.get_text(" ", strip=True)
                    value = dd.get_text(" ", strip=True)
                    if key and value and len(key) < 100:
                        specs[key] = value
    if not specs:
        parent_containers = soup.find_all(["div", "section"], class_=re.compile(r"(spec|char|prop|detail)", re.I))
        for parent in parent_containers:
            spans = parent.find_all("span")
            for i in range(0, len(spans) - 1, 2):
                key_span = spans[i]
                value_span = spans[i + 1]
                key = key_span.get_text(" ", strip=True)
                value = value_span.get_text(" ", strip=True)
                if (key and value and len(key) < 100 and len(value) < 200
                        and key != value and not key.isdigit()):
                    specs[key] = value
    if not specs:
        spec_lists = soup.find_all("ul", class_=re.compile(r"(spec|char|feature)", re.I))
        for ul in spec_lists:
            for li in ul.find_all("li"):
                text = li.get_text(" ", strip=True)
                if len(text) > 200:
                    continue
                match = re.match(r"^([^:]+):\s*(.+)$", text)
                if match:
                    key, value = match.groups()
                    key = key.strip()
                    value = value.strip()
                    if key and value and len(key) < 100:
                        specs[key] = value
    cleaned_specs = {}
    for key, value in specs.items():
        if (key and value and key != value
                and not key.lower().startswith(value.lower()[:10])
                and not value.lower().startswith(key.lower()[:10])
                and len(key.strip()) > 2
                and len(value.strip()) > 0):
            cleaned_specs[key.strip()] = value.strip()
    return cleaned_specs

def parse_page(url):
    r = requests.get(url, headers=headers, timeout=20)
    r.raise_for_status()
    text = r.text
    soup = BeautifulSoup(text, "lxml")
    product = {
        "name": None,
        "color": None,
        "memory": None,
        "seller": None,
        "price_old": None,
        "price_new": None,
        "photos": [],
        "code": None,
        "reviews": 0,
        "series": None,
        "screen_diagonal": None,
        "screen_resolution": None,
        "specs": {},
    }
    h1 = soup.find("h1")
    if h1:
        product["name"] = h1.get_text(" ", strip=True)
    ld = extract_ld_json(soup)
    if ld:
        if not product["name"] and ld.get("name"):
            product["name"] = ld.get("name")
        img = ld.get("image") or ld.get("images")
        if img:
            product["photos"] = [str(x) for x in (img if isinstance(img, list) else [img])]
        sku = ld.get("sku") or ld.get("mpn") or ld.get("productID")
        if sku:
            product["code"] = str(sku)
        offers = ld.get("offers")
        if isinstance(offers, dict):
            price = offers.get("price")
            if price:
                product["price_new"] = re.sub(r"\D", "", str(price)) or None
            seller = offers.get("seller")
            if isinstance(seller, dict):
                product["seller"] = seller.get("name") or product["seller"]
        agg = ld.get("aggregateRating")
        if isinstance(agg, dict):
            rc = agg.get("reviewCount") or agg.get("ratingCount")
            try:
                product["reviews"] = int(rc) if rc else product["reviews"]
            except Exception:
                pass
    og_image = soup.find("meta", property="og:image")
    if og_image and og_image.get("content"):
        if og_image["content"] not in product["photos"]:
            product["photos"].insert(0, og_image["content"])
    gallery_links = soup.select(".br-pp-additional-photo a")
    for link in gallery_links:
        src = link.get("href")
        if not src:
            continue
        if src.startswith("//"):
            src = "https:" + src
        if src not in product["photos"]:
            product["photos"].append(src)
    price_selectors = [
        ".product-price__current", ".product-price__new", ".price", ".product-price .current", ".product-price-current",
        ".price-current",
        ".price__current", ".product-price"
    ]
    for sel in price_selectors:
        el = soup.select_one(sel)
        if el and el.get_text(strip=True):
            val = re.sub(r"\D", "", el.get_text())
            if val:
                product["price_new"] = val
                break
    for sel in [".product-price__old", ".price-old", ".product-price-old", ".price--old", ".product-price .old"]:
        el = soup.select_one(sel)
        if el and el.get_text(strip=True):
            val = re.sub(r"\D", "", el.get_text())
            if val:
                product["price_old"] = val
                break
    if not product["price_new"]:
        m = re.search(r"(\d{2,3}\d{0,3})\s*(?:грн|UAH|₴)", text)
        if m:
            product["price_new"] = re.sub(r"\D", "", m.group(1))
    m_code = re.search(r"Код товару[:\s]*([A-Za-z0-9\-_]+)", text)
    if m_code:
        product["code"] = m_code.group(1)
    rv_sel = [".product-rating__count", ".reviews-count", ".rating-count", ".product-reviews-count", ".comments-count"]
    for sel in rv_sel:
        el = soup.select_one(sel)
        if el:
            m = re.search(r"\d+", el.get_text())
            if m:
                product["reviews"] = int(m.group(0))
                break
    if not product["seller"]:
        site_title = None
        if soup.title and soup.title.string:
            site_title = soup.title.string.strip()
        if site_title:
            if "Brain" in site_title:
                product["seller"] = "Brain"
            else:
                product["seller"] = "brain.com.ua"
    specs = extract_specs_from_soup(soup)
    product["specs"] = specs
    def find_spec(keys):
        for k in keys:
            for spec_key in product["specs"].keys():
                if k.lower() in spec_key.lower():
                    return product["specs"][spec_key]
        return None
    product["series"] = find_spec(["Серія", "Series", "Модель", "Model"])
    product["screen_diagonal"] = find_spec(["Діагональ", "Diagonal", "Розмір", "Size"])
    product["screen_resolution"] = find_spec(["Роздільна здатність", "Resolution", "Дозвіл"])
    if product["name"]:
        color_match = re.search(r"(Black|White|Blue|Green|Titanium|Graphite|Gold|Silver|чорний|білий|зелений|синій)",
                                product["name"], re.I)
        if color_match:
            product["color"] = color_match.group(0)
        mem_match = re.search(r"(\d+\s?GB|\d+\s?Gb|\d+\s?Tb|\d+\s?TB)", product["name"], re.I)
        if mem_match:
            product["memory"] = mem_match.group(0).replace(" ", "")
    if not product["color"]:
        c = find_spec(["Колір", "Color"])
        if c:
            product["color"] = c
    if not product["memory"]:
        m = find_spec(["Обсяг пам'яті", "Пам'ять", "Memory", "Storage", "Накопичувач"])
        if m:
            product["memory"] = m
    product["photos"] = [p for p in product["photos"] if p]
    return product

if __name__ == "__main__":
    prod = parse_page(url)
    pprint(prod)