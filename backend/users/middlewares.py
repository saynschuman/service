from datetime import datetime

from django.conf import settings
from django.utils.deprecation import MiddlewareMixin

from backend.users.models import User


class LastActiveUserMiddleware(MiddlewareMixin):
    def __call__(self, request):
        if request.user and request.user.is_authenticated:
            u = User.objects.get(id=request.user.id)
            u.last_active = datetime.now()
            u.save()

        response = self.get_response(request)
        return response
       
