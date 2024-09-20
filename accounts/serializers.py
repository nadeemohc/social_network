from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from rest_framework import serializers
from .models import User


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'email', 'username', 'role']


class MyTokenObtainPairSerializer(TokenObtainPairSerializer):
    def validate(self, attrs):
        data = super().validate(attrs)
        refresh = self.get_token(self.user)
        data['id'] = self.user.id
        data['refresh'] = str(refresh)
        data['access'] = str(refresh.access_token)

        # Add extra claims
        data['email'] = self.user.email
        data['role'] = self.user.role
        return data
