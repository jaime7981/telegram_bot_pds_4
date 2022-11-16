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
        elif len(text[1]) == 1:
            return OneLetter(text[1], chat, player)
        else:
            return GuessWord(text[1], chat, player)
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

def OneLetter(letter, chat, player):
    if CheckIfGameEndedOrClosed(chat) == False:
        return f'{player.user_name} out of lives or game is closed'
    
    game = Hangman.objects.filter(chat=chat.chat_id)
    if len(game) >= 1:
        game = game[0]

        if letter in game.word_solution:
            new_progress = LetterToRegexProgress(game.word_solution, 
                                                 game.word_progress, 
                                                 letter)
            game.word_progress = new_progress
            game.save(update_fields=['word_progress'])
            return f'Letter {letter} is contained in the word\n +1 point for letter\n {new_progress}'
        else:
            game.lives_counter = game.lives_counter - 1
            game.save(update_fields=['lives_counter'])
            return f'{player.user_name} bad Guess {game.lives_counter} lives left\n {game.word_progress}'
    return f'letter {letter}'

def GuessWord(word, chat, player):
    if CheckIfGameEndedOrClosed(chat) == False:
        return f'{player.user_name} out of lives or game is closed'
    
    game = Hangman.objects.filter(chat=chat.chat_id)
    if len(game) >= 1:
        game = game[0]
        if game.word_solution == word:
            game.game_state = 'B'
            game.save(update_fields=['game_state'])
            return f'{player.user_name} you guess the word! {word}\n +5 points for completing the answer'
        else:
            game.lives_counter = game.lives_counter - 1
            game.save(update_fields=['lives_counter'])
            return f'{player.user_name} bad Guess {game.lives_counter} lives left\n {game.word_progress}'

    return f'trying hard guess {word}'

def newGameIfNotExists(chat):
    new_game = Hangman.objects.filter(chat=chat.chat_id)
    word_from_api = GetRandomWord()
    word_progress = WordToRegexStart(word_from_api)
    if len(new_game) < 1:
        new_game = Hangman.objects.create(game_state="W",
                                          word_solution=word_from_api,
                                          word_progress=word_progress,
                                          chat=chat.chat_id)
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
        if game.game_state == "B" or int(game.lives_counter) <= 0:
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
                game.lives = value
                game.lives_counter = value
                game.save(update_fields=['lives',
                                         'lives_counter'])
                return f"Number of lives successfully updated to {value}"
    return "Number of games could not be changed"

def GameInfo(chat):
    instance = HangmanGameInstance.objects.filter(chat=chat.chat_id)
    if len(instance) >= 1:
        game = Hangman.objects.filter(id=instance[0].hangman.id)
        if len(game) >= 1:
            texto = F"Number of lives: {game[0].lives}"
            return texto
    return "No game was found"

def StartOrResetGame(chat):
    word_from_api = GetRandomWord()
    logger.info(f'Answer: {word_from_api}')
    word_progress = WordToRegexStart(word_from_api)
    hangman = Hangman.objects.filter(chat=chat.chat_id)
    
    if len(hangman) >= 1:
        hangman = hangman[0]
        hangman.game_state = "W"
        hangman.word_solution = word_from_api
        hangman.word_progress = word_progress
        hangman.lives_counter = hangman.lives
        hangman.save(update_fields=['game_state',
                                    'word_solution',
                                    'word_progress',
                                    'lives_counter'])
        return f'Start guessing\n {word_progress}'
    return 'Error while starting the game'

def GetRandomWord():
    url = 'https://api.api-ninjas.com/v1/randomword'
    response = requests.get(url, headers={'X-Api-Key': 'YOUR_API_KEY'})
    if response.status_code == requests.codes.ok:
        return response.json().get('word', 'false').lower()
    else:
        return 'false'

def WordToRegexStart(word):
    final_string = ''
    n = len(word)
    for position in range(n):
        if position == n - 1:
            final_string += '_'
        else:
            final_string += '_ '
    return final_string

def LetterToRegexProgress(solution, progress, letter):
    progress_list = progress.split()
    final_string = ''
    points = 0

    for progress_letter, solution_letter in zip(progress_list,solution):
        if progress_letter != '_':
            final_string += f'{progress_letter} '
        else:
            if solution_letter == letter:
                final_string += f'{letter} '
                points += 1
            else:
                final_string += '_ '

    return final_string

def is_integer(n):
    try:
        float(n)
    except ValueError:
        return False
    else:
        return float(n).is_integer()