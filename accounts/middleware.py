from django.core.cache import cache
from rest_framework.response import Response
from rest_framework.views import APIView

class RateLimitMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        # Skip rate limiting for admin URLs
        if request.path.startswith('/admin/'):
            return self.get_response(request)

        ip_address = request.META.get('REMOTE_ADDR')
        cache_key = f'rate_limit_{ip_address}'
        count = cache.get(cache_key)

        if count is None:
            cache.set(cache_key, 1, timeout=60)  # 1 minute timeout
            count = 1
        else:
            count = cache.incr(cache_key)

        if count > 5:
            return Response({"error": "Rate limit exceeded"}, status=429)

        response = self.get_response(request)
        return response
