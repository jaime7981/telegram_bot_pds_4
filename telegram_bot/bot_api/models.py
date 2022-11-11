from django.db import models

# Create your models here.
class Player(models.Model):
    user_id = models.BigIntegerField(primary_key = True)
    user_name = models.CharField(max_length=100)

class Chat(models.Model):
    player = models.ForeignKey(Player, on_delete=models.CASCADE)
    chat_id = models.BigIntegerField()
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
    game_state = models.CharField(default='W', max_length=1, choices=GAME_STATES)
    attempts = models.IntegerField(default=0, null=True, blank=True)

    rule_attempts = models.IntegerField(default=5, null=True, blank=True)
    rule_highest = models.IntegerField(default=100, null=True, blank=True)
    answer = models.IntegerField(default=None, null=True, blank=True)


class Question(models.Model):
    question = models.CharField(max_length=300)
    ans1 = models.CharField(max_length=100)
    ans2 = models.CharField(max_length=100)
    ans3 = models.CharField(max_length=100)
    #ans4 = models.CharField(default=None, max_length=100)
    correct = models.CharField(max_length=100)

class TriviaGame(models.Model):
    GAME_STATES = (
        ('W', 'Write'),
        ('B', 'Block')
    )

    GAME_MODES = (
        ('F', 'First'),
        ('T', 'Time')
    )

    question = models.ForeignKey(Question, default=None)

    game_state = models.CharField(default='W', max_length=1, choices=GAME_STATES)
    game_mode = models.CharField(default='F', max_length=1, choices=GAME_MODES)
    num_of_questions = models.IntegerField(default='1')

class TriviaGameInstance(models.Model):
    player = models.ForeignKey(Player, on_delete=models.CASCADE)
    chat = models.ForeignKey(Chat, on_delete=models.CASCADE)
    trivia = models.ForeignKey(TriviaGame, on_delete=models.CASCADE)

    points = models.IntegerField(default=0)
