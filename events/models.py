from django.contrib.auth import get_user_model
from django.core.validators import MaxValueValidator
from django.db import models
from core.models.base import BaseModel


User = get_user_model()


class Event(BaseModel):
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
        validators=[MaxValueValidator(10_000)]
    )
    is_archived = models.BooleanField(default=False)

    class Meta:
        ordering = ["start_date", "title"]
        constraints = [
            models.UniqueConstraint(
                fields=["organizer", "title", "start_date", "location"],
                name="unique_events",
            )
        ]
