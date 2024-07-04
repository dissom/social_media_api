import os
from datetime import datetime
from django.db import models
from django.utils.text import slugify
from social_media_api import settings


def profile_image_path(instance, filename):
    _, extension = os.path.splitext(filename)
    upload_datetime = datetime.now().strftime("%Y%m%d%H%M")
    return os.path.join(
        "profile", "images",
        f"{slugify(instance.owner)}" f"--{upload_datetime}{extension}",
    )


def post_image_path(instance, filename):
    _, extension = os.path.splitext(filename)
    upload_datetime = datetime.now().strftime("%Y%m%d%H%M")
    return os.path.join(
        "post", "images",
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


class SocialLink(models.Model):
    profile = models.ForeignKey(
        UserProfile,
        on_delete=models.CASCADE,
        related_name="social_links"
    )
    platform = models.CharField(max_length=255)
    url = models.URLField(max_length=255)

    def __str__(self):
        return f"{self.platform}: {self.url}"


class Post(models.Model):

    owner = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="posts"
    )
    title = models.CharField(max_length=255)
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
        return f"{self.owner.username} - {self.title}"


class Comment(models.Model):

    post = models.ForeignKey(
        Post,
        related_name="comments",
        on_delete=models.CASCADE
    )
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        related_name="comments",
        on_delete=models.CASCADE
    )
    text = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self) -> str:
        return f"{self.user.username} - {self.text[:50]}"


class Like(models.Model):

    class ActionChoices(models.TextChoices):
        LIKE = "like", "Like"
        DISLIKE = "dislike", "Dislike"

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="likes",
    )
    post = models.ForeignKey(
        Post,
        on_delete=models.CASCADE,
        related_name="likes"
    )
    action = models.CharField(
        max_length=7,
        choices=ActionChoices.choices
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ("user", "post")

    def __str__(self):
        return f"{self.user.username} {self.action}ed {self.post.title}"
