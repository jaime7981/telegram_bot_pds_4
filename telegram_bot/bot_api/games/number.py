
from random import randint

from bot_api.models import Chat, NumberGame, Stats

def play_number(text, chat):
    # Manage Text Parameters
    if len(text) == 2:
        parameter = text[1]
        number = int(parameter) if parameter.isdigit() else None

        if number != None:
            number_game = NumberGame.objects.filter(player=chat.player).filter(chat=chat)
            answer = number_game.answer
            if answer != None:
                MainGame(number_game, answer, number, chat)
            else:
                return 'No answer is set for this game, try the start command'
        else:
            if parameter == 'start' or parameter == 'reset':
                CreateOrResetNumberGame(chat)
                return 'Answer set and game Ready to be played\nGO!'
            elif parameter == 'info':
                return GetNumberGameParams(chat)
            elif parameter == 'end':
                return 'TBI: Ending game'
            else:
                return 'Unkown Number or Game Command'
    elif len(text) == 3:
        parameter = text[1]
        set_num = text[2]
        number = int(set_num) if set_num.isdigit() else None

        if number != None:
            if parameter == 'set_attemps':
                SetRulesInNumberGame(chat, max_attempts=number)
                return 'Max attempts setted to ' + str(number)
            elif parameter == 'set_max':
                SetRulesInNumberGame(chat, max_answer=number)
                return 'Max random number setted to ' + str(number)
        else:
            return 'Bad arguments for seting game params'
    elif len(text) == 1:
        return 'NUMBER GAME\n\
                Objective: Guess the number\n\
                Commands:\n\
                 -start or reset: restarts the game\n\
                 -set_attemps num: Sets a "num" times of attempst\n\
                 -set_max num: Sets a limit of "num" for the random number\n\
                 -info: Returns the actual parameters of the game\n\
                 -end: Finishes the game\n\
                 -num: Your guess number (must be an int)'
    else:
        return 'Too many parameters'

# Funcion para comenzar o resetear juego
def CreateOrResetNumberGame(chat):
    # Todas las instancias de player en chat
    chats = Chat.objects.filter(chat_id=chat.chat_id)

    # modified rules to be implemented
    max_answer = 100
    max_attemps = 5

    answer = randint(1, max_answer)

    for chat in chats:
        number_game = NumberGame.objects.filter(player=chat.player).filter(chat=chat)
        if len(number_game) >= 1:
            number_game = number_game[0]
            number_game.game_state = 'W'
            number_game.attempts = 0
            number_game.response = None
            number_game.won = False
            number_game.rule_atemps = max_attemps
            number_game.answer = answer
            number_game.save(update_fields=['game_state',
                                            'attempts',
                                            'response',
                                            'won',
                                            'rule_attempts',
                                            'answer'])
        else:
            number_game = NumberGame.objects.create(player=chat.player,
                                                    chat=chat,
                                                    rule_attempts=max_attemps,
                                                    answer=answer)
            number_game.save()

# Funcion para comenzar o resetear juego
def SetRulesInNumberGame(chat, max_answer=None, max_attempts=None):
    # Todas las instancias de player en chat
    chats = Chat.objects.filter(chat_id=chat.chat_id)

    for chat in chats:
        number_game = NumberGame.objects.filter(player=chat.player).filter(chat=chat)
        if len(number_game) >= 1:
            number_game = number_game[0]
            if max_attempts != None:
                number_game.rule_attempts = max_attempts
                number_game.save(update_fields=['rule_attempts'])
            elif max_answer != None:
                number_game.rule_highest = max_answer
                number_game.save(update_fields=['rule_highest'])
        else:
            if max_attempts != None:
                number_game = NumberGame.objects.create(player=chat.player,
                                                        chat=chat,
                                                        rule_attempts=max_attempts)
            elif max_answer != None:
                number_game = NumberGame.objects.create(player=chat.player,
                                                        chat=chat,
                                                        rule_highest=max_answer)
            else:
                number_game = NumberGame.objects.create(player=chat.player,
                                                        chat=chat)
            number_game.save()

def GetNumberGameParams(chat):
    # Todas las instancias de player en chat
    chats = Chat.objects.filter(chat_id=chat.chat_id)

    for chat in chats:
        number_game = NumberGame.objects.filter(player=chat.player).filter(chat=chat)
        if len(number_game) >= 1:
            number_game = number_game[0]
            return  f'Attempts: {number_game.rule_attempts}\nMax Number: {number_game.rule_highest}'
        else:
            return 'Error when requesting info params'

def MainGame(number_game, answer, number, chat):
    if answer > number:
        flag = UpdateOnWrongAnswer(number_game)
        if flag == True:
            return f'{number_game.player.user_name} answer is higher than {number}\n\
                {number_game.attemps} attempts out of {number_game.rule_attempts}'
        else:
            return f'{number_game.player.user_name} is out of attempts'
    elif answer < number:
        flag = UpdateOnWrongAnswer(number_game)
        if flag == True:
            return f'{number_game.player.user_name} answer is lower than {number}\n\
                {number_game.attemps} attempts out of {number_game.rule_attempts}'
        else:
            return f'{number_game.player.user_name} is out of attempts'
    elif answer == number:
        UpdateOnCorrectAnswer(number_game, chat)
        return f'{number_game.player.user_name} answer is corrrect!\n\
            {number_game.answer} was the answer in {number_game.attempts}'

# True if can continue False if total attempts done
def UpdateOnWrongAnswer(number_game):
    attempts_done = number_game.attempts

    if attempts_done >= number_game.rule_attempts:
        number_game.game_state = 'B'
        number_game.save(update_fields=['game_state'])
        return False
    else:
        number_game.attempts = attempts_done + 1
        return True

def UpdateOnCorrectAnswer(winner_game, chat):
    # Todas las instancias de player en chat
    chats = Chat.objects.filter(chat_id=chat.chat_id)

    # modified rules to be implemented
    max_answer = winner_game.rule_highest
    max_attemps = winner_game.rule_attempts

    answer = randint(1, max_answer)

    stats = Stats.objects.get(player=winner_game.player)
    stats.win = stats.win + 1

    for chat in chats:
        number_game = NumberGame.objects.filter(player=chat.player).filter(chat=chat)
        if len(number_game) >= 1:
            number_game = number_game[0]
            number_game.game_state = 'B'
            number_game.attempts = 0
            number_game.response = None
            number_game.won = False
            number_game.rule_atemps = max_attemps
            number_game.answer = answer
            number_game.save(update_fields=['game_state',
                                            'attempts',
                                            'response',
                                            'won',
                                            'rule_attempts',
                                            'answer'])
            stats = Stats.objects.get(player=number_game.player)
            stats.played = stats.played + 1
            stats.lost = stats.played - stats.win

        else:
            number_game = NumberGame.objects.create(player=chat.player,
                                                    chat=chat,
                                                    rule_attempts=max_attemps,
                                                    answer=answer)
            number_game.save()
    
    winner_game.won = True
    winner_game.save()
