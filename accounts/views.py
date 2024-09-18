from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView
from django.contrib.auth.hashers import make_password
from .models import User
from rest_framework_simplejwt.views import TokenObtainPairView
from .serializers import MyTokenObtainPairSerializer
from django.core.cache import cache
from .permissions import IsRead, IsWrite, IsAdmin
from accounts.middleware import RateLimitMiddleware
import logging

logger = logging.getLogger(__name__)

class SignUpView(APIView):
    permission_classes = [IsWrite]  # Only users with 'write' or higher roles can sign up new users
    
    def get(self, request):
        return Response({"message": "Use POST to sign up a new user."}, status=status.HTTP_405_METHOD_NOT_ALLOWED)

    def post(self, request):
        email = request.data.get('email')
        password = request.data.get('password')

        if not email or not password:
            return Response({"error": "Email and password are required"}, status=status.HTTP_400_BAD_REQUEST)

        if User.objects.filter(email=email).exists():
            return Response({"error": "User already exists"}, status=status.HTTP_400_BAD_REQUEST)

        user = User.objects.create(
            email=email,
            username=email.split('@')[0],
            password=make_password(password),
            role='read'  # New users start with 'read' permissions
        )

        return Response({"message": "User created successfully"}, status=status.HTTP_201_CREATED)


import logging
logger = logging.getLogger(__name__)

class MyTokenObtainPairView(TokenObtainPairView):
    serializer_class = MyTokenObtainPairSerializer

    def post(self, request, *args, **kwargs):
        return super().post(request, *args, **kwargs)
        cache_key = f'rate_limit_{ip_address}'

        # count = cache.get(cache_key)
        # logger.info(f"Cache Key: {cache_key}, Count: {count}")
        print(f'count={count}')
        if count is None:
            cache.set(cache_key, 1, timeout=60)
            count = 1
            print(f'count={count}')
        else:
            count = cache.incr(cache_key)
            print(f'count={count}')

        if count > 5:
            logger.info(f"Rate limit exceeded for {ip_address}")
            return Response({"error": "Rate limit exceeded"}, status=status.HTTP_429_TOO_MANY_REQUESTS)

        return super().post(request, *args, **kwargs)
