# Generated by Django 4.2.8 on 2024-01-10 22:34

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0002_user_time_zone'),
    ]

    operations = [
        migrations.AddField(
            model_name='user',
            name='is_user',
            field=models.BooleanField(default=False),
        ),
    ]