from rest_framework import serializers
from rest_framework.authtoken.models import Token
from django.contrib.auth import get_user_model

from django.utils.translation import gettext as _


class UserSerializer(serializers.ModelSerializer):

    class Meta:
        model = get_user_model()
        fields = (
            "id",
            "email",
            "username",
            # "first_name",
            # "last_name",
            "is_active",
            "date_joined",
            "is_staff",
            "password",

        )
        read_only_fields = (
            "id",
            "is_staff",
            "is_active",
            "date_joined",
        )
        extra_kwargs = {
            "password": {
                "write_only": True,
                "min_length": 5,
                "label": _("Password"),
                "style": {"input_type": "password"}
            }
        }

    def create(self, validated_data):
        """Create User with encrypted password"""
        user = get_user_model().objects.create_user(**validated_data)
        Token.objects.create(user=user)
        return user

    def update(self, instance, validated_data):
        """Update User with encrypted password"""
        password = validated_data.pop("password", None)
        user = super().update(instance, validated_data)
        if password:
            user.set_password(password)
            user.save()
        return user


class UserDetailSerializer(UserSerializer):

    class Meta:
        model = get_user_model()
        fields = (
            "id",
            "email",
            # "username",
            "first_name",
            "last_name",
            "is_active",
            "date_joined",
            "is_staff",
            "password",

        )

        read_only_fields = (
            "id",
            "is_staff",
            "is_active",
            "date_joined",
        )
        extra_kwargs = {
            "password": {
                "write_only": True,
                "min_length": 5,
                "label": _("Password"),
                "style": {"input_type": "password"}
            }
        }


class UserLoginSerializer(serializers.ModelSerializer):

    class Meta:
        model = get_user_model()
        fields = ("id", "email", "password")
