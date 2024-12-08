
def get_host(request):
    return request.get_host().split(':')[0]
