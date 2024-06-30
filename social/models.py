import os
from datetime import datetime
from django.db import models
from django.utils.text import slugify
from social_media_api import settings


def profile_image_path(instance, filename):
    _, extension = os.path.splitext(filename)
    upload_datetime = datetime.now().strftime("%Y%m%d%H%M")
    return os.path.join(
        "images",
        f"{slugify(instance.owner)}" f"--{upload_datetime}{extension}",
    )


class UserProfile(models.Model):

    owner = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="profile",
    )
    profile_picture = models.ImageField(
        null=True,
        blank=True,
        upload_to=profile_image_path
    )
    bio = models.TextField(
        blank=True
    )
    birth_date = models.DateField(
        null=True, blank=True
    )
    location = models.CharField(
        max_length=255, null=True, blank=True
    )
    website = models.URLField(
        max_length=255, null=True, blank=True
    )
    phone_number = models.CharField(
        max_length=20, null=True, blank=True
    )
    social_links = models.JSONField(
        null=True, blank=True,
    )
    created_at = models.DateTimeField(
        auto_now_add=True,
    )
    updated_at = models.DateTimeField(
        auto_now=True,
    )
    followers = models.ManyToManyField(
        "self", blank=True, related_name="user_followers", symmetrical=False
    )
    following = models.ManyToManyField(
        "self", blank=True, related_name="user_following", symmetrical=False
    )

    def __str__(self) -> str:
        return self.owner.username


def post_image_path(instance, filename):
    _, extension = os.path.splitext(filename)
    upload_datetime = datetime.now().strftime("%Y%m%d%H%M")
    return os.path.join(
        "post, images",
        f"{slugify(instance.owner)}" f"--{upload_datetime}{extension}",
    )


class Post(models.Model):

    owner = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="post"
    )
    text = models.TextField(blank=True, null=True)
    image = models.ImageField(
        blank=True,
        null=True,
        upload_to=post_image_path
    )
    hashtags = models.CharField(max_length=255, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.owner.username} - {self.text[:30]}"
