from bot_api.models import Chat, Stats, Hangman, HangmanGameInstance, Player

import requests, logging

logger = logging.getLogger('django')

def play_hangman(text, chat, player):
    # Manage Text Parameters
    newGameIfNotExists(chat)
    newHangmanInstance(chat, player)
        
    if len(text) == 2:
        if text[1] == 'start':
            return StartOrResetGame(chat)
        elif text[1] == 'info':
            return GameInfo(chat=chat)
        return 'Two parameters not implemented'
    elif len(text) == 3:
        if text[1] == 'set_lives':
            return UpdateGameParams(chat, text[2], text[1])
        return 'Three parameters not implemented'
    elif len(text) == 1:
        return 'HANGMAN GAME\n\
Objective: Guess the word\n\
Commands:\n\
 -start or reset: restarts the game\n\
 -info: Returns the actual parameters of the game\n\
 -set_lives: Sets number of lives\n\
 -end: Finishes the game'
    else:
        return 'Too many parameters'

def newGameIfNotExists(chat):
    new_game = Hangman.objects.filter(chat=chat.chat_id)
    if len(new_game) < 1:
        new_game = Hangman.objects.create(game_state="W",chat=chat.chat_id)
        new_game.save()

def newHangmanInstance(chat, player):
    trivia_intance = HangmanGameInstance.objects.filter(chat=chat.chat_id).filter(player=player)
    if len(trivia_intance) < 1:
        new_hangman = Hangman.objects.filter(chat=chat.chat_id)
        if len(new_hangman) >= 1:
            new_hangman = new_hangman[0]
            new_instance = HangmanGameInstance.objects.create(player=player,
                                                              chat=chat.chat_id,
                                                              hangman=new_hangman)
            new_instance.save()

def CheckIfGameEndedOrClosed(chat):
    game = Hangman.objects.filter(chat=chat.chat_id)
    if len(game) >= 1:
        game = game[0]
        if game.game_state == "B" or int(game.lives) <= 0:
            game.game_state = "B"
            game.save(update_fields=['game_state'])
            return False
        else:
            return True
    else:
        newGameIfNotExists(chat)
        return False

def UpdateGameParams(chat, value, command):
    instance = HangmanGameInstance.objects.filter(chat=chat.chat_id)
    if len(instance) >= 1:
        games = Hangman.objects.filter(id=instance[0].hangman.id)
        game = games[0]
        if command == "set_lives":
            if is_integer(value) and int(value) >= 1:
                game.num_of_questions = value
                game.save(update_fields=['lives'])
                return f"Number of lives successfully updated to {value}"
    return "Number of games could not be changed"

def GameInfo(chat):
    instance = HangmanGameInstance.objects.filter(chat=chat.chat_id)
    if len(instance) >= 1:
        game = Hangman.objects.filter(id=instance[0].trivia.id)
        if len(game) >= 1:
            texto = F"Number of lives: {game[0].lives}"
            return texto
    return "No game was found"

def StartOrResetGame(chat):
    word_from_api = GetRandomWord()
    word_progress = WordToRegexStart(word_from_api)
    hangman = Hangman.objects.filter(chat=chat.chat_id)[0]
    
    if len(hangman) >= 1:
        hangman = hangman[0]
        hangman.game_state = "W"
        hangman.word_solution = word_from_api
        hangman.word_progress = word_progress
        hangman.save(update_fields=['game_state',
                                    'word_solution',
                                    'word_progress'])
        return f'Start guessing {word_progress}'
    return 'Error while starting the game'

def GetRandomWord():
    url = 'https://api.api-ninjas.com/v1/randomword'
    response = requests.get(url, headers={'X-Api-Key': 'YOUR_API_KEY'})
    if response.status_code == requests.codes.ok:
        return response.json().get('word', 'false')
    else:
        return 'false'

def WordToRegexStart(word):
    final_string = ''
    for leter in word:
        final_string += '_ '
    final_string.pop()
    return final_string

def is_integer(n):
    try:
        float(n)
    except ValueError:
        return False
    else:
        return float(n).is_integer()