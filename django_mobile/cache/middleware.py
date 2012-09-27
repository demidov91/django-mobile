from django.utils.cache import patch_vary_headers


class CacheFlavourMiddleware(object):
    def process_request(self, request):
        request.META['HTTP_X_Flavour'] = request.flavour.get()
        
    def process_response(self, request, response):
        patch_vary_headers(response, ['X-Flavour'])
        return response
