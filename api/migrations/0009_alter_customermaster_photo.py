# Generated by Django 3.2.16 on 2022-11-07 06:33

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0008_alter_mos_sales_options'),
    ]

    operations = [
        migrations.AlterField(
            model_name='customermaster',
            name='photo',
            field=models.ImageField(blank=True, default='', null=True, upload_to='customer_photo'),
        ),
    ]
