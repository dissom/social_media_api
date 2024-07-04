from django.db.models import Q
from rest_framework import viewsets, status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from django.shortcuts import get_object_or_404
from drf_spectacular.utils import (
    extend_schema,
    OpenApiParameter,
    OpenApiTypes,
)

from permissions import IsOwnerOrFollower, IsOwnerOrReadOnly
from social.models import Comment, Like, Post, UserProfile
from social.serializers import (
    CommentSerializer,
    FollowUnfollowSerializer,
    LikeSerializer,
    PostListSerializer,
    PostSerializer,
    UserProfileDetailSerializer,
    UserProfileListSerializer,
    UserProfileSerializer,
)


class UserProfileView(viewsets.ModelViewSet):

    queryset = (
        UserProfile.objects.all()
        .prefetch_related("followers", "following")
    )
    serializer_class = UserProfileSerializer
    permission_classes = (
        IsOwnerOrFollower,
        IsAuthenticated,
    )

    def get_queryset(self):
        """
        Retrieve profiles with filters by owner,
        birth_date and location
        """
        queryset = self.queryset

        owner = self.request.query_params.get("owner")
        birth_date = self.request.query_params.get("birth_date")
        location = self.request.query_params.get("location")
        if owner:
            owner = owner.split(",")
            print(owner)
            queryset = queryset.filter(owner__username__in=owner)

        if birth_date:
            queryset = queryset.filter(birth_date=birth_date)

        if location:
            queryset = queryset.filter(location__icontains=location)

        return queryset

    @extend_schema(
        parameters=[
            OpenApiParameter(
                name="owner",
                type=OpenApiTypes.STR,
                description="Filter by owner (ex. ?owner=owner_username)"
            ),
            OpenApiParameter(
                name="birth_date",
                type=OpenApiTypes.DATE,
                description="Filter by birth_date "
                            "(ex. ?birth_date=2000-06-25)"
            ),
            OpenApiParameter(
                name="location",
                type=OpenApiTypes.STR,
                description="Filter by location (ex. ?location=owner_location)"
            ),
        ]
    )
    def list(self, request, *args, **kwargs):
        """Filtering by owner, birth_date, location"""
        return super().list(request, *args, **kwargs)

    def get_serializer_class(self):
        serializer = self.serializer_class
        if self.action == "retrieve":
            serializer = UserProfileDetailSerializer
        if self.action == "list":
            serializer = UserProfileListSerializer
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
        """Follow or unfollow profiles"""
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
    queryset = Post.objects.all().select_related("owner")
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
        created_at = self.request.query_params.get("created_at")
        updated_at = self.request.query_params.get("updated_at")

        if hashtag_params:
            hashtags_params = hashtag_params.split(",")
            queryset = queryset.filter(hashtags__in=hashtags_params)

        if created_at:
            print(created_at)
            queryset = queryset.filter(created_at__date=created_at)

        if updated_at:
            queryset = queryset.filter(updated_at__date=updated_at)

        return queryset.distinct()

    def get_serializer_class(self):
        serializer = self.serializer_class
        if self.action in ("list", "retrieve"):
            serializer = PostListSerializer
        return serializer

    def perform_create(self, serializer):
        serializer.save(owner=self.request.user)

    @extend_schema(
        parameters=[
            OpenApiParameter(
                name="hashtag",
                type=OpenApiTypes.STR,
                description="Filter by hashtag (ex. ?hashtag=example)",
            ),
            OpenApiParameter(
                name="created_at",
                type=OpenApiTypes.DATE,
                description="Filter by post create date "
                            "(ex. ?created_at=2024-06-24)",
            ),
            OpenApiParameter(
                name="updated_at",
                type=OpenApiTypes.DATE,
                description="Filter by post updated date "
                            "(ex. ?updated_at=2024-06-24)",
            ),
        ]
    )
    def list(self, request, *args, **kwargs):
        """Filtering by hashtag"""
        return super().list(request, *args, **kwargs)


class CommentViewSet(viewsets.ModelViewSet):
    queryset = Comment.objects.all().select_related()
    serializer_class = CommentSerializer

    def get_queryset(self):
        queryset = self.queryset
        user = self.request.user
        following_users = user.profile.following.values_list(
            "owner", flat=True
        )
        print(following_users)

        queryset = queryset.filter(
            Q(user__in=following_users) | Q(user=user)
        )
        return queryset

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)


class LikeViewSet(viewsets.ModelViewSet):
    queryset = Like.objects.all()
    serializer_class = LikeSerializer
