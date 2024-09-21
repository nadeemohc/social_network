from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView
from django.contrib.auth.hashers import make_password
from .models import User, FriendRequest
from rest_framework_simplejwt.views import TokenObtainPairView
from .serializers import MyTokenObtainPairSerializer, PendingFriendRequestSerializer
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
from rest_framework.generics import ListAPIView

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
        print(f'reciever id = {receiver_id}')

        if not can_send_friend_request(sender):
            return Response({"error": "Request limit exceeded"}, status=status.HTTP_429_TOO_MANY_REQUESTS)

        try:
            receiver = User.objects.get(id=receiver_id)
            print(f'reciever={receiver}')
        except User.DoesNotExist:
            return Response({"error": "User not found"}, status=status.HTTP_404_NOT_FOUND)

        if sender.is_blocked(receiver) or receiver.is_blocked(sender):
            return Response({"error": "You cannot send a friend request to this user"}, status=status.HTTP_403_FORBIDDEN)


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
        friend_request = FriendRequest.objects.get(id=kwargs['request_id'], receiver=request.user)
        if friend_request.status != 'rejected':
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
        
        return Response({"message": "Friend request already rejected"}, status=status.HTTP_200_OK)
        


class RejectFriendRequestView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, *args, **kwargs):
        if not request.user or request.user.is_anonymous:
            return Response({"error": "Authentication required"}, status=status.HTTP_401_UNAUTHORIZED)

        try:
            friend_request = FriendRequest.objects.get(id=kwargs['request_id'], receiver=request.user)
        except FriendRequest.DoesNotExist:
            return Response({"error": "Request not found"}, status=status.HTTP_404_NOT_FOUND)

        # Ensure cooldown period after rejecting
        if friend_request.is_rejected_cooldown_active():
            return Response({"error": "You can't send request now as you're in the cooldown period"}, status=status.HTTP_403_FORBIDDEN)

        with transaction.atomic():
            friend_request.status = FriendRequest.REJECTED
            friend_request.save()

        return Response({"message": "Friend request rejected"}, status=status.HTTP_200_OK)

class BlockUserView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, *args, **kwargs):
        blocker = request.user
        blocked_id = request.data.get('blocked_id')

        try:
            blocked_user = User.objects.get(id=blocked_id)
        except User.DoesNotExist:
            return Response({"error": "User not found"}, status=status.HTTP_404_NOT_FOUND)

        if blocker.is_blocked(blocked_user):
            return Response({"error": "User is already blocked"}, status=status.HTTP_400_BAD_REQUEST)

        # Block the user
        blocker.blocked_users.add(blocked_user)

        # Optionally, handle existing friend requests
        FriendRequest.objects.filter(sender=blocker, receiver=blocked_user).update(status=FriendRequest.BLOCKED)
        FriendRequest.objects.filter(sender=blocked_user, receiver=blocker).update(status=FriendRequest.BLOCKED)

        return Response({"message": "User blocked"}, status=status.HTTP_200_OK)



class UnblockUserView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, *args, **kwargs):
        blocker = request.user
        blocked_id = request.data.get('blocked_id')

        try:
            blocked_user = User.objects.get(id=blocked_id)
        except User.DoesNotExist:
            return Response({"error": "User not found"}, status=status.HTTP_404_NOT_FOUND)

        if not blocker.is_blocked(blocked_user):
            return Response({"error": "User is not blocked"}, status=status.HTTP_400_BAD_REQUEST)

        # Unblock the user
        blocker.blocked_users.remove(blocked_user)
        return Response({"message": "User unblocked"}, status=status.HTTP_200_OK)


class ProfileView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, user_id):
        try:
            # Fetch the profile of the requested user
            user = User.objects.get(id=user_id)
            
            # Check if the requesting user has blocked the target user or vice versa
            if user in request.user.blocked_users.all() or request.user in user.blocked_users.all():
                return Response({"error": "You cannot view this profile as one of you has blocked the other."}, 
                                status=status.HTTP_403_FORBIDDEN)
            
            # Serialize and return the user profile data
            serializer = UserSerializer(user)
            return Response(serializer.data, status=status.HTTP_200_OK)
        
        except User.DoesNotExist:
            return Response({"error": "User not found"}, status=status.HTTP_404_NOT_FOUND)

class FriendListPagination(PageNumberPagination):
    page_size = 10

class FriendListView(ListAPIView):
    permission_classes = [IsAuthenticated]
    pagination_class = FriendListPagination
    serializer_class = UserSerializer

    def get_queryset(self):
        user = self.request.user

        # Check if result is cached
        cache_key = f"friends_list_{user.id}"
        friends_list = cache.get(cache_key)

        if not friends_list:
            # Query for accepted friend requests
            accepted_friend_requests = FriendRequest.objects.filter(
                Q(sender=user) | Q(receiver=user),
                status=FriendRequest.ACCEPTED
            ).select_related('sender', 'receiver')

            # Build the list of friends
            friends = []
            for request in accepted_friend_requests:
                if request.sender == user:
                    friends.append(request.receiver)
                else:
                    friends.append(request.sender)

            # Cache the result for 10 minutes
            cache.set(cache_key, friends, timeout=60 * 10)

        return friends_list or []

    def list(self, request, *args, **kwargs):
        """
        Override list method to cache paginated response as well.
        """
        response = super().list(request, *args, **kwargs)
        return response


from .pagination import PendingFriendRequestPagination

class PendingFriendRequestsView(ListAPIView):
    permission_classes = [IsAuthenticated]
    pagination_class = PendingFriendRequestPagination
    serializer_class = PendingFriendRequestSerializer

    def get_queryset(self):
        user = self.request.user
        print(user)
        return FriendRequest.objects.filter(receiver=user, status=FriendRequest.PENDING).order_by('-created_at')

