from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from social.models import UserProfile
from social.serializers import (
    UserProfileDetailSerializer,
    # UserProfileListSerializer,
    UserProfileSerializer
)


class UserProfileView(viewsets.ModelViewSet):

    queryset = UserProfile.objects.all()
    serializer_class = UserProfileSerializer

    def get_queryset(self):
        queryset = self.queryset.filter(owner=self.request.user)
        return queryset

    def get_serializer_class(self):
        serializer = self.serializer_class
        if self.action == "retrieve":
            serializer = UserProfileDetailSerializer
        return serializer

    @action(
        methods=["POST"],
        detail=True,
        url_path="upload-image",
        # permission_classes=[IsAdminUser]
    )
    def upload_image(self, request, pk=None) -> Response:
        """Endpoint for uploading image to User Profile"""
        train = self.get_object()
        serializer = self.get_serializer(train, data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data, status=status.HTTP_200_OK)
