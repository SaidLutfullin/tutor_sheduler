# Generated by Django 4.2.8 on 2024-01-10 22:37

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0004_rename_is_user_user_is_teacher'),
    ]

    operations = [
        migrations.RenameField(
            model_name='user',
            old_name='is_teacher',
            new_name='is_tutor',
        ),
    ]