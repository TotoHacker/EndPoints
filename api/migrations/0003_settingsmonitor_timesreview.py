# Generated by Django 5.1.2 on 2024-11-19 18:15

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0002_settingsmonitor'),
    ]

    operations = [
        migrations.AddField(
            model_name='settingsmonitor',
            name='timesReview',
            field=models.IntegerField(default=1),
            preserve_default=False,
        ),
    ]
