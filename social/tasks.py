from datetime import date
from celery import shared_task
from django.db.models import Q

from social.models import Post


@shared_task
def create_and_schedule_post():
    unpublished_posts = Post.objects.filter(
        published=False,
        publish_date=date.today()
    )
    for post in unpublished_posts:
        post.published = True
        post.save()
    return (
        f"Successfully published {unpublished_posts.count()} posts."
    )
