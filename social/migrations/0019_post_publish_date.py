# Generated by Django 5.0.6 on 2024-07-04 13:48

import datetime
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("social", "0018_post_published"),
    ]

    operations = [
        migrations.AddField(
            model_name="post",
            name="publish_date",
            field=models.DateTimeField(default=datetime.datetime.now),
        ),
    ]
