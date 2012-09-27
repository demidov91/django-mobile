from django.core.exceptions import ImproperlyConfigured
from django_mobile.conf import settings
import logging
import re

class DjangoMobile(object):
    """Base 'abstract' class for all implementations of django-mobile."""
    def __init__(self, request, detected):
        raise NotImplementedError(
            '%s is `abstract` class. You should use some implementation of it.' % self.__class__.__name__ 
        )
    def get(self):
        raise NotImplementedError(
            '%s is `abstract` class. You should use some implementation of it.' % self.__class__.__name__ 
        )
    def set(self, flavour):
        if not flavour in  settings.FLAVOURS:
            if flavour:
                logging.warning('Attempt to use illegal flavour.')
            return False
        return True
    def is_mobile(self):
        return self.get() == settings.DEFAULT_MOBILE_FLAVOUR
    def is_default(self):
        return self.get() == settings.DEFAULT_FLAVOUR
    

class CookiesHolder:
    """
    Wrapper around list to provide default path.
    """
    _list_of_cookies = []
    def add(self, dictionary, path = '/'):
        if not dictionary.__class__ is dict:
            raise ValueError('Object of class `dict` expected, got %s.' % dictionary.__class__.__name__)
        self._list_of_cookies.append((dictionary, path))
    def get(self):
        return self._list_of_cookies

class Middleware(object):
    """ 
    Base implementation of django-mobile middleware and factory for DjangoMobile objects.
    """
    is_stopped = False
    user_agents_test_match = (
        "w3c ", "acs-", "alav", "alca", "amoi", "audi",
        "avan", "benq", "bird", "blac", "blaz", "brew",
        "cell", "cldc", "cmd-", "dang", "doco", "eric",
        "hipt", "inno", "ipaq", "java", "jigs", "kddi",
        "keji", "leno", "lg-c", "lg-d", "lg-g", "lge-",
        "maui", "maxo", "midp", "mits", "mmef", "mobi",
        "mot-", "moto", "mwbp", "nec-", "newt", "noki",
        "xda",  "palm", "pana", "pant", "phil", "play",
        "port", "prox", "qwap", "sage", "sams", "sany",
        "sch-", "sec-", "send", "seri", "sgh-", "shar",
        "sie-", "siem", "smal", "smar", "sony", "sph-",
        "symb", "t-mo", "teli", "tim-", "tosh", "tsm-",
        "upg1", "upsi", "vk-v", "voda", "wap-", "wapa",
        "wapi", "wapp", "wapr", "webc", "winw", "winw",
        "xda-",)
    user_agents_test_search = u"(?:%s)" % u'|'.join((
        'up.browser', 'up.link', 'mmp', 'symbian', 'smartphone', 'midp',
        'wap', 'phone', 'windows ce', 'pda', 'mobile', 'mini', 'palm',
        'netfront', 'opera mobi',
    ))
    user_agents_exception_search = u"(?:%s)" % u'|'.join((
        'ipad',
    ))
    http_accept_regex = re.compile("application/vnd\.wap\.xhtml\+xml", re.IGNORECASE)

    def __init__(self):
        user_agents_test_match = r'^(?:%s)' % '|'.join(self.user_agents_test_match)
        self.user_agents_test_match_regex = re.compile(user_agents_test_match, re.IGNORECASE)
        self.user_agents_test_search_regex = re.compile(self.user_agents_test_search, re.IGNORECASE)
        self.user_agents_exception_search_regex = re.compile(self.user_agents_exception_search, re.IGNORECASE)
        
    def create(self, *args, **kwargs):
        raise NotImplementedError(
            '%s is `abstract` class. You should use some implementation of it.' % self.__class__ 
        )
        
    def stop(self):
        self.is_stopped = True
                
    def start():
        raise NotImplementedError(
            '%s is `abstract` class. You should use some implementation of it.' % self.__class__ 
        )    
        
    def process_request(self, request):
        if self.is_stopped:
            logging.warning(
                "Django-mobile was stopped. Request won't be processed with %s middleware." % self.__class__.__name__
                )
            return
        if hasattr(request, 'flavour') or hasattr(request, 'cookies_to_save'):
            self.stop()
            raise ImproperlyConfigured(
                "Some middleware has used 'flavour' or 'cookies_to_save' field of `request` object. Django-mobile is stopped."
                )       
        request.cookies_to_save = CookiesHolder()
        request.flavour = self.create(request = request)        
        if not request.flavour:
            raise NotImplementedError(
                '`create` method should return instance of class inherited from DjangoMobile.'
                )       
        
                
    def is_mobile(request):
        if request.META.has_key('HTTP_USER_AGENT'):
            user_agent = request.META['HTTP_USER_AGENT']
            if self.user_agents_test_search_regex.search(user_agent) and \
                not self.user_agents_exception_search_regex.search(user_agent):
                return True
            else:
                # Nokia like test for WAP browsers.
                # http://www.developershome.com/wap/xhtmlmp/xhtml_mp_tutorial.asp?page=mimeTypesFileExtension
                if request.META.has_key('HTTP_ACCEPT'):
                    http_accept = request.META['HTTP_ACCEPT']
                    if self.http_accept_regex.search(http_accept):
                        return True
            if self.user_agents_test_match_regex.match(user_agent):
                return True
                
    def process_template_response(self, request, response):
        if not (request.flavour.is_default() or self.is_stopped):          
            response.template_name = "%s/%s" % (request.flavour.get(), response.template_name)
            if settings.FLAVOURS_TEMPLATE_PREFIX:
                response.template_name = settings.FLAVOURS_TEMPLATE_PREFIX + response.template_name
            response.context_data.update(self.get_additional_context(request))
        return response
    
    def get_additional_context(self, request):
        return {
            'flavour': request.flavour.get(),
            'is_mobile': request.flavour.is_mobile(),
            'is_default': request.flavour.is_default(),
            'STATIC_URL_MOBILE':settings.STATIC_URL_MOBILE,
        }
    def process_response(self, request, response):
        if not self.is_stopped:
            for cookies, path in request.cookies_to_save.get():
                for name, value in cookies.items():
                    response.set_cookie(name, value, path=path)
                    print 'cookie %s saved' % name
        return response


def get_flavour(request):
    return request.flavour.get()
    
def set_flavour(request, flavour):
    request.flavour.set(flavour)
    


    
    
    
    
   

