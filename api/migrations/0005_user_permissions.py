# Generated by Django 5.1.2 on 2024-11-21 18:08

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0004_remove_settingsmonitor_hour_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='user',
            name='Permissions',
            field=models.IntegerField(default=1),
            preserve_default=False,
        ),
    ]
