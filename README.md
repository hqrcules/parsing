# 🛒 Django E-Commerce Scraper

> **A Django application for scraping and exporting product data from e-commerce websites**  
> *(Example target: [brain.com.ua](https://brain.com.ua))*

This project demonstrates a flexible scraping system built on **Django**, supporting multiple scraping methods — from simple HTTP parsing to full browser automation — with data storage and export capabilities.

---

## 🚀 Features

- **Data Scraping:**  
  Collects product information including:
  - Name  
  - Price  
  - Product code  
  - Specifications  
  - Image URLs

- **Three Scraping Methods:**
  1. **Requests + BeautifulSoup** — Fast static HTML parsing.  
  2. **Selenium** — Handles dynamic JavaScript-rendered content.  
  3. **Playwright** — Asynchronous scraping for modern interactive sites.

- **Data Storage:**  
  Persists results in a PostgreSQL database via Django ORM.

- **Data Export:**  
  Custom Django command to export all products to `products_export.csv`.

---

## 🧱 Tech Stack

| Layer | Technology |
|--------|-------------|
| **Backend** | Django |
| **Database** | PostgreSQL (`psycopg2-binary`) |
| **Scraping** | `requests`, `beautifulsoup4`, `selenium`, `playwright` |
| **Environment** | Python 3.x, Virtualenv |
| **Export** | CSV via Django custom commands |

---

## 📁 Project Structure

parsing/
├── config/ # Django project configuration
│ ├── settings.py
│ ├── urls.py
│ └── wsgi.py
├── parser_app/ # Main scraping application
│ ├── models.py # Product model (ORM)
│ ├── tests.py
│ ├── management/
│ │ └── commands/ # Custom Django commands
│ │ ├── save_product.py
│ │ ├── save_selenium_product.py
│ │ ├── save_playwright_product.py
│ │ └── export_csv.py
│ └── modules/ # Scraping logic
│ ├── requests_parser.py
│ ├── selenium_parser.py
│ └── playwright_parser.py
├── requirements.txt
└── manage.py

yaml
Копіювати код

---

## ⚙️ Installation & Setup

### **Prerequisites**
- Python 3.x  
- PostgreSQL  
- Git  

---

### **1. Clone the Repository**
```bash
git clone <https://github.com/hqrcules/parsing.git>
cd parsing
2. Create and Activate a Virtual Environment
bash
python -m venv venv
source venv/bin/activate   # Linux/Mac
.\venv\Scripts\activate    # Windows
3. Install Dependencies
bash
pip install -r requirements.txt
4. Install Playwright Browsers
(Required for the Playwright-based scraper.)

bash
playwright install
5. Configure Database
Create a PostgreSQL database (e.g., parser_db) and user, then update config/settings.py:

python
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': 'parser_db',
        'USER': 'parser_user',
        'PASSWORD': '12345678',
        'HOST': 'localhost',
        'PORT': '5432',
    }
}
6. Apply Migrations
bash
python manage.py migrate
🧩 Usage
Custom Django management commands are used to control scraping and export.

Command	Description
python manage.py save_product	Scrapes using Requests + BeautifulSoup
python manage.py save_selenium_product	Scrapes using Selenium + Chrome
python manage.py save_playwright_product	Scrapes using Playwright (async)
python manage.py export_csv	Exports all product data to products_export.csv

Example:

bash
python manage.py save_playwright_product
📊 Example Output
Example CSV export (products_export.csv):

Name	Price	Code	Specs	Image URL
Lenovo IdeaPad 3	18 999 ₴	81WB001CRA	Ryzen 5 / 16GB / 512GB SSD	https://...

🧪 Testing
To run tests (currently minimal placeholder):

bash
python manage.py test parser_app
🩺 Troubleshooting
Issue	Solution
Database connection error	Check PostgreSQL credentials in config/settings.py.
No data scraped	Target site structure may have changed — update CSS selectors in modules/*.py.
Selenium/Playwright errors	Ensure browser drivers are installed (playwright install, chromedriver for Selenium).

📜 License
This project is released under the MIT License.

🤝 Contributing
Contributions are welcome!
Please open an Issue or submit a Pull Request with improvements or new scraping logic.
