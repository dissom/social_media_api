from django.contrib import admin

from social.models import Post, SocialLink, UserProfile


admin.site.register(UserProfile)
admin.site.register(SocialLink)
admin.site.register(Post)
