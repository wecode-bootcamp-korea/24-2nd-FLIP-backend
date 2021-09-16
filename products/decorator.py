import jwt

from django.http   import JsonResponse
from django.conf   import settings
from users.models  import User  

def visitor_decorator(func):
    def wraper(self, request, *args, **kwargs):
        try:           
            access_token = request.headers.get('Authorization', None)
            token = jwt.decode(access_token, settings.SECRET_KEY, algorithms='HS256')
            user = User.objects.get(id=token['id'])
            request.user = user.id
        except jwt.exceptions.DecodeError:
             return JsonResponse({'MESSAGE': 'WRONG_ACCESS'}, status=401)
        except User.DoesNotExist:
            return JsonResponse({'MESSAGE': 'INVALID_USER'}, status=401)
        return func(self, request, *args, **kwargs)
    return wraper