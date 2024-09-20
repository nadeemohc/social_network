from django.core.cache import cache
from rest_framework.response import Response
from django.http import JsonResponse
from django.utils.timezone import now
from datetime import timedelta
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
            return JsonResponse({"error": "Rate limit exceeded"}, status=429)

        response = self.get_response(request)
        return response

def can_send_friend_request(sender):
    cache_key = f"example:{sender.id}:friend_request_limit"
    
    # Check if the key exists, if not, initialize it with 0
    if not cache.has_key(cache_key):
        cache.set(cache_key, 0, timeout=60)  # Set the key with a timeout of 60 seconds
    
    # Increment the counter
    count = cache.incr(cache_key)
    
    # If the count exceeds 3, deny the request
    if count > 3:
        return False
    return True