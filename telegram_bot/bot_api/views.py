from django.shortcuts import render
from django.http import HttpResponse, HttpResponseBadRequest, JsonResponse


# Create your views here.
def test_page(request):
    context = {}
    return(render(request, 'test.html', context=context))


def webhook(request):
    if request.method == 'POST':
        return JsonResponse({'error':'post method not doing anything'},status=204)
    elif request.method == 'GET':
        #return HttpResponse(status=200)
        return JsonResponse({'success':'get method working'},status=200)
    else:
        return HttpResponseBadRequest()
        
