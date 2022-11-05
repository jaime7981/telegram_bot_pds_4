from cmath import log
from random import randint
from django.shortcuts import render
from django.http import HttpResponse, HttpResponseBadRequest, JsonResponse

from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator

from bot_api.models import Player, Chat, Stats, NumberGame

import logging, requests, json
logger = logging.getLogger('django')

bot_commands = ['/start', '/games', '/stats']
game_list = ['/number', '/trivia', '/custom']

# Create your views here.
def test_page(request):
    context = {}
    return(render(request, 'test.html', context=context))

def root(request):
    return HttpResponse(status=200)

@csrf_exempt
def webhook(request):
    #logger.info(request)
    #logger.info(request.headers)
    #logger.info(request.body)

    if request.method == 'POST':
        request_data = json.loads(request.body)
        message_to_send = ''

        logger.info(request_data)
        request_json = formatInfo(request_data)

        player, chat = getPlayerAndChatOrCreate(request_json)
        logger.info(player.user_name)
        logger.info(chat.chat_title)

        text = request_json.get('message_text').split()
        if len(text) >= 1:
            command = text[0]

            # Commands for info
            if command in bot_commands:
                if command == '/start':
                    message_to_send = 'Starting Bot'
                elif command == '/games':
                    message_to_send = '\n'.join(game_list)
                elif command == '/stats':
                    message_to_send = 'To Be Imlpemented: user stats'
                else:
                    message_to_send = 'Command Not Implemented'
            
            # Commands for games
            elif command in game_list:
                if command == '/number':
                    message_to_send = 'Number Game'
                    message_to_send = play_number(text, player, chat)
                else:
                    message_to_send = 'Game Not Implemented'
            else:
                message_to_send = str('Unkown command, try:\n' + '\n'.join(bot_commands))
        
        chat_id = int(request_json.get('chat_id'))
        sendMessage(chat_id, text=message_to_send)
        return JsonResponse({'success':'post method working'},status=200)
    elif request.method == 'GET':
        return JsonResponse({'success':'get method working'},status=200)
    else:
        return HttpResponseBadRequest()
        
def sendMessage(chat_id, text='bot response'):
    url = f'https://api.telegram.org/bot5668389701:AAHWwdNxz6fbX3lh4RfhSyuZvnHpOFHT9IQ/sendMessage'
    data = {'chat_id':int(chat_id),
            'text':text}
    request = requests.post(url, json=data)
    return request


def play_number(text, player, chat):
    logger.info(text)

    # Manage Text Parameters
    if len(text) == 2:
        parameter = text[1]
        number = int(parameter) if parameter.isdigit() else None

        if number != None:
            return str(number)
        else:
            if parameter == 'start' or parameter == 'reset':
                CreateOrResetNumberGame(chat)
                return 'Answer set and game Ready to be played\nGO!'
            elif parameter == 'info':
                return 'TBI: Info'
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
                SetRulesInNumberGame(max_attempts=number)
                return 'Max attempts setted to ' + str(number)
            elif parameter == 'set_max':
                SetRulesInNumberGame(max_answer=number)
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
        if len(number_game) == 1:
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
        if len(number_game) == 1:
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

def formatInfo(json_request):
    formated_json = {}
    message = json_request.get('message')

    if message is not None:
        #Skipping checks
        formated_json['chat_id'] = message.get('chat').get('id')
        formated_json['chat_type'] = message.get('chat').get('type')

        if formated_json['chat_type'] == 'group':
            formated_json['chat_title'] = message.get('chat').get('title')
        else:
            formated_json['chat_title'] = message.get('chat').get('first_name') + ' ' + message.get('chat').get('last_name')

        formated_json['sender_id'] = message.get('from').get('id')
        formated_json['sender_name'] = message.get('from').get('first_name') + ' ' + message.get('from').get('last_name')
        
        formated_json['message_id'] = message.get('id')
        formated_json['message_date'] = message.get('date')
        formated_json['message_text'] = message.get('text')
    return formated_json

def getPlayerAndChatOrCreate(json_request):
    player = Player.objects.filter(user_id = json_request.get('sender_id'))
    if len(player) == 1:
        player = player[0]
        chat = Chat.objects.filter(chat_id = json_request.get('chat_id')).filter(player=player)
        if len(chat) == 1:
            chat = chat[0]
        else:
            chat = Chat.objects.create(player=player,
                                       chat_id=json_request.get('chat_id'),
                                       chat_type=json_request.get('chat_type'),
                                       chat_title=json_request.get('chat_title'))
            chat.save()
    else:
        player = Player.objects.create(user_id=json_request.get('sender_id'),
                                       user_name=json_request.get('sender_name'))
        player.save()
        stats = Stats.objects.create(player=player)
        stats.save()
        chat = Chat.objects.create(player=player,
                                       chat_id=json_request.get('chat_id'),
                                       chat_type=json_request.get('chat_type'),
                                       chat_title=json_request.get('chat_title'))
        chat.save()
    return (player, chat)
