from django.shortcuts import render
from django.http import HttpResponse, HttpResponseBadRequest, JsonResponse

import logging, requests
logger = logging.getLogger('django')

# Create your views here.
def test_page(request):
    context = {}
    return(render(request, 'test.html', context=context))


def webhook(request):
    logger.info(request)
    logger.info(request.data)

    if request.method == 'POST':
        return JsonResponse({'error':'post method not doing anything'},status=204)
    elif request.method == 'GET':
        #return HttpResponse(status=200)
        chat_id = request.data['message']['chat']['id']
        text = request.data['message']['chat']['id']
        sendMessage(chat_id)
        return JsonResponse({'success':'get method working'},status=200)
    else:
        return HttpResponseBadRequest()
        
def sendMessage(chat_id, text='bot response'):
    url = f'https://api.telegram.org/bot5668389701:AAHWwdNxz6fbX3lh4RfhSyuZvnHpOFHT9IQ/sendMessage'
    data = {'chat_id':chat_id,
            'text':text}
    request = requests.post(url, json=data)
    return request