from cmath import log
from random import randint
from django.shortcuts import render
from django.http import HttpResponse, HttpResponseBadRequest, JsonResponse

from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator

from bot_api.models import Player, Chat, Stats, NumberGame, Poll

import logging, requests, json

from bot_api.games.number import play_number
from bot_api.games.trivia import play_trivia, PollWinOrResponseLimit, checkPlayerAnswer
from bot_api.games.hangman import play_hangman

logger = logging.getLogger('django')

bot_commands = ['/start', '/games', '/stats', '/welcome']
game_list = ['/number', '/trivia', '/hangman']

# Create your views here.
def test_page(request):
    context = {}
    return(render(request, 'test.html', context=context))

def root(request):
    all_stats = Stats.objects.all().order_by('won')

    groups_id = []

    for stat in all_stats:
        if stat.chat_id not in groups_id:
            groups_id.append(stat.chat_id)

    context = {'all_stats':all_stats, 'groups_id': groups_id}
    return(render(request, 'stats.html', context=context))

def show_group_stats(request):
    if request.method == 'POST':
        request_data = json.loads(request.body)
        group_id = request_data.get('group_id', 0)
        all_stats = Stats.objects.filter(group_id=group_id).order_by('won')
        context = {'all_stats':all_stats, 'group_id': group_id}
        return(render(request, 'group_stats.html', context=context))
    else:
        return HttpResponseBadRequest()

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
        
        if request_json.get('chat_type') == 'poll':
            poll_id = request_json.get('poll_id')
            option_id = request_json.get('option_ids')
            sender_id = request_json.get('sender_id')
            
            try:
                poll = Poll.objects.get(poll_id=poll_id)
            except:
                return JsonResponse({'error':'model not found'},status=200)
            checkPlayerAnswer(poll, option_id, sender_id)
            PollWinOrResponseLimit(request_json, poll)
            return JsonResponse({'success':'post method working'},status=200)
    
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
                    message_to_send = get_stats(text, player, chat)
                    #message_to_send = 'To Be Imlpemented: user stats'
                elif command == '/welcome':
                    message_to_send = f'Hello {player.user_name}!\nWelcome to {chat.chat_title}'
                else:
                    message_to_send = 'Command Not Implemented'
            
            # Commands for games
            elif command in game_list:
                if command == '/number':
                    message_to_send = 'Number Game'
                    message_to_send = play_number(text, chat, player)
                elif command == '/trivia':
                    message_to_send = play_trivia(text, chat, player)
                elif command == '/hangman':
                    message_to_send = play_hangman(text, chat, player)
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
    if message == None:
        message = json_request.get('my_chat_member')
    if message == None:
        message = json_request.get('poll')
        if message != None:
            formated_json['poll_id'] = message.get('id')
            formated_json['total_voter_count'] = message.get('total_voter_count')
            formated_json['is_closed'] = message.get('is_closed')
            formated_json['chat_type'] = 'poll'
            return formated_json
    if message == None:
        message = json_request.get('poll_answer')
        formated_json['poll_id'] = message.get('poll_id')
        formated_json['sender_id'] = message.get('user').get('id')
        formated_json['option_ids'] = message.get('option_ids')
        formated_json['chat_type'] = 'poll'
        return formated_json

    if message is not None:
        #Skipping checks
        formated_json['chat_id'] = message.get('chat').get('id')
        formated_json['chat_type'] = message.get('chat').get('type')

        if formated_json['chat_type'] == 'group':
            formated_json['chat_title'] = message.get('chat').get('title')
        elif formated_json['chat_type'] == 'supergroup':
            formated_json['chat_title'] = message.get('chat').get('title')
        else:
            formated_json['chat_title'] = message.get('chat').get('first_name') + ' ' + message.get('chat').get('last_name', '')

        formated_json['sender_id'] = message.get('from').get('id')
        formated_json['sender_name'] = message.get('from').get('first_name') + ' ' + message.get('from').get('last_name', '')
        
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
        stats = Stats.objects.filter(player=player, chat_id=json_request.get('chat_id'))
        if int(len(stats)) < 1:
            stats = Stats.objects.create(player=player, chat_id=json_request.get('chat_id'))
    else:
        player = Player.objects.create(user_id=json_request.get('sender_id'),
                                       user_name=json_request.get('sender_name'))
        player.save()
        stats = Stats.objects.create(player=player, chat_id=json_request.get('chat_id'))
        stats.save()
        chat = Chat.objects.create(player=player,
                                       chat_id=json_request.get('chat_id'),
                                       chat_type=json_request.get('chat_type'),
                                       chat_title=json_request.get('chat_title'))
        chat.save()
    return (player, chat)

def get_stats(text, player, chat):
    #logger.info(text)
    if len(text) == 1:
        player_stats = Stats.objects.filter(player=player.user_id,chat_id=chat.chat_id)
        if len(player_stats) >= 1:
            logger.info(player_stats[0].won)
            return f"The player {player.user_name} has played {player_stats[0].played} games, won {player_stats[0].won} games, and lost {player_stats[0].lost} games"
        else:
            return f"The player {player.user_name} has not played any games"
    if len(text) == 2:
        if text[1] == "all":
            
            
            chats = Chat.objects.filter(chat_id=chat.chat_id)
            text = "Player                          W L played\n"
            for i in range(len(chats)):
                stat = Stats.objects.filter(player=chats[i].player)
                if len(stat) >= 1:
                    player_name = Player.objects.filter(user_id=chats[i].player.user_id)
                    length = int(len(player_name[0].user_name))
                    total = "  "*(20-int(len(player_name[0].user_name)))
                    text+= f" {str(player_name[0].user_name)[:21]}{total}{stat[0].won}  {stat[0].lost}     {stat[0].played}\n"
            return text
                
    return f"No se encontro la accion: {' '.join(text)}"
