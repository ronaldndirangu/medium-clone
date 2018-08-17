
from django.db import models
from django.conf import settings

# User = settings.AUTH_USER_MODEL


class Profile(models.Model):
    """This class represents the user profile model."""

    #resticting user to have one and only one profile
    user = models.OneToOneField(
        'authentication.User', on_delete=models.CASCADE
    )
    bio = models.TextField(blank=True)
    image = models.URLField(blank=True)
    interests = models.CharField(max_length=255, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    favorites = models.ManyToManyField('articles.Article', symmetrical=False, related_name='users_fav_articles')
    follows = models.ManyToManyField(
        'self',
        related_name='follower',
        symmetrical=False
    )
    
    def __str__(self):
        return '{}'.format(self.user.email)

    def favorite(self, article):
        self.favorites.add(article)

    def unfavorite(self, article):
        self.favorites.remove(article)

    def follow(self, profile):
        """Follow another user if not already following"""
        self.follows.add(profile)

    def unfollow(self, profile):
        """Unfollow another user if followed"""
        self.follows.remove(profile)

    def is_following(self, profile):
        """Returns True if a user is followed by active user. False otherwise."""
        return self.follows.filter(pk=profile.pk).exists()

    def is_follower(self, profile):
        """Returns True if a user is following active user; False otherwise."""
        return self.follower.filter(pk=profile.pk).exists()
