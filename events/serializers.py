from datetime import datetime

from django.utils import timezone
from rest_framework import serializers

from events.models import Event
from users.serializers import (
    UserEventListSerializer,
    UserOrganizerInfoSerializer,
)


class EventCreateSerializer(serializers.ModelSerializer):
    start_date = serializers.DateTimeField(
        format="%Y-%m-%d %H:%M",
    )

    class Meta:
        model = Event
        fields = [
            "id",
            "title",
            "description",
            "start_date",
            "location",
            "max_members",
        ]

    def validate_start_date(self, date: datetime) -> datetime:
        if date < timezone.now():
            raise serializers.ValidationError(
                "The event start date cannot be in the past."
            )

        return date

    def validate_location(self, location_name: str) -> str:
        clean_location_name = location_name.strip()

        if len(clean_location_name) < 3:
            raise serializers.ValidationError(
                "Location name is too short."
            )

        return clean_location_name

    def validate_title(self, title_text: str) -> str:
        clean_title = title_text.strip()

        if len(clean_title) < 3:
            raise serializers.ValidationError(
                "The title is too short. It must be at least 3"
                " characters long."
            )

        if clean_title.isupper():
            raise serializers.ValidationError(
                "The title cannot be written in ALL CAPS."
            )

        return clean_title

    def validate(self, attrs: dict) -> dict:
        organizer = self.context["request"].user

        title = attrs.get(
            "title",
            self.instance.title if self.instance else None,
        )
        location = attrs.get(
            "location",
            self.instance.location if self.instance else None,
        )
        start_date = attrs.get(
            "start_date",
            self.instance.start_date if self.instance else None,
        )

        duplicate_exists = Event.objects.filter(
            organizer=organizer,
            title__iexact=title,
            location__iexact=location,
            start_date=start_date,
        )

        if self.instance:
            duplicate_exists = duplicate_exists.exclude(
                pk=self.instance.pk
            )

        if duplicate_exists.exists():
            raise serializers.ValidationError(
                {
                    "start_date": (
                        "This organizer already has an event "
                        "with the same title, location and start time."
                    )
                }
            )

        return attrs


class EventDetailSerializer(serializers.ModelSerializer):
    organizer = UserOrganizerInfoSerializer(read_only=True)
    members_count = serializers.IntegerField(read_only=True)
    start_date = serializers.DateTimeField(format="%Y-%m-%d %H:%M")
    left_places = serializers.SerializerMethodField()
    is_registered = serializers.SerializerMethodField()

    class Meta:
        model = Event
        fields = [
            "id",
            "title",
            "description",
            "start_date",
            "location",
            "members_count",
            "max_members",
            "left_places",
            "is_registered",
            "organizer"
        ]

    def get_left_places(self, obj: Event) -> int:
        return obj.max_members - obj.members_count

    def get_is_registered(self, obj: Event) -> bool:
        request = self.context["request"]

        if not request.user.is_authenticated:
            return False

        return obj.members.filter(
            pk=request.user.pk
        ).exists()


class EventOrganizerDetailSerializer(EventDetailSerializer):
    members = UserEventListSerializer(
        many=True,
        read_only=True,
    )

    class Meta(EventDetailSerializer.Meta):
        fields = EventDetailSerializer.Meta.fields + [
            "members",
        ]


class EventListSerializer(serializers.ModelSerializer):
    members_count = serializers.IntegerField(read_only=True)
    start_date = serializers.DateTimeField(format="%Y-%m-%d %H:%M")
    organizer = UserOrganizerInfoSerializer(read_only=True)

    class Meta:
        model = Event
        fields = [
            "id",
            "title",
            "start_date",
            "location",
            "members_count",
            "max_members",
            "organizer"
        ]
