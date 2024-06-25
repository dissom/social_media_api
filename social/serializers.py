from rest_framework import serializers

from social.models import UserProfile


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


class UserProfileDetailSerializer(UserProfileSerializer):

    owner = serializers.SlugRelatedField(
        read_only=True,
        slug_field="username"
    )
    followers = serializers.SerializerMethodField()
    following = serializers.SerializerMethodField()

    def get_followers(self, obj):
        from user.serializers import UserFollowingSerializer
        followers = obj.followers.all()
        return UserFollowingSerializer(followers, many=True).data

    def get_following(self, obj):
        from user.serializers import UserFollowingSerializer
        following = obj.following.all()
        return UserFollowingSerializer(following, many=True).data

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
            "followers",
            "following",
        )
        read_only_fields = ("owner", "creared_at", "updated_at")


class UserProfileListSerializerView(UserProfileDetailSerializer):
    owner = serializers.SlugRelatedField(
        read_only=True,
        slug_field="username"
    )
    followers = serializers.SerializerMethodField()
    following = serializers.SerializerMethodField()

    def get_followers(self, obj):
        followers = obj.followers.count()
        return followers

    def get_following(self, obj):
        following = obj.following.count()
        return following
