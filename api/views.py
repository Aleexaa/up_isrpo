from django.http import JsonResponse

def api_info(request):
    return JsonResponse({
        'status': 'ok',
        'message': 'API работает'
    })