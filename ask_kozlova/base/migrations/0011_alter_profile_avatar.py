# Generated by Django 4.0 on 2023-12-27 01:27

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('base', '0010_profile_avatar'),
    ]

    operations = [
        migrations.AlterField(
            model_name='profile',
            name='avatar',
            field=models.ImageField(blank=True, default='avatar.jpg', null=True, upload_to='uploads'),
        ),
    ]