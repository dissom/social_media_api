from rest_framework import generics, status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.settings import api_settings
from rest_framework.authtoken.models import Token
from rest_framework.authtoken.views import ObtainAuthToken

from django.contrib.auth import authenticate, login, logout

from user.serializers import (
    UserDetailSerializer,
    UserLoginSerializer,
    UserSerializer
)


class CreateUserView(generics.CreateAPIView):
    serializer_class = UserSerializer
    permission_classes = ()

    def perform_create(self, serializer):
        serializer.save()


class LoginUserView(ObtainAuthToken):
    serializer_class = UserLoginSerializer
    renderer_classes = api_settings.DEFAULT_RENDERER_CLASSES

    def post(self, request) -> Response:

        email = request.data.get("email")
        password = request.data.get("password")
        user = authenticate(request, email=email, password=password)

        if user:
            login(request, user)
            token, created = Token.objects.get_or_create(user=user)
            return Response({"token": token.key}, status=status.HTTP_200_OK)

        return Response(
            {"error": "Invalid credentials"},
            status=status.HTTP_401_UNAUTHORIZED,
        )


class UserLogoutAPIView(APIView):

    def post(self, request):
        token = Token.objects.get(user=request.user)
        token.delete()
        logout(request)
        return Response(
            {"success": True, "detail": "Logged out!"},
            status=status.HTTP_200_OK
        )


class ManageUserView(generics.RetrieveUpdateDestroyAPIView):
    serializer_class = UserDetailSerializer

    def get_object(self):
        return self.request.user

    # def get_serializer_class(self):
    #     serializer = self.serializer_class
    #     if self.request.method == "retrieve":
    #         serializer = UserDetailSerializer
    #     return serializer
