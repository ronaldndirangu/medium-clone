"""
Module contains Models for article related tables
"""
from datetime import datetime
from django.db import models
from django.db.models.signals import post_save, pre_save
from django.utils.text import slugify
from mptt.models import MPTTModel, TreeForeignKey
from notifications.signals import notify
from authors.apps.authentication.models import User
from authors.apps.profiles.models import Profile
from authors.apps.core.models import TimestampModel
from authors.apps.articles.notification_emails import SendEmail


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
    likes = models.ManyToManyField(User, related_name='likes', blank=True)
    dislikes = models.ManyToManyField(
        User, related_name='dislikes', blank=True)
    tags = models.ManyToManyField(
        'articles.Tag', related_name='articles'
    )

    def __str__(self):
        return self.title


class Comment(MPTTModel,TimestampModel):
    """
    Defines the comments table for an article
    """
    body = models.TextField()
    comment_likes = models.ManyToManyField(User, related_name='comment_likes', blank=True)
    comment_dislikes = models.ManyToManyField(User, related_name='comment_dislikes', blank=True)
    parent = TreeForeignKey('self',related_name='reply_set',null=True ,on_delete=models.CASCADE)
    article = models.ForeignKey(
        'articles.Article', related_name='comments', on_delete=models.CASCADE
    )

    author = models.ForeignKey(
        'profiles.Profile', related_name='comments', on_delete=models.CASCADE
    )


class CommentEditHistory(models.Model):
    """
    Define comment_edit_history table and functionality
    """
    body = models.TextField(null=False)
    comment = models.ForeignKey(Comment, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=False)


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


class Tag(TimestampModel):
    """This class defines the tag model"""

    tag = models.CharField(max_length=255)
    slug = models.SlugField(db_index=True, unique=True)

    def __str__(self):
        return '{}'.format(self.tag)
      
      
class Bookmarks(models.Model):
    """
    Defines the model used for storing bookmarked articles
    """
    user = models.ForeignKey(Profile, on_delete=models.CASCADE)
    article = models.ForeignKey(Article, on_delete=models.CASCADE, related_name='bookmarked')
    date = models.DateTimeField(default=datetime.now, blank=True)        


def pre_save_article_receiver(sender, instance, *args, **kwargs):
    """
    Method uses a signal to add slug to an article before saving it
    A slug will always be unique
    """
    if instance.slug:
        return instance
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


def notify_followers_new_article(sender, instance, created, **kwargs):
    """
    Notify followers of new article posted.
    """
    user = User.objects.get(pk=instance.author.id)
    title = instance.title
    author = instance.author.user.get_full_name()
    recipients = []
    for follower in user.profile.follower.all():
        if follower.user.get_notified:
            recipients.append(follower.user)
        SendEmail().send_article_notification_email(
            follower.user.email, title, author)
    notify.send(instance, recipient=recipients, verb='was posted', slug=instance.slug,
                title=instance.title, author=instance.author.user.get_full_name())

post_save.connect(notify_followers_new_article, sender=Article)



def notify_comments_favorited_articles(sender, instance, created, **kwargs):
    """
    Signal that notifies users on comments on favorited items
    """
    users = instance.article.users_fav_articles.all()
    title = instance.article.title
    slug = instance.article.slug
    author = instance.article.author.user.get_full_name()
    commenter = instance.author.user.get_full_name()
    comment = instance.body
    recipients = []
    for user in users:
        if user.user.get_notified:
            recipients.append(user.user)
        SendEmail().send_comment_notification_email(
            user.user.email, title, author, commenter)
    notify.send(instance, recipient=recipients,
                verb='was commented on', slug=slug, title=title, author=author, commenter=commenter, comment=comment)


post_save.connect(notify_comments_favorited_articles, sender=Comment)
