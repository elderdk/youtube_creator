# Generated by Django 3.1.1 on 2020-10-03 02:54

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('scraper', '0010_auto_20201001_0629'),
    ]

    operations = [
        migrations.AddField(
            model_name='submission',
            name='sub_bg_image',
            field=models.CharField(blank=True, max_length=300),
        ),
    ]
