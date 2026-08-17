from celery import shared_task
from django.utils import timezone

from events.models import Event


@shared_task
def archive_finished_events():
    updated_count = Event.objects.filter(
        start_date__lte=timezone.now(),
        is_archived=False,
    ).update(is_archived=True)

    return updated_count
