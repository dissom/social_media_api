from django.shortcuts import redirect
from rest_framework import generics, status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.settings import api_settings
from rest_framework.authtoken.models import Token
from rest_framework.authtoken.views import ObtainAuthToken

# from rest_framework.permissions import IsAuthenticated
from django.contrib.auth import authenticate, login, logout

from user.serializers import (
    UserDetailSerializer,
    UserLoginSerializer,
    UserSerializer
)


class CreateUserView(generics.CreateAPIView):
    serializer_class = UserSerializer
    permission_classes = ()


class LoginUserView(ObtainAuthToken):
    serializer_class = UserLoginSerializer
    renderer_classes = api_settings.DEFAULT_RENDERER_CLASSES

    def post(self, request) -> Response:
        # print(request.data)
        email = request.data.get("email")
        password = request.data.get("password")
        user = authenticate(request, email=email, password=password)
        if user:
            # User is authenticated
            login(request, user)
            token, created = Token.objects.get_or_create(user=user)

            response = redirect("user:manage")
            return response

            # return Response({"token": token.key}, status=status.HTTP_200_OK)
        return Response(
            {"error": "Invalid credentials"},
            status=status.HTTP_401_UNAUTHORIZED,
        )


class UserLogoutAPIView(APIView):

    def post(self, request, *args):
        token = Token.objects.get(user=request.user)
        token.delete()
        logout(request)
        return Response(
            {"success": True, "detail": "Logged out!"},
            status=status.HTTP_200_OK
        )
# class UserLogoutAPIView(ObtainAuthToken):
#     serializer_class = UserSerializer
#     renderer_classes = api_settings.DEFAULT_RENDERER_CLASSES

#     def post(self, request):

#         print(request.data)
#         logout(request)
#         return Response(status=status.HTTP_200_OK)


class ManageUserView(generics.RetrieveUpdateDestroyAPIView):
    serializer_class = UserDetailSerializer
    # permission_classes = (IsAuthenticated)

    def get_object(self):
        return self.request.user
