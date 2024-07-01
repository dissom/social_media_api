from django.db.models import Q
from rest_framework import viewsets, status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from django.shortcuts import get_object_or_404

from permissions import IsOwnerOrReadOnly
from social.models import Post, UserProfile
from social.serializers import (
    FollowUnfollowSerializer,
    PostListSerializer,
    PostSerializer,
    UserProfileDetailSerializer,
    UserProfileListSerializerView,
    UserProfileSerializer,
)


class UserProfileView(viewsets.ModelViewSet):

    queryset = UserProfile.objects.all()
    serializer_class = UserProfileSerializer
    permission_classes = (
        IsOwnerOrReadOnly,
        IsAuthenticated,
    )

    def get_queryset(self):
        """Retrieve profiles with filters by owner"""
        queryset = self.queryset.filter(
            Q(owner=self.request.user.id)
            | Q(followers=self.request.user.id)
            | Q(following=self.request.user.id)
        ).distinct()

        owner = self.request.query_params.get("owner")
        if owner:
            owner = owner.split(",")
            print(owner)
            queryset = queryset.filter(owner__username__in=owner)
        return queryset

    def get_serializer_class(self):
        serializer = self.serializer_class
        if self.action == "retrieve":
            serializer = UserProfileDetailSerializer
        if self.action == "list":
            serializer = UserProfileListSerializerView
        return serializer

    def perform_create(self, serializer):
        serializer.save(owner=self.request.user)

    @action(
        methods=["POST"],
        detail=True,
        url_path="upload-image",
    )
    def upload_image(self, request, pk=None) -> Response:
        """Endpoint for uploading image to User Profile"""
        profile = self.get_object()
        serializer = self.get_serializer(profile, data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data, status=status.HTTP_200_OK)


class FollowUnfollowView(APIView):
    serializer_class = FollowUnfollowSerializer

    def other_profile(self, pk):
        return get_object_or_404(UserProfile, id=pk)

    def post(self, request) -> Response:
        user_id = request.data.get("user_id")
        action = request.data.get("action")

        data = {"user_id": user_id, "action": action}
        serializer = FollowUnfollowSerializer(
            data=data,
            context={"request": request}
        )
        serializer.is_valid(raise_exception=True)
        serializer.save()
        print(serializer.data)
        return Response(
            {
                "message": f"Successfully {action}ed "
                f"{self.other_profile(user_id)}"
            },
            status=status.HTTP_200_OK
        )


class PostViewSet(viewsets.ModelViewSet):
    queryset = Post.objects.all()
    serializer_class = PostSerializer
    permission_classes = (
        IsOwnerOrReadOnly,
        IsAuthenticated,
    )

    def get_queryset(self):
        """
        Retrieve posts filtered by following users, with search by hashtags
        """
        queryset = self.queryset
        user = self.request.user

        following_users = user.profile.following.values_list(
            "owner", flat=True
        )
        queryset = queryset.filter(
            Q(owner__in=following_users) | Q(owner=user)
        )

        hashtag_params = self.request.query_params.get("hashtag")

        if hashtag_params:
            hashtags_params = hashtag_params.split(",")
            queryset = queryset.filter(hashtags__in=hashtags_params)

        return queryset.distinct()

    def get_serializer_class(self):
        serializer = self.serializer_class
        if self.action == "list":
            serializer = PostListSerializer
        return serializer

    def perform_create(self, serializer):
        serializer.save(owner=self.request.user)
