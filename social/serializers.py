from django.shortcuts import get_object_or_404
from rest_framework import serializers

from social.models import UserProfile
from user.models import User


class UserProfileSerializer(serializers.ModelSerializer):

    class Meta:
        model = UserProfile
        fields = (
            "id",
            "owner",
            "profile_picture",
            "bio",
            "birth_date",
            "location",
            "website",
            "phone_number",
            "social_links",
            "created_at",
            "updated_at",
        )
        read_only_fields = ("owner", "creared_at", "updated_at")


class UserProfileDetailSerializer(serializers.ModelSerializer):

    owner = serializers.SlugRelatedField(read_only=True, slug_field="username")

    user_followers = serializers.SerializerMethodField()
    user_following = serializers.SerializerMethodField()

    def get_user_followers(self, obj):
        return [follower.owner.username for follower in obj.followers.all()]

    def get_user_following(self, obj):
        return [following.owner.username for following in obj.following.all()]

    class Meta:
        model = UserProfile
        fields = (
            "id",
            "owner",
            "profile_picture",
            "bio",
            "birth_date",
            "location",
            "website",
            "phone_number",
            "social_links",
            "created_at",
            "updated_at",
            "user_followers",
            "user_following",
        )
        read_only_fields = ("owner", "creared_at", "updated_at")


class UserProfileListSerializerView(serializers.ModelSerializer):
    owner = serializers.SlugRelatedField(
        read_only=True,
        slug_field="username"
    )
    followers_count = serializers.IntegerField(
        read_only=True,
        source="followers.count"
    )
    following_count = serializers.IntegerField(
        read_only=True,
        source="following.count"
    )

    class Meta:
        model = UserProfile
        fields = (
            "id",
            "owner",
            "profile_picture",
            "bio",
            "birth_date",
            "location",
            "website",
            "phone_number",
            "social_links",
            "created_at",
            "updated_at",
            "followers_count",
            "following_count",
        )
        read_only_fields = ("owner", "creared_at", "updated_at")


class SocialLinkSerializer(serializers.Serializer):
    platform = serializers.CharField(max_length=255)
    link = serializers.URLField()


class FollowUnfollowSerializer(serializers.ModelSerializer):
    user_id = serializers.IntegerField()
    action = serializers.ChoiceField(choices=["follow", "unfollow"])

    class Meta:
        model = User
        fields = (
            "user_id",
            "action",
        )

    def validate(self, attrs):
        data = super(FollowUnfollowSerializer, self).validate(attrs)
        user_to_follow_unfollow = get_object_or_404(User, pk=attrs["user_id"])

        if user_to_follow_unfollow == self.context["request"].user:
            raise serializers.ValidationError(
                "You cannot follow/unfollow yourself."
            )
        data["user_to_follow_unfollow"] = user_to_follow_unfollow
        return data

    def save(self, *args, **kwargs):
        action = self.validated_data["action"]
        user_to_follow_unfollow = self.validated_data[
            "user_to_follow_unfollow"
        ]
        user_profile = get_object_or_404(
            UserProfile,
            owner=self.context["request"].user
        )
        follow_profile = get_object_or_404(
            UserProfile,
            owner=user_to_follow_unfollow
        )

        if action == "follow":
            if user_profile.following.filter(id=follow_profile.id).exists():
                raise serializers.ValidationError(
                    "Already following this user."
                )
            user_profile.following.add(follow_profile)
            user_to_follow_unfollow.profile.followers.add(user_profile)

        elif action == "unfollow":
            if not user_profile.following.filter(
                id=follow_profile.id
            ).exists():
                raise serializers.ValidationError(
                    "You are not following this user."
                )
            user_profile.following.remove(follow_profile)
            user_to_follow_unfollow.profile.followers.remove(user_profile)
