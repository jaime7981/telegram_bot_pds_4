from django.shortcuts import render
from django.http import HttpResponse, HttpResponseBadRequest, JsonResponse

from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator

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
        logger.info(request_data)
        message = request_data.get('message')
        text = ''
        
        if message is not None:
            if message.get('chat').get('id') is not None:
                chat_id = request_data['message']['chat']['id']
            else:
                return JsonResponse({'error':'could not get chat id'},status=400)
            text = message.get('text', 'could not format text')
        
        flag=True
        for element in text.split():
            if element in bot_commands:
                if element == '/start':
                    sendMessage(chat_id, text='Starting Bot')
                elif element == '/games':
                    sendMessage(chat_id, text='\n'.join(game_list))
                elif element == '/stats':
                    sendMessage(chat_id, text='To Be Imlpemented: user stats')
                flag=False
                break
        if flag:
            sendMessage(chat_id, text=str('Unkown command\n' + '\n'.join(bot_commands)))
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