from rest_framework_simplejwt.serializers import TokenObtainPairSerializer

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
