from django.shortcuts import get_object_or_404
from rest_framework import serializers

from social.models import Post, SocialLink, UserProfile
from user.models import User


class SocialLinkSerializer(serializers.ModelSerializer):

    class Meta:
        model = SocialLink
        fields = (
            "platform",
            "url",
        )


class UserProfileSerializer(serializers.ModelSerializer):
    social_links = SocialLinkSerializer(
        many=True,
        read_only=False,
        required=False
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
        )
        read_only_fields = ("owner", "created_at", "updated_at")

    def create(self, validated_data) -> UserProfile:
        social_links_data = validated_data.pop("social_links")

        profile = UserProfile.objects.create(**validated_data)
        self._create_or_update_social_links(profile, social_links_data)

        return profile

    def update(self, instance, validated_data) -> UserProfile:
        social_links_data = validated_data.pop("social_links", None)

        for attr, value in validated_data.items():
            setattr(instance, attr, value)

        instance.save()
        instance.social_links.all().delete()
        self._create_or_update_social_links(instance, social_links_data)

        return instance

    def _create_or_update_social_links(self, profile, social_links_data):
        if social_links_data:
            SocialLink.objects.bulk_create(
                [SocialLink(profile=profile, **link_data)
                 for link_data in social_links_data]
            )


class UserProfileDetailSerializer(serializers.ModelSerializer):

    owner = serializers.SlugRelatedField(read_only=True, slug_field="username")
    social_links = SocialLinkSerializer(many=True, read_only=True)

    user_followers = serializers.SerializerMethodField()
    user_following = serializers.SerializerMethodField()

    def get_user_followers(self, obj) -> list:
        return [follower.owner.username for follower in obj.followers.all()]

    def get_user_following(self, obj) -> list:
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


class UserProfileListSerializer(serializers.ModelSerializer):
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
            "location",
            "created_at",
            "updated_at",
            "followers_count",
            "following_count",
        )
        read_only_fields = ("owner", "creared_at", "updated_at")


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

    def save(self, *args, **kwargs) -> None:
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


class PostSerializer(serializers.ModelSerializer):

    class Meta:
        model = Post
        fields = (
            "id",
            "owner",
            "text",
            "image",
            "hashtags",
            "created_at",
            "updated_at",
        )
        read_only_fields = ("owner", "created_at", "updated_at")


class PostListSerializer(PostSerializer):
    owner = serializers.CharField(
        source="owner.username",
        read_only=True

    )
