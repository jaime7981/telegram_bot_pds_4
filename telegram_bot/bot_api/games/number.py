
from random import randint

from bot_api.models import Chat, NumberGame, Stats

def play_number(text, chat, player):
    # Manage Text Parameters
    newGameIfNotExists(chat)
    if len(text) == 2:
        parameter = text[1]
        number = int(parameter) if parameter.isdigit() else None

        if number != None:
            number_game = NumberGame.objects.filter(player=chat.player).filter(chat_id_int=chat.chat_id)
            if len(number_game) >= 1:
                number_game = number_game[0]
                answer = number_game.answer
                if answer != None:
                    return MainGame(number_game, answer, number, chat)
                else:
                    return 'No answer is set for this game, try the start command'
            else:
                number_game = NumberGame.objects.filter(chat_id_int=chat.chat_id)
                answer = None
                if len(number_game) >= 1:
                    number_game = number_game[0]
                    answer = number_game.answer
                if answer != None:
                    new_game = NumberGame.objects.create(player=player,
                                                         chat=chat,
                                                         answer=answer,
                                                         chat_id_int=chat.chat_id)
                    new_game.save()
                    return MainGame(new_game, answer, number, chat)
                else:
                    return 'No answer is set for this game, try the start command'
        else:
            if parameter == 'start' or parameter == 'reset':
                CreateOrResetNumberGame(chat)
                return 'Answer set and game Ready to be played\nGO!'
            elif parameter == 'info':
                return GetNumberGameParams(chat)
            elif parameter == 'end':
                EndGame(chat)
                return 'Game ended\nrun start or reset for new game'
            else:
                return 'Unkown Number or Game Command'
    elif len(text) == 3:
        parameter = text[1]
        set_num = text[2]
        number = int(set_num) if set_num.isdigit() else None

        if number != None:
            if parameter == 'set_attempts':
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
 -set_attempts num: Sets a "num" times of attempts\n\
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
    number_game = NumberGame.objects.filter(player=chat.player).filter(chat_id_int=chat.chat_id)

    # modified rules to be implemented
    max_answer = 100
    answer = randint(1, max_answer)

    if len(number_game) >= 1:
        number_game = number_game[0]
        answer = randint(1, number_game.rule_highest)

    for chat in chats:
        number_game = NumberGame.objects.filter(player=chat.player).filter(chat_id_int=chat.chat_id)
        if len(number_game) >= 1:
            number_game = number_game[0]
            number_game.game_state = 'W'
            number_game.attempts = 0
            number_game.answer = answer
            number_game.save(update_fields=['game_state',
                                            'attempts',
                                            'answer'])
        else:
            number_game = NumberGame.objects.create(player=chat.player,
                                                    chat=chat,
                                                    answer=answer,
                                                    chat_id_int=chat.chat_id)
            number_game.save()

# Funcion para comenzar o resetear juego
def SetRulesInNumberGame(chat, max_answer=None, max_attempts=None):
    # Todas las instancias de player en chat
    chats = Chat.objects.filter(chat_id=chat.chat_id)

    for chat in chats:
        number_game = NumberGame.objects.filter(player=chat.player).filter(chat_id_int=chat.chat_id)
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
                                                        rule_attempts=max_attempts,
                                                        chat_id_int=chat.chat_id)
            elif max_answer != None:
                number_game = NumberGame.objects.create(player=chat.player,
                                                        chat=chat,
                                                        rule_highest=max_answer,
                                                        chat_id_int=chat.chat_id)
            else:
                number_game = NumberGame.objects.create(player=chat.player,
                                                        chat=chat,
                                                        chat_id_int=chat.chat_id)
            number_game.save()

def newGameIfNotExists(chat):
    new_numberGame = NumberGame.objects.filter(chat_id_int=chat.chat_id)
    if int(len(new_numberGame)) < 1:
        new_game = NumberGame.objects.create(player=chat.player,chat=chat, chat_id_int=chat.chat_id)
        new_game.save()

def GetNumberGameParams(chat):
    # Todas las instancias de player en chat
    chats = Chat.objects.filter(chat_id=chat.chat_id)

    for chat in chats:
        number_game = NumberGame.objects.filter(player=chat.player).filter(chat_id_int=chat.chat_id)
        if len(number_game) >= 1:
            number_game = number_game[0]
            return  f'Attempts: {number_game.rule_attempts}\nMax Number: {number_game.rule_highest}'
        else:
            return 'Error when requesting info params'

def MainGame(number_game, answer, number, chat):
    if number_game.game_state == 'B':
        return f'{number_game.player.user_name} game is blocked, try start or restart'
    elif answer > number:
        flag = UpdateOnWrongAnswer(number_game)
        if flag == True:
            return f'{number_game.player.user_name} answer is higher than {number}\n\
{number_game.attempts} attempts out of {number_game.rule_attempts}'
        else:
            return f'{number_game.player.user_name} is out of attempts'
    elif answer < number:
        flag = UpdateOnWrongAnswer(number_game)
        if flag == True:
            return f'{number_game.player.user_name} answer is lower than {number}\n\
{number_game.attempts} attempts out of {number_game.rule_attempts}'
        else:
            return f'{number_game.player.user_name} is out of attempts'
    elif answer == number:
        UpdateOnCorrectAnswer(number_game, chat)
        return f'{number_game.player.user_name} answer is corrrect!\n\
{number_game.answer} was the answer in {number_game.attempts} attempts'

# True if can continue False if total attempts done
def UpdateOnWrongAnswer(number_game):
    attempts_done = number_game.attempts

    if attempts_done < number_game.rule_attempts:
        number_game.attempts = attempts_done + 1
        number_game.save(update_fields=['attempts'])
        return True
    else:
        return False

def UpdateOnCorrectAnswer(winner_game, chat):
    # Todas las instancias de player en chat
    chats = Chat.objects.filter(chat_id=chat.chat_id)

    stats = Stats.objects.filter(player=winner_game.player,chat_id=chat.chat_id)[0]
    stats.won = stats.won + 1
    stats.save(update_fields=['won'])

    for chat in chats:
        number_game = NumberGame.objects.filter(player=chat.player).filter(chat_id_int=chat.chat_id)
        if len(number_game) >= 1:
            number_game = number_game[0]
            number_game.game_state = 'B'
            number_game.save(update_fields=['game_state'])

            stats = Stats.objects.filter(player=number_game.player,chat_id=chat.chat_id)[0]
            stats.played = stats.played + 1
            stats.lost = stats.played - stats.won
            stats.save(update_fields=['played', 'lost'])
        else:
            number_game = NumberGame.objects.create(player=chat.player,
                                                    chat=chat,
                                                    chat_id_int=chat.chat_id)
            number_game.save()

def EndGame(chat):
    # Todas las instancias de player en chat
    chats = Chat.objects.filter(chat_id=chat.chat_id)

    for chat in chats:
        number_game = NumberGame.objects.filter(player=chat.player).filter(chat_id_int=chat.chat_id)
        if len(number_game) >= 1:
            number_game = number_game[0]
            number_game.game_state = 'B'
            number_game.save(update_fields=['game_state'])

            stats = Stats.objects.filter(player=number_game.player,chat_id=chat.chat_id)[0]
            stats.played = stats.played + 1
            stats.lost = stats.played - stats.won
            stats.save(update_fields=['played', 'lost'])
        else:
            number_game = NumberGame.objects.create(player=chat.player,
                                                    chat=chat,
                                                    game_state = 'B',
                                                    chat_id_int=chat.chat_id)
            number_game.save()
