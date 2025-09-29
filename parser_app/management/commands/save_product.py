import os
import sys
from django.core.management.base import BaseCommand
from parser_app.models import Product

project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '../../../'))
if project_root not in sys.path:
    sys.path.append(project_root)

from modules.requests_parser import parse_page

class Command(BaseCommand):
    help = 'Parses a product page and saves the data to the database'

    def handle(self, *args, **options):
        url = "https://brain.com.ua/ukr/Mobilniy_telefon_Apple_iPhone_16_Pro_Max_256GB_Black_Titanium-p1145443.html"
        self.stdout.write(f"Parsing {url}...")

        try:
            data = parse_page(url)
        except Exception as e:
            self.stderr.write(self.style.ERROR(f"Failed to parse page: {e}"))
            return

        if not data or not data.get('code'):
            self.stderr.write(self.style.ERROR("Could not extract product code. Aborting save."))
            return

        product_data = {
            'full_name': data.get('name'),
            'price': data.get('price_new'),
            'special_price': data.get('price_old'),
            'seller': data.get('seller'),
            'reviews_count': data.get('reviews'),
            'color': data.get('color'),
            'memory': data.get('memory'),
            'series': data.get('series'),
            'screen_diagonal': data.get('screen_diagonal'),
            'display_resolution': data.get('screen_resolution'),
            'photos': data.get('photos'),
            'specifications': data.get('specs'),
        }

        product, created = Product.objects.update_or_create(
            product_code=data.get('code'),
            defaults=product_data
        )

        if created:
            self.stdout.write(self.style.SUCCESS(f"Successfully created product: {product.full_name}"))
        else:
            self.stdout.write(self.style.SUCCESS(f"Successfully updated product: {product.full_name}"))