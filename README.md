Django E-Commerce Scraper
A Django application for scraping product data from e-commerce sites (using brain.com.ua as an example) with Requests, Selenium, and Playwright.

Features
Data Scraping: Collects product data (name, price, code, specifications, photos).

Three Scraping Methods:

Requests + BeautifulSoup: Fast scraping for static HTML.

Selenium: Scraping dynamic sites with browser-based JavaScript execution.

Playwright: Asynchronous scraping of dynamic sites.

Data Storage: Uses Django ORM to save data to PostgreSQL.

Data Export: A custom Django command to export data from the database to products_export.csv.

Tech Stack
Backend: Django

Database: PostgreSQL (psycopg2-binary)

Scraping:

requests

beautifulsoup4

selenium

playwright

Structure (Core Components)
config/: Django project configuration (settings.py, urls.py).

parser_app/: The main application.

models.py: The Product model for the database.

management/commands/: Custom commands to run scrapers and export data.

modules/: Isolated scraper logic.

requests_parser.py: Scraper using requests + BeautifulSoup.

selenium_parser.py: Scraper using Selenium.

playwright_parser.py: Scraper using Playwright.

Installation and Setup
Prerequisites

Python 3.x

PostgreSQL

Git

Quick Start

Clone the repository:

Bash

git clone <REPOSITORY_URL>
cd parsing
Create and activate a virtual environment:

Bash

python -m venv venv
source venv/bin/activate  # (Linux/Mac)
.\venv\Scripts\activate   # (Windows)
Install dependencies:

Bash

pip install -r requirements.txt
Install Playwright browsers (for save_playwright_product):

Bash

playwright install
Configure the PostgreSQL database:

Create a database (e.g., parser_db) and a user.

Update the DATABASES config in config/settings.py:

Python

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
Apply database migrations:

Bash

python manage.py migrate
Usage (Commands)
Custom Django commands are used to run the scrapers and export data.

Run Scraper (Requests): Parses using requests and BeautifulSoup.

Bash

python manage.py save_product
Run Scraper (Selenium): Parses using Selenium and Chrome.

Bash

python manage.py save_selenium_product
Run Scraper (Playwright): Parses using Playwright (asynchronously).

Bash

python manage.py save_playwright_product
Export Data to CSV: Saves all data from the Product model to products_export.csv in the project root.

Bash

python manage.py export_csv
Running Tests
To run tests (currently, the tests.py file is empty):

Bash

python manage.py test parser_app
Troubleshooting
DB Connection Errors: Check the DATABASES settings in config/settings.py.

Scrapers Find No Data: The target site (brain.com.ua) may have changed its HTML structure. The selectors in the respective modules/*.py files will need to be updated.

Selenium/Playwright Errors: Ensure the necessary drivers and browsers are installed (playwright install).

License
This project is distributed under the MIT License.

Contributing
Contributions are welcome. Please feel free to submit a Pull Request.
