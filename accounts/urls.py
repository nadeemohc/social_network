from django.urls import path
from rest_framework_simplejwt.views import TokenRefreshView
from .views import *
from rest_framework import permissions
from drf_yasg.views import get_schema_view
from drf_yasg import openapi

schema_view = get_schema_view(
   openapi.Info(
      title="Your Project API",
      default_version='v1',
      description="API documentation for your project",
      terms_of_service="https://www.google.com/policies/terms/",
      contact=openapi.Contact(email="your-email@example.com"),
      license=openapi.License(name="BSD License"),
   ),
   public=True,
   permission_classes=(permissions.AllowAny,),
)
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
    path('sent-pending-requests/', SentPendingFriendRequestsView.as_view(), name='sent-pending-requests'),
    # path('pending-friend-requests/', PendingFriendRequestsView.as_view(), name='pending-friend-requests'),
    path('received-pending-requests/', ReceivedPendingFriendRequestsView.as_view(), name='received-pending-requests'),
    path('swagger/', schema_view.with_ui('swagger', cache_timeout=0), name='schema-swagger-ui'),
    path('redoc/', schema_view.with_ui('redoc', cache_timeout=0), name='schema-redoc'),
]
