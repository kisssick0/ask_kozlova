# Generated by Django 4.0 on 2023-12-25 13:28

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('base', '0007_alter_answer_question_alter_answer_user_and_more'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='profile',
            name='nickname',
        ),
    ]