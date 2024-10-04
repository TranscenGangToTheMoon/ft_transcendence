import json

from django.http import JsonResponse


# Create your views here.
def api_root(request):
    print(request.method)
    print(request.GET)
    print(request.POST)
    try:
        response = json.loads(request.body)
    except json.decoder.JSONDecodeError:
        response = {}
    response['params'] = dict(request.GET)
    response['headers'] = dict(request.headers)
    response['content_type'] = request.content_type
    print(response)
    return JsonResponse(response)
