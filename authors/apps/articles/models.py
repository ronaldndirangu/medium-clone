"""
Module contains Models for article related tables
"""
from authors.apps.core.models import TimestampModel
from django.db import models
from django.db.models.signals import pre_save
from django.utils.text import slugify
from authors.apps.profiles.models import Profile


class Article(TimestampModel):
    """
    Defines the articles table and functionality
    """
    title = models.CharField(db_index=True, max_length=255)
    slug = models.SlugField(db_index=True, max_length=255, unique=True)
    body = models.TextField()
    description = models.TextField()
    image_url = models.URLField(blank=True, null=True)
    author = models.ForeignKey(Profile, on_delete=models.CASCADE)

    def __str__(self):
        return self.title


class Ratings(models.Model):
    """
    Defines the ratings fields for a rater
    """
    rater = models.ForeignKey(
        Profile, on_delete=models.CASCADE)
    article = models.ForeignKey(
        Article,  on_delete=models.CASCADE, related_name="rating")
    counter = models.IntegerField(default=0)
    stars = models.IntegerField(null=False)


def pre_save_article_receiver(sender, instance, *args, **kwargs):
    """
    Method uses a signal to add slug to an article before saving it
    A slug will always be unique
    """
    if instance.slug:
        return
    slug = slugify(instance.title)
    num = 1
    unique_slug = slug
    # loops until a unique slug is generated
    while Article.objects.filter(slug=unique_slug).exists():
        unique_slug = "%s-%s" % (slug, num)
        num += 1

    instance.slug = unique_slug


# Called just before a save is made in the db
pre_save.connect(pre_save_article_receiver, sender=Article)
