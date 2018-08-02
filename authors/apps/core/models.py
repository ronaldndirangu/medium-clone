from django.db import models


class TimestampModel(models.Model):
    """
    A class to auto add `created_at` and `updated_at`
    timestamp fields to model(s)
    """
    # timestamp for when an entry is made into a model(table)
    created_at = models.DateTimeField(auto_now_add=True)
    # timestamp updated any time model(table) field is updated
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True
        # By default, any model that inherits from `TimestampedModel` should
        # be ordered in reverse-chronological order. We can override this on a
        # per-model basis as needed, but reverse-chronological is a good
        # default ordering for most models.
        ordering = ['-created_at', '-updated_at']
