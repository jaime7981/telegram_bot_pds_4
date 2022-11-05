from django.db import models

# Create your models here.
class Player(models.Model):
    user_id = models.BigIntegerField(primary_key = True)
    user_name = models.CharField(max_length=100)

class Chat(models.Model):
    player = models.ForeignKey(Player, on_delete=models.CASCADE)
    chat_id = models.BigIntegerField(primary_key = True)
    chat_type = models.CharField(max_length=100)
    chat_title = models.CharField(max_length=100)

class Stats(models.Model):
    player = models.ForeignKey(Player, on_delete=models.CASCADE)
    played = models.IntegerField(default=0, null=True, blank=True)
    won = models.IntegerField(default=0, null=True, blank=True)
    lost = models.IntegerField(default=0, null=True, blank=True)

class NumberGame(models.Model):
    GAME_STATES = (
        ('W', 'Write'),
        ('B', 'Block')
    )

    player = models.ForeignKey(Player, on_delete=models.CASCADE)
    chat = models.ForeignKey(Chat, on_delete=models.CASCADE)
    game_state = models.CharField(max_length=1, choices=GAME_STATES)
    attempts = models.IntegerField(default=0, null=True, blank=True)
    response = models.IntegerField(default=None, null=True, blank=True)
    won = models.BooleanField(null=True, blank=True)
