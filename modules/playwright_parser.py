import json
import asyncio
from playwright.async_api import async_playwright


async def extract_specs(page):
    specs = {}

    rows = await page.query_selector_all("dl.char-line")
    for row in rows:
        try:
            key_element = await row.query_selector("dt.char-line__title")
            val_element = await row.query_selector("dd.char-line__value")
            if key_element and val_element:
                key_text = await key_element.text_content()
                val_text = await val_element.text_content()
                key = ' '.join(key_text.split())
                val = ' '.join(val_text.split())
                if key and val:
                    specs[key] = val
        except Exception:
            continue

    if not specs:
        rows = await page.query_selector_all("div.char-line")
        for row in rows:
            try:
                key_element = await row.query_selector(".char-line__title")
                val_element = await row.query_selector(".char-line__value")
                if key_element and val_element:
                    key_text = await key_element.text_content()
                    val_text = await val_element.text_content()
                    key = ' '.join(key_text.split())
                    val = ' '.join(val_text.split())
                    if key and val:
                        specs[key] = val
            except Exception:
                continue

    if not specs:
        rows = await page.query_selector_all("#specification .char-line")
        for row in rows:
            try:
                key_element = await row.query_selector(".char-line__title")
                val_element = await row.query_selector(".char-line__value")
                if key_element and val_element:
                    key_text = await key_element.text_content()
                    val_text = await val_element.text_content()
                    key = ' '.join(key_text.split())
                    val = ' '.join(val_text.split())
                    if key and val:
                        specs[key] = val
            except Exception:
                continue

    if not specs:
        rows = await page.query_selector_all("div.br-pp-spec-cont dl")
        for row in rows:
            try:
                key_element = await row.query_selector("dt")
                val_element = await row.query_selector("dd")
                if key_element and val_element:
                    key_text = await key_element.text_content()
                    val_text = await val_element.text_content()
                    key = ' '.join(key_text.split())
                    val = ' '.join(val_text.split())
                    if key and val:
                        specs[key] = val
            except Exception:
                continue

    if not specs:
        rows = await page.query_selector_all("table tr")
        for row in rows:
            cells = await row.query_selector_all("td")
            if len(cells) >= 2:
                key_text = await cells[0].text_content()
                val_text = await cells[1].text_content()
                key = ' '.join(key_text.split())
                val = ' '.join(val_text.split())
                if key and val:
                    specs[key] = val

    if not specs:
        rows = await page.query_selector_all("ul.spec li")
        for row in rows:
            text_content = await row.text_content()
            text = ' '.join(text_content.split())
            if ":" in text:
                key, val = text.split(":", 1)
                if key and val:
                    specs[key.strip()] = val.strip()

    if not specs:
        rows = await page.query_selector_all(
            "xpath=//div[contains(@class, 'br-pr-chr-item')]//div[span[1] and span[2]]")
        for row in rows:
            try:
                key_element = await row.query_selector("xpath=./span[1]")
                val_element = await row.query_selector("xpath=./span[2]")
                if key_element and val_element:
                    key_text = await key_element.text_content()
                    val_text = await val_element.text_content()
                    key = ' '.join(key_text.split())
                    val = ' '.join(val_text.split())
                    if key and val:
                        specs[key] = val
            except Exception:
                continue

    return specs


async def handle_modals_and_cookies(page):
    try:
        await page.wait_for_timeout(2000)

        cookie_selectors = [
            "button[id*='cookie'][id*='accept']",
            "button[class*='cookie'][class*='accept']",
            "button:has-text('Прийняти')",
            "button:has-text('Согласиться')",
            "button:has-text('Accept')",
            ".cookie-consent button",
            "#cookie-consent button",
            "[data-cookie-consent] button"
        ]

        for selector in cookie_selectors:
            try:
                element = await page.query_selector(selector)
                if element and await element.is_visible():
                    await element.click()
                    break
            except Exception:
                continue

        modal_selectors = [
            ".modal .close",
            ".popup .close",
            "[role='dialog'] button",
            ".overlay button"
        ]

        for selector in modal_selectors:
            try:
                element = await page.query_selector(selector)
                if element and await element.is_visible():
                    await element.click()
                    break
            except Exception:
                continue

    except Exception:
        pass


async def find_search_input(page):
    selectors = [
        "input.quick-search-input[placeholder='Знайти...']",
        "input.quick-search-input",
        "form[action='/ukr/filter/'] input[type='search']",
        "input[type='search'][class='quick-search-input']",
        "input[placeholder*='Знайти']",
        "input[placeholder*='найти']",
        "input[placeholder*='Search']",
        "input[placeholder*='Поиск']",
        "input[type='search']",
        ".quick-search-input",
        "#search",
        "input.search-input",
        "input[name*='search']",
        "input[id*='search']",
        ".search input",
        ".search-form input",
        ".header-search input",
        ".top-search input",
        "[data-search] input",
        "form[action*='search'] input",
        "form[action*='filter'] input",
        ".navbar input[type='text']",
        ".header input[type='text']",
        "input[placeholder*='товар']",
        "input[placeholder*='продук']",
        ".search-container input",
        "#header-search input",
        ".site-search input"
    ]

    for selector in selectors:
        try:
            element = await page.query_selector(selector)
            if element and await element.is_visible():
                return element
        except Exception:
            continue

    try:
        all_inputs = await page.query_selector_all("input[type='text'], input:not([type]), input[type='search']")
        for inp in all_inputs:
            try:
                if await inp.is_visible():
                    placeholder = await inp.get_attribute("placeholder") or ""
                    name = await inp.get_attribute("name") or ""
                    id_attr = await inp.get_attribute("id") or ""
                    class_attr = await inp.get_attribute("class") or ""
                    text_to_check = f"{placeholder} {name} {id_attr} {class_attr}".lower()
                    if any(keyword in text_to_check for keyword in ['search', 'поиск', 'знайти', 'найти', 'товар', 'продук']):
                        return inp
            except Exception:
                continue
    except Exception:
        pass

    return None


