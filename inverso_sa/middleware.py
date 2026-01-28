from django.shortcuts import redirect
from django.urls import resolve, Resolver404


class Redirect404Middleware:

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):

        # ⚠️ NO tocar archivos estáticos ni media
        if (
            request.path.startswith('/static/') or
            request.path.startswith('/media/') or
            request.path.startswith('/admin/')
        ):
            return self.get_response(request)

        try:
            resolve(request.path)
        except Resolver404:

            # 🔐 usuario logueado → inicio
            if request.user.is_authenticated:
                return redirect('inicio')

            # 🚪 usuario NO logueado → login
            return redirect('login')

        return self.get_response(request)
