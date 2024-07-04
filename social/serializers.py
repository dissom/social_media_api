from django.shortcuts import get_object_or_404
from django.contrib.auth import get_user_model
from rest_framework import serializers

from social.models import (
    Comment,
    Like,
    Post,
    SocialLink,
    UserProfile
)


class SocialLinkSerializer(serializers.ModelSerializer):

    class Meta:
        model = SocialLink
        fields = (
            "platform",
            "url",
        )


class CommentSerializer(serializers.ModelSerializer):

    class Meta:
        model = Comment
        fields = ("post", "text", "created_at")


class CommentListSerializer(serializers.ModelSerializer):

    class Meta:
        model = Comment
        fields = ("text", "created_at")


class PostSerializer(serializers.ModelSerializer):

    class Meta:
        model = Post
        fields = (
            "id",
            "owner",
            "title",
            "text",
            "image",
            "hashtags",
            "published",
            "publish_date",
            "created_at",
            "updated_at",
        )
        read_only_fields = (
            "owner",
            "published",
            "created_at",
            "updated_at"
        )


class PostListSerializer(serializers.ModelSerializer):
    owner = serializers.CharField(
        source="owner.username",
        read_only=True
    )
    likes = serializers.CharField(read_only=True, source="likes.count")

    comments = CommentListSerializer(many=True, read_only=True)

    class Meta:
        model = Post
        fields = (
            "id",
            "title",
            "image",
            "text",
            "hashtags",
            "owner",
            "published",
            "created_at",
            "updated_at",
            "comments",
            "likes",
        )
        read_only_fields = (
            "owner",
            "published",
            "created_at",
            "updated_at"
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

    posts = serializers.SerializerMethodField()

    user_followers = serializers.SerializerMethodField()
    user_following = serializers.SerializerMethodField()

    def get_posts(self, obj):
        posts = Post.objects.filter(owner=obj.owner)
        return [post.title for post in posts]

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
            "posts",
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
        model = get_user_model()
        fields = (
            "user_id",
            "action",
        )

    def validate(self, attrs):
        data = super(FollowUnfollowSerializer, self).validate(attrs)
        user_to_follow_unfollow = get_object_or_404(
            get_user_model(),
            pk=attrs["user_id"]
        )

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


class LikeSerializer(serializers.ModelSerializer):

    class Meta:
        model = Like
        fields = (
            "post",
            "action",
        )

    def validate(self, attrs):
        data = super(LikeSerializer, self).validate(attrs)
        post = attrs["post"]
        action = attrs["action"]
        user = self.context["request"].user

        if action == "like" and Like.objects.filter(
            user=user,
            post=post
        ).exists():
            raise serializers.ValidationError(
                "You have already liked this post."
            )
        if action == "dislike" and not Like.objects.filter(
            user=user,
            post=post
        ).exists():
            raise serializers.ValidationError(
                "You have not liked this post."
            )

        return data

    def save(self, **kwargs):
        action = self.validated_data["action"]
        post = self.validated_data["post"]
        user = self.context["request"].user

        if action == "like":
            Like.objects.create(user=user, post=post, action=action)
        else:
            Like.objects.filter(user=user, post=post).delete()

        return post
