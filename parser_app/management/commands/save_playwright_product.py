import os
import sys
import asyncio
from django.core.management.base import BaseCommand
from parser_app.models import Product

project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '../../../'))
if project_root not in sys.path:
    sys.path.append(project_root)

from modules.playwright_parser import get_product_info

class Command(BaseCommand):
    help = 'Parses a product page using Playwright and saves the data to the database'

    def handle(self, *args, **options):
        base_url = "https://brain.com.ua/ukr/"
        query = "Apple iPhone 15 128GB Black"

        self.stdout.write(self.style.NOTICE(f"Starting Playwright parser for query: '{query}'..."))

        try:
            data = asyncio.run(get_product_info(base_url, query))
        except Exception as e:
            self.stderr.write(self.style.ERROR(f"An error occurred during Playwright parsing: {e}"))
            return

        if not data or not data.get('product_code'):
            self.stderr.write(self.style.ERROR("Could not extract product code. Aborting save."))
            return

        product_data = {
            'full_name': data.get('full_name'),
            'price': data.get('price'),
            'special_price': data.get('special_price'),
            'seller': data.get('seller'),
            'reviews_count': data.get('reviews_count'),
            'color': data.get('color'),
            'memory': data.get('memory'),
            'series': data.get('series'),
            'screen_diagonal': data.get('screen_diagonal'),
            'display_resolution': data.get('screen_resolution'),
            'photos': data.get('photos'),
            'specifications': data.get('specifications'),
        }

        product, created = Product.objects.update_or_create(
            product_code=data.get('product_code'),
            defaults=product_data
        )

        if created:
            self.stdout.write(self.style.SUCCESS(f"Successfully CREATED product: {product.full_name}"))
        else:
            self.stdout.write(self.style.SUCCESS(f"Successfully UPDATED product: {product.full_name}"))