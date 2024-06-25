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


class UserProfileListSerializerView(UserProfileDetailSerializer):
    owner = serializers.SlugRelatedField(
        read_only=True,
        slug_field="username"
    )
    followers = serializers.IntegerField(
        read_only=True,
        source="followers.count"
    )
    following = serializers.IntegerField(
        read_only=True,
        source="following.count"
    )
