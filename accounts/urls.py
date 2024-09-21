from django.urls import path
from rest_framework_simplejwt.views import TokenRefreshView
from .views import *

urlpatterns = [
    path('signup/', SignUpView.as_view(), name='signup'),
    path('login/', MyTokenObtainPairView.as_view(), name='login'),
    path('refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('search/', UserSearchView.as_view(), name='user_search'),
    path('send/', SendFriendRequestView.as_view(), name='send_friend_request'),
    path('accept/<int:request_id>/', AcceptFriendRequestView.as_view(), name='accept_friend_request'),
    path('reject/<int:request_id>/', RejectFriendRequestView.as_view(), name='reject_friend_request'),
    path('block/', BlockUserView.as_view(), name='block_user'),
    path('unblock/', UnblockUserView.as_view(), name='unblock_user'),
    path('profile/<int:user_id>/', ProfileView.as_view(), name='view_profile'),
    path('friends/', FriendListView.as_view(), name='friends-list'),
    path('pending-friend-requests/', PendingFriendRequestsView.as_view(), name='pending-friend-requests'),
]
