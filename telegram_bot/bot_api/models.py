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
    chat_id = models.IntegerField(null=True, default=None)

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
    question = models.CharField(max_length=500)
    ans1 = models.CharField(max_length=100)
    ans2 = models.CharField(max_length=100)
    ans3 = models.CharField(max_length=100)
    #ans4 = models.CharField(default=None, max_length=100)
    correct = models.CharField(max_length=100)

class Poll(models.Model):
    chat = models.ForeignKey(Chat, on_delete=models.CASCADE)
    question = models.ForeignKey(Question, on_delete=models.CASCADE, default=None)
    poll_id = models.BigIntegerField()
    vote_numbers = models.IntegerField(default='0')
    closed = models.BooleanField(default=False)
    correct_option = models.IntegerField(default=0)

class TriviaGame(models.Model):
    GAME_STATES = (
        ('W', 'Write'),
        ('B', 'Block')
    )

    GAME_MODES = (
        ('F', 'First'),
        ('T', 'Time')
    )
    
    chat = models.IntegerField(null=True, default=None)
    question = models.ForeignKey(Question, on_delete=models.CASCADE, default=None, null=True)
    poll = models.ForeignKey(Poll, on_delete=models.CASCADE, default=None, null=True)
    game_state = models.CharField(default='W', max_length=1, choices=GAME_STATES)
    game_mode = models.CharField(default='F', max_length=1, choices=GAME_MODES)
    num_of_questions = models.IntegerField(default='1')
    answered_questions = models.IntegerField(default='0')

class TriviaGameInstance(models.Model):
    player = models.ForeignKey(Player, on_delete=models.CASCADE)
    chat = models.IntegerField(null=True, default=None)
    trivia = models.ForeignKey(TriviaGame, on_delete=models.CASCADE, default=None, null=True)

    points = models.IntegerField(default=0)

class Hangman(models.Model):
    GAME_STATES = (
        ('W', 'Write'),
        ('B', 'Block')
    )

    chat = models.BigIntegerField(null=True, default=None)
    game_state = models.CharField(default='W', max_length=1, choices=GAME_STATES)

    word_solution = models.CharField(default=None, max_length=100)
    word_progress = models.CharField(default=None, max_length=100)

    lives = models.IntegerField(default=10)
    lives_counter = models.IntegerField(default=10)

class HangmanGameInstance(models.Model):
    chat = models.BigIntegerField(null=True, default=None)
    player = models.ForeignKey(Player, on_delete=models.CASCADE)
    hangman = models.ForeignKey(Hangman, on_delete=models.CASCADE, default=None, null=True)

    points = models.IntegerField(default=0)

