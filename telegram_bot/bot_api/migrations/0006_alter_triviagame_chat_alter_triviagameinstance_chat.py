# Generated by Django 4.1 on 2022-11-13 21:37

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('bot_api', '0005_triviagame_chat_alter_triviagameinstance_trivia'),
    ]

    operations = [
        migrations.AlterField(
            model_name='triviagame',
            name='chat',
            field=models.IntegerField(),
        ),
        migrations.AlterField(
            model_name='triviagameinstance',
            name='chat',
            field=models.IntegerField(),
        ),
    ]