async def get_product_info(base_url: str, search_query: str):
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        page = await browser.new_page()

        page.set_default_timeout(60000)
        page.set_default_navigation_timeout(60000)

        await page.set_extra_http_headers({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
        })

        try:
            try:
                await page.goto(base_url, wait_until='domcontentloaded', timeout=60000)
            except Exception:
                await page.goto(base_url, wait_until='load', timeout=60000)

            await page.wait_for_timeout(5000)

            title = await page.title()
            if not title or "error" in title.lower() or len(title) < 3:
                raise Exception("Page did not load correctly")

            await handle_modals_and_cookies(page)

            search_input = await find_search_input(page)
            if not search_input:
                raise Exception("Could not find search input field")

            await search_input.fill(search_query)
            await search_input.press("Enter")

            try:
                await page.wait_for_selector("div[class*='goods-block'], .product-list, .search-results", timeout=20000)
            except Exception:
                pass

            product_selectors = [
                "xpath=(//div[contains(@class, 'goods-block__item')])[1]//a[@href]",
                ".product-item:first-child a",
                ".goods-item:first-child a",
                ".product-card:first-child a",
                ".search-result:first-child a"
            ]

            product_link = None
            for selector in product_selectors:
                try:
                    product_link = await page.query_selector(selector)
                    if product_link:
                        break
                except Exception:
                    continue

            if not product_link:
                raise Exception("Product not found in search results")

            await product_link.click()
            await page.wait_for_load_state('networkidle')

            scripts = await page.query_selector_all("script[type='application/ld+json']")
            ld_json = None
            for script in scripts:
                try:
                    script_content = await script.inner_html()
                    data = json.loads(script_content.strip())
                    if isinstance(data, dict) and data.get("@type") == "Product":
                        ld_json = data
                        break
                    if isinstance(data, list):
                        for item in data:
                            if isinstance(item, dict) and item.get("@type") == "Product":
                                ld_json = item
                                break
                except Exception:
                    continue

            product = {
                "full_name": None, "color": None, "memory": None, "seller": None,
                "price": None, "special_price": None, "photos": [],
                "product_code": None, "reviews_count": 0, "series": None,
                "screen_diagonal": None, "screen_resolution": None, "specifications": {}
            }

            if ld_json:
                product["full_name"] = ld_json.get("name")
                img = ld_json.get("image")
                if img:
                    product["photos"] = img if isinstance(img, list) else [img]
                product["product_code"] = ld_json.get("sku") or ld_json.get("mpn") or ld_json.get("productID")

                offers = ld_json.get("offers")
                if isinstance(offers, dict):
                    product["price"] = offers.get("price")
                    seller = offers.get("seller")
                    if isinstance(seller, dict):
                        product["seller"] = seller.get("name")

                agg = ld_json.get("aggregateRating")
                if isinstance(agg, dict):
                    product["reviews_count"] = agg.get("reviewCount") or agg.get("ratingCount") or 0

            try:
                data_container = await page.query_selector("div[class*='br-container-prt']")
                if data_container:
                    if not product["seller"]:
                        product["seller"] = await data_container.get_attribute("data-vendor")
                    if not product["series"]:
                        product["series"] = await data_container.get_attribute("data-model")
            except Exception:
                pass

            if not product["product_code"]:
                try:
                    code_element = await page.query_selector("span.br-pr-code-val")
                    if code_element:
                        code_text = await code_element.text_content()
                        product["product_code"] = ' '.join(code_text.split())
                except Exception:
                    pass

            try:
                all_specs_selectors = [
                    "xpath=//span[text()='Всі характеристики']",
                    "xpath=//span[text()='Все характеристики']",
                    "xpath=//a[contains(text(), 'характеристики')]",
                    ".show-all-specs", ".all-characteristics"
                ]

                specs_btn = None
                for selector in all_specs_selectors:
                    try:
                        specs_btn = await page.query_selector(selector)
                        if specs_btn and await specs_btn.is_visible():
                            break
                    except Exception:
                        continue

                if specs_btn:
                    await specs_btn.click()
                    await page.wait_for_timeout(2000)

                specs = await extract_specs(page)
                product["specifications"] = specs

                def find_spec(keys):
                    for k in keys:
                        for kk, vv in specs.items():
                            if k.lower() in kk.lower():
                                return vv
                    return None

                if not product["series"]:
                    product["series"] = find_spec(["Серія", "Серия", "Model"])
                product["screen_diagonal"] = find_spec(["Діагональ", "Диагональ"])
                product["screen_resolution"] = find_spec(["Роздільна здатність", "Разрешение", "Resolution"])
                if not product["color"]:
                    product["color"] = find_spec(["Колір", "Цвет", "Color"])
                if not product["memory"]:
                    product["memory"] = find_spec(["Пам'ять", "Память", "Memory", "Storage"])

            except Exception:
                pass

            for k, v in product.items():
                print(f"{k}: {v}")

            return product

        except Exception as e:
            print(f"An error occurred: {e}")
            raise
        finally:
            await browser.close()


async def main():
    base_url = "https://brain.com.ua/ukr/"
    query = "Apple iPhone 15 128GB Black"
    try:
        await get_product_info(base_url, query)
    except Exception as e:
        pass


if __name__ == "__main__":
    asyncio.run(main())