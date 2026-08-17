from rest_framework import generics
from rest_framework.permissions import AllowAny

from users.serializers import UserSignUpSerializer, UserDetailSerializer


class SignUpView(generics.CreateAPIView):
    serializer_class = UserSignUpSerializer
    permission_classes = [AllowAny]


class UserMeView(generics.RetrieveUpdateDestroyAPIView):
    serializer_class = UserDetailSerializer

    def get_object(self):
        return self.request.user
