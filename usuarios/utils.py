def get_client_ip(request):
    forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if forwarded_for:
        client_ip = forwarded_for.split(',', 1)[0].strip()
        if client_ip:
            return client_ip
    return request.META.get('REMOTE_ADDR') or 'unknown'
