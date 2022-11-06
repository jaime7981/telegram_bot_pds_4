from cmath import log
from random import randint
from django.shortcuts import render
from django.http import HttpResponse, HttpResponseBadRequest, JsonResponse

from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator

from bot_api.models import Player, Chat, Stats, NumberGame

import logging, requests, json

from telegram_bot.bot_api.games.number import play_number
logger = logging.getLogger('django')

bot_commands = ['/start', '/games', '/stats', '/welcome']
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
        if player == None or chat == None:
            chat_id = int(request_json.get('chat_id'))
            sendMessage(chat_id, text='Error getting the player or the chat')
            return JsonResponse({'success':'post method working'},status=200)
        
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
                elif command == '/welcome':
                    message_to_send = f'Hello {player.user_name}!\nWelcome to {chat.chat_title}'
                else:
                    message_to_send = 'Command Not Implemented'
            
            # Commands for games
            elif command in game_list:
                if command == '/number':
                    message_to_send = 'Number Game'
                    message_to_send = play_number(text, chat)
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

def formatInfo(json_request):
    formated_json = {}
    message = json_request.get('message')
    if message == None:
        message = json_request.get('edited_message')

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
        formated_json['message_text'] = message.get('text', '/welcome')
    return formated_json

def getPlayerAndChatOrCreate(json_request):
    user_id = json_request.get('sender_id')
    if user_id != None:
        player = Player.objects.filter(user_id = json_request.get('sender_id'))
    else:
        return None, None
    
    if len(player) >= 1:
        player = player[0]
        chat = Chat.objects.filter(chat_id = json_request.get('chat_id')).filter(player=player)
        if len(chat) >= 1:
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
