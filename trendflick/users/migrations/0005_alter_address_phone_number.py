# Generated by Django 5.1.7 on 2025-06-01 07:13

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0004_alter_passwordresetcode_code'),
    ]

    operations = [
        migrations.AlterField(
            model_name='address',
            name='phone_number',
            field=models.CharField(max_length=20, null=True),
        ),
    ]
