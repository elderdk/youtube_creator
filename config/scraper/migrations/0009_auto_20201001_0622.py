# Generated by Django 3.1.1 on 2020-10-01 06:22

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('scraper', '0008_submission_dub_len'),
    ]

    operations = [
        migrations.RenameField(
            model_name='submission',
            old_name='dub_len',
            new_name='sub_len',
        ),
    ]
