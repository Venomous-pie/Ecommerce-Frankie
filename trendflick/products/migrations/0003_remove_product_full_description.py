# Generated by Django 5.1.7 on 2025-05-28 14:40

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('products', '0002_alter_product_category'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='product',
            name='full_description',
        ),
    ]
