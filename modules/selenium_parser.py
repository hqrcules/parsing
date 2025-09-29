import json
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC


def extract_specs(driver):
    specs = {}

    rows = driver.find_elements(By.CSS_SELECTOR, "dl.char-line")
    for row in rows:
        try:
            key = row.find_element(By.CSS_SELECTOR, "dt.char-line__title").text.strip()
            val = row.find_element(By.CSS_SELECTOR, "dd.char-line__value").text.strip()
            if key and val:
                specs[key] = val
        except Exception:
            continue

    if not specs:
        rows = driver.find_elements(By.CSS_SELECTOR, "div.char-line")
        for row in rows:
            try:
                key = row.find_element(By.CSS_SELECTOR, ".char-line__title").text.strip()
                val = row.find_element(By.CSS_SELECTOR, ".char-line__value").text.strip()
                if key and val:
                    specs[key] = val
            except Exception:
                continue

    if not specs:
        rows = driver.find_elements(By.CSS_SELECTOR, "#specification .char-line")
        for row in rows:
            try:
                key = row.find_element(By.CSS_SELECTOR, ".char-line__title").text.strip()
                val = row.find_element(By.CSS_SELECTOR, ".char-line__value").text.strip()
                if key and val:
                    specs[key] = val
            except Exception:
                continue

    if not specs:
        rows = driver.find_elements(By.CSS_SELECTOR, "div.br-pp-spec-cont dl")
        for row in rows:
            try:
                key = row.find_element(By.TAG_NAME, "dt").text.strip()
                val = row.find_element(By.TAG_NAME, "dd").text.strip()
                if key and val:
                    specs[key] = val
            except Exception:
                continue

    if not specs:
        rows = driver.find_elements(By.CSS_SELECTOR, "table tr")
        for row in rows:
            cells = row.find_elements(By.TAG_NAME, "td")
            if len(cells) >= 2:
                key = cells[0].text.strip()
                val = cells[1].text.strip()
                if key and val:
                    specs[key] = val

    if not specs:
        rows = driver.find_elements(By.CSS_SELECTOR, "ul.spec li")
        for row in rows:
            text = row.text.strip()
            if ":" in text:
                key, val = text.split(":", 1)
                if key and val:
                    specs[key.strip()] = val.strip()

    if not specs:
        rows = driver.find_elements(By.XPATH, "//div[contains(@class, 'br-pr-chr-item')]//div[span[1] and span[2]]")
        for row in rows:
            try:
                key = row.find_element(By.XPATH, "./span[1]").text.strip()
                val = row.find_element(By.XPATH, "./span[2]").text.strip()
                if key and val:
                    specs[key] = val
            except Exception:
                continue

    return specs


def get_product_info(base_url: str, search_query: str):
    driver = webdriver.Chrome()
    driver.maximize_window()

    try:
        driver.get(base_url)

        search_inputs = WebDriverWait(driver, 20).until(
            EC.presence_of_all_elements_located((By.XPATH, "//input[@class='quick-search-input']"))
        )
        visible_search_input = next((i for i in search_inputs if i.is_displayed()), None)
        visible_search_input.send_keys(search_query)
        visible_search_input.send_keys(Keys.RETURN)

        search_results_container = WebDriverWait(driver, 20).until(
            EC.presence_of_element_located((By.XPATH, "//div[contains(@class, 'goods-block')]"))
        )
        product_link_xpath = "(//div[contains(@class, 'goods-block__item')])[1]//a[@href]"
        driver.find_element(By.XPATH, product_link_xpath).click()

        WebDriverWait(driver, 20).until(EC.staleness_of(search_results_container))

        scripts = driver.find_elements(By.XPATH, "//script[@type='application/ld+json']")
        ld_json = None
        for s in scripts:
            try:
                data = json.loads(s.get_attribute("innerHTML").strip())
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
            "full_name": None,
            "color": None,
            "memory": None,
            "seller": None,
            "price": None,
            "special_price": None,
            "photos": [],
            "product_code": None,
            "reviews_count": 0,
            "series": None,
            "screen_diagonal": None,
            "screen_resolution": None,
            "specifications": {}
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
            data_container = driver.find_element(By.XPATH, "//div[contains(@class, 'br-container-prt')]")
            if not product["seller"]:
                product["seller"] = data_container.get_attribute("data-vendor")
            if not product["series"]:
                product["series"] = data_container.get_attribute("data-model")
        except Exception:
            pass

        if not product["product_code"]:
            try:
                product["product_code"] = driver.find_element(By.XPATH, "//span[@class='br-pr-code-val']").text.strip()
            except Exception:
                pass

        try:
            all_specs_btn = WebDriverWait(driver, 5).until(
                EC.element_to_be_clickable((By.XPATH, "//span[text()='Всі характеристики']"))
            )
            all_specs_btn.click()

            specs = extract_specs(driver)
            product["specifications"] = specs

            def find_spec(keys):
                for k in keys:
                    for kk, vv in specs.items():
                        if k.lower() in kk.lower():
                            return vv
                return None

            if not product["series"]:
                product["series"] = find_spec(["Серія", "Model"])
            product["screen_diagonal"] = find_spec(["Діагональ"])
            product["screen_resolution"] = find_spec(["Роздільна здатність", "Resolution"])
            if not product["color"]:
                product["color"] = find_spec(["Колір", "Color"])
            if not product["memory"]:
                product["memory"] = find_spec(["Пам'ять", "Memory", "Storage"])

        except Exception:
            pass

        for k, v in product.items():
            print(f"{k}: {v}")

        return product

    finally:
        driver.quit()


if __name__ == "__main__":
    base_url = "https://brain.com.ua/ukr/"
    query = "Apple iPhone 15 128GB Black"
    get_product_info(base_url, query)