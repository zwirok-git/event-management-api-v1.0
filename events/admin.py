from django.contrib import admin

from events.models import Event


@admin.register(Event)
class EventAdmin(admin.ModelAdmin):
    list_display = (
        "title",
        "organizer",
        "start_date",
        "location",
        "max_members",
        "is_archived",
    )

    list_filter = (
        "is_archived",
        "start_date",
        "location",
    )

    search_fields = (
        "title",
        "location",
        "organizer__username",
    )

    ordering = (
        "-start_date",
    )
