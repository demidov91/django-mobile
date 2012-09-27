from django_mobile import get_flavour, get_platform
from django_mobile.conf import settings


def flavour(request):
    return {
        'flavour': get_flavour(request),
        'client_platform':get_platform(request),
        'is_mobile': get_flavour(request) == settings.DEFAULT_MOBILE_FLAVOUR,
        'STATIC_URL_MOBILE': settings.STATIC_URL_MOBILE,
    }
