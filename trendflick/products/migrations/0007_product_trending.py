# Generated by Django 5.2.1 on 2025-06-01 07:52

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('products', '0006_product_featured'),
    ]

    operations = [
        migrations.AddField(
            model_name='product',
            name='trending',
            field=models.BooleanField(default=False),
        ),
    ]
