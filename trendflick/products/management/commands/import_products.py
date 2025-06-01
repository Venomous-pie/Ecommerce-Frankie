import csv
from django.core.management.base import BaseCommand
from products.models import Product, Category
from django.core.files.base import ContentFile
from django.conf import settings
import os

class Command(BaseCommand):
    help = 'Import products from clothing_products.csv'

    def handle(self, *args, **options):
        # Use the correct path to the CSV file (project root, one level up from trendflick)
        csv_path = os.path.abspath(os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), '..', 'clothing_products.csv'))
        if not os.path.exists(csv_path):
            self.stdout.write(self.style.ERROR(f"CSV file not found at: {csv_path}"))
            return
        with open(csv_path, newline='', encoding='utf-8') as csvfile:
            reader = csv.DictReader(csvfile)
            for row in reader:
                # Get or create category
                category, _ = Category.objects.get_or_create(name=row['category'], defaults={'slug': row['category'].lower()})
                # Prepare image path to include category folder
                image_path = os.path.join('products', category.name, os.path.basename(row['image_url'].replace('\\', '/').split('/')[-1]))
                # Create product
                product, created = Product.objects.get_or_create(
                    name=row['name'],
                    description=row['description'],
                    price=row['price'],
                    category=category,
                    defaults={
                        'featured': row['featured'].strip().lower() == 'yes',
                        'image': image_path,
                    }
                )
                if created:
                    self.stdout.write(self.style.SUCCESS(f"Imported: {product.name}"))
                else:
                    self.stdout.write(self.style.WARNING(f"Skipped (exists): {product.name}"))
        self.stdout.write(self.style.SUCCESS('Import complete.'))
