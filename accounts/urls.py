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
]
