import csv
import json
from django.core.management.base import BaseCommand
from parser_app.models import Product


class Command(BaseCommand):
    help = 'Exports product data to a CSV file'

    def handle(self, *args, **options):
        output_filename = 'products_export.csv'
        products = Product.objects.all()

        if not products.exists():
            self.stdout.write(self.style.WARNING("No products found in the database."))
            return

        field_names = [field.name for field in Product._meta.get_fields() if field.name != 'id']

        with open(output_filename, 'w', newline='', encoding='utf-8') as csvfile:
            writer = csv.DictWriter(csvfile, fieldnames=field_names)
            writer.writeheader()

            for product in products:
                row = {}
                for field in field_names:
                    value = getattr(product, field)
                    if isinstance(value, (dict, list)):
                        row[field] = json.dumps(value, ensure_ascii=False)
                    else:
                        row[field] = value
                writer.writerow(row)

        self.stdout.write(self.style.SUCCESS(f"Successfully exported {products.count()} products to {output_filename}"))