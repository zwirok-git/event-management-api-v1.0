from django.contrib.auth import get_user_model
from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models
from django.utils import timezone


User = get_user_model()


class Event(models.Model):
    title = models.CharField(max_length=255)
    description = models.TextField()
    start_date = models.DateTimeField()
    location = models.CharField(max_length=255)

    members = models.ManyToManyField(
        User,
        related_name="registered_events",
        blank=True
    )
    organizer = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="organized_events",
    )

    max_members = models.PositiveIntegerField(
        validators=[
            MinValueValidator(1),
            MaxValueValidator(10_000)
        ]
    )

    is_archived = models.BooleanField(default=False)
    created_at = models.DateTimeField(db_index=True, default=timezone.now)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["start_date", "title"]
        constraints = [
            models.UniqueConstraint(
                fields=["organizer", "title", "start_date", "location"],
                name="unique_events",
            )
        ]
