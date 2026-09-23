from django.contrib.auth import logout


class SessionVersionMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        if request.user.is_authenticated:
            profile = getattr(request.user, 'profile', None)
            if profile and request.session.get('session_version') != profile.session_version:
                logout(request)
        return self.get_response(request)