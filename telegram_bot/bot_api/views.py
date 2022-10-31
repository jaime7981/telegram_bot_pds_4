from django.shortcuts import render
from django.http import HttpResponse, HttpResponseBadRequest, JsonResponse

from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator

import logging, requests, json
logger = logging.getLogger('django')

# Create your views here.
def test_page(request):
    context = {}
    return(render(request, 'test.html', context=context))

def root(request):
    return HttpResponse(status=200)

@csrf_exempt
def webhook(request):
    logger.info(request)
    logger.info(request.headers)
    logger.info(request.body)

    if request.method == 'POST':
        logger.info(json.loads(request.body))
        request_data = json.loads(request.body)
        chat_id = request_data['message']['chat']['id']
        text = request_data['message']['chat']['id']
        sendMessage(chat_id)
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