# accounts/pagination.py
from rest_framework.pagination import PageNumberPagination

class PendingFriendRequestPagination(PageNumberPagination):
    page_size = 10
