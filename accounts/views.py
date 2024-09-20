from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView
from django.contrib.auth.hashers import make_password
from .models import User, FriendRequest
from rest_framework_simplejwt.views import TokenObtainPairView
from .serializers import MyTokenObtainPairSerializer
from rest_framework.permissions import IsAuthenticated
from django.core.cache import cache
from .permissions import IsRead, IsWrite, IsAdmin
from accounts.middleware import RateLimitMiddleware
import logging
from rest_framework import generics
from django.db.models import Q
from django.contrib.postgres.search import SearchVector, SearchQuery, SearchRank
from .serializers import UserSerializer
from rest_framework.pagination import PageNumberPagination
from accounts.middleware import can_send_friend_request
from django.db import transaction
from django.utils.timezone import now, timedelta

logger = logging.getLogger(__name__)

class SignUpView(APIView):
    permission_classes = [IsWrite]  # Only users with 'write' or higher roles can sign up new users
    
    def get(self, request):
        return Response({"message": "Use POST to sign up a new user."}, status=status.HTTP_405_METHOD_NOT_ALLOWED)

    def post(self, request):
        email = request.data.get('email').strip().lower()
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


class UserSearchPagination(PageNumberPagination):
    page_size = 10

class UserSearchView(generics.ListAPIView):
    serializer_class = UserSerializer
    pagination_class = UserSearchPagination

    def get_queryset(self):
        search_query = self.request.query_params.get('q', '')
        if not search_query:
            return User.objects.none()

        # Search by exact email
        email_matches = User.objects.filter(email__iexact=search_query)

        # Full-text search for username
        search_vector = SearchVector('username')
        search_query_obj = SearchQuery(search_query, config='english')
        name_matches = User.objects.annotate(
            rank=SearchRank(search_vector, search_query_obj)
        ).filter(Q(username__icontains=search_query) | Q(rank__gte=0.1)).order_by('-rank')

        # Combine email matches and name matches
        # Convert QuerySets to lists to perform union and deduplication
        email_matches_list = list(email_matches.values_list('id', flat=True))
        name_matches_list = list(name_matches.values_list('id', flat=True))

        combined_ids = set(email_matches_list) | set(name_matches_list)
        queryset = User.objects.filter(id__in=combined_ids)

        return queryset

class SendFriendRequestView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, *args, **kwargs):
        sender = request.user
        print(f'sender = {sender}')
        # Ensure the sender is authenticated and has a valid ID
        if not sender or not sender.id:
            return Response({"error": "Authentication required"}, status=status.HTTP_401_UNAUTHORIZED)

        receiver_id = request.data.get('receiver_id')

        if not can_send_friend_request(sender):
            return Response({"error": "Request limit exceeded"}, status=status.HTTP_429_TOO_MANY_REQUESTS)

        try:
            receiver = User.objects.get(id=receiver_id)
        except User.DoesNotExist:
            return Response({"error": "User not found"}, status=status.HTTP_404_NOT_FOUND)

        # Check if a friend request was already sent
        friend_request = FriendRequest.objects.filter(sender=sender, receiver=receiver).first()
        print(f'Request info: {friend_request}')

        if friend_request and friend_request.status == FriendRequest.REJECTED:
            cooldown_end = friend_request.updated_at + timedelta(hours=24)
            if now() < cooldown_end:
                return Response({"error": "Cannot send request yet, cooldown active"}, status=status.HTTP_403_FORBIDDEN)

        if friend_request and friend_request.status == FriendRequest.PENDING:
            return Response({"error": "Friend request already sent"}, status=status.HTTP_400_BAD_REQUEST)

        # Create a new friend request
        FriendRequest.objects.create(sender=sender, receiver=receiver)
        return Response({"message": "Friend request sent"}, status=status.HTTP_201_CREATED)


class AcceptFriendRequestView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, *args, **kwargs):
        # Ensure the user is authenticated
        if not request.user or request.user.is_anonymous:
            return Response({"error": "Authentication required"}, status=status.HTTP_401_UNAUTHORIZED)

        try:
            # Fetch the friend request sent to the current authenticated user
            friend_request = FriendRequest.objects.get(id=kwargs['request_id'], receiver=request.user)
        except FriendRequest.DoesNotExist:
            return Response({"error": "Request not found"}, status=status.HTTP_404_NOT_FOUND)

        # Atomic transaction to ensure data integrity
        with transaction.atomic():
            friend_request.status = FriendRequest.ACCEPTED
            friend_request.save()

        return Response({"message": "Friend request accepted"}, status=status.HTTP_200_OK)



