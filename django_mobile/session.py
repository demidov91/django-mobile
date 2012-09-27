from session_settings import settings
from django_mobile import Middleware, DjangoMobile

class SessionMiddleware(Middleware):
    def create(self, request):
        return DjangoSessionMobile(request)
                
       
class DjangoSessionMobile(DjangoMobile):
    def __init__(self, request):
        self.request = request
        self.set(request.GET.get(settings.FLAVOURS_GET_PARAMETER))
        if not request.session.get(settings.FLAVOURS_SESSION_KEY):
            if SessionMiddleware.is_mobile(request):
                self.set(settings.DEFAULT_MOBILE_FLAVOUR)
            else:
                self.set(settings.DEFAULT_FLAVOUR)
    
    def get(self):
        return self.request.session.get(settings.FLAVOURS_SESSION_KEY) or settings.DEFAULT_FLAVOUR

    def set(self, flavour):
        if not super(DjangoSessionMobile, self).set(flavour):
            return False
        else:
            self.request.session[settings.FLAVOURS_SESSION_KEY] = flavour
            return True
