# Generated by Django 4.1 on 2022-11-12 19:30

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Chat',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('chat_id', models.BigIntegerField()),
                ('chat_type', models.CharField(max_length=100)),
                ('chat_title', models.CharField(max_length=100)),
            ],
        ),
        migrations.CreateModel(
            name='Player',
            fields=[
                ('user_id', models.BigIntegerField(primary_key=True, serialize=False)),
                ('user_name', models.CharField(max_length=100)),
            ],
        ),
        migrations.CreateModel(
            name='Question',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('question', models.CharField(max_length=300)),
                ('ans1', models.CharField(max_length=100)),
                ('ans2', models.CharField(max_length=100)),
                ('ans3', models.CharField(max_length=100)),
                ('correct', models.CharField(max_length=100)),
            ],
        ),
        migrations.CreateModel(
            name='TriviaGame',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('game_state', models.CharField(choices=[('W', 'Write'), ('B', 'Block')], default='W', max_length=1)),
                ('game_mode', models.CharField(choices=[('F', 'First'), ('T', 'Time')], default='F', max_length=1)),
                ('num_of_questions', models.IntegerField(default='1')),
                ('answered_questions', models.IntegerField(default='0')),
                ('question', models.ForeignKey(default=None, on_delete=django.db.models.deletion.CASCADE, to='bot_api.question')),
            ],
        ),
        migrations.CreateModel(
            name='TriviaGameInstance',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('points', models.IntegerField(default=0)),
                ('chat', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='bot_api.chat')),
                ('player', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='bot_api.player')),
                ('trivia', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='bot_api.triviagame')),
            ],
        ),
        migrations.CreateModel(
            name='Stats',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('played', models.IntegerField(blank=True, default=0, null=True)),
                ('won', models.IntegerField(blank=True, default=0, null=True)),
                ('lost', models.IntegerField(blank=True, default=0, null=True)),
                ('player', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='bot_api.player')),
            ],
        ),
        migrations.CreateModel(
            name='Poll',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('poll_id', models.BigIntegerField()),
                ('vote_numbers', models.IntegerField(default='0')),
                ('closed', models.BooleanField(default=False)),
                ('correct_option', models.IntegerField(default=0)),
                ('chat', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='bot_api.chat')),
                ('question', models.ForeignKey(default=None, on_delete=django.db.models.deletion.CASCADE, to='bot_api.question')),
            ],
        ),
        migrations.CreateModel(
            name='NumberGame',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('game_state', models.CharField(choices=[('W', 'Write'), ('B', 'Block')], default='W', max_length=1)),
                ('attempts', models.IntegerField(blank=True, default=0, null=True)),
                ('rule_attempts', models.IntegerField(blank=True, default=5, null=True)),
                ('rule_highest', models.IntegerField(blank=True, default=100, null=True)),
                ('answer', models.IntegerField(blank=True, default=None, null=True)),
                ('chat', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='bot_api.chat')),
                ('player', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='bot_api.player')),
            ],
        ),
        migrations.AddField(
            model_name='chat',
            name='player',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='bot_api.player'),
        ),
    ]
