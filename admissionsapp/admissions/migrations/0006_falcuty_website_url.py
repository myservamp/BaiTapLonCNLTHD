# Generated by Django 4.2 on 2023-04-25 16:20

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('admissions', '0005_falcuty_livestream_info_slider_questions_major'),
    ]

    operations = [
        migrations.AddField(
            model_name='falcuty',
            name='website_url',
            field=models.URLField(null=True),
        ),
    ]