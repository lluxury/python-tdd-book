from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.backends import ModelBackend
from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse
import logging

logger = logging.getLogger(__name__)


class EmailBackend(ModelBackend):
    """
    Authentication backend that uses email instead of username
    """
    def authenticate(self, request, email=None, password=None, **kwargs):
        from accounts.models import ListUser
        try:
            user = ListUser.objects.get(email=email)
            return user
        except ListUser.DoesNotExist:
            # Create user if doesn't exist
            user = ListUser.objects.create_user(email=email)
            return user


@csrf_exempt
def supabase_auth(request):
    """
    Handle Supabase authentication
    """
    if request.method == 'POST':
        import json
        try:
            data = json.loads(request.body.decode('utf-8'))
            email = data.get('email')

            if email:
                # Use authenticate to verify the user
                user = authenticate(request, email=email)

                if user:
                    login(request, user, backend='accounts.views.EmailBackend')
                    return JsonResponse({'status': 'success', 'email': email})

        except Exception as e:
            logger.error(f"Auth error: {e}")
            return JsonResponse({'status': 'error', 'message': str(e)}, status=400)

    return JsonResponse({'status': 'error', 'message': 'Invalid request'}, status=400)


def supabase_logout(request):
    """
    Handle Supabase logout
    """
    logout(request)
    return redirect('/')
