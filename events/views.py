from django.db.models import Count
from django.utils import timezone
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import mixins, viewsets, status
from rest_framework.decorators import action
from rest_framework.filters import SearchFilter, OrderingFilter
from rest_framework.permissions import AllowAny
from rest_framework.response import Response

from events.models import Event
from events.serializers import (
    EventListSerializer,
    CreateEventSerializer,
    EventOrganizerDetailSerializer,
    PublicDetailEventSerializer
)


class EventViewSet(
    mixins.CreateModelMixin,
    mixins.ListModelMixin,
    mixins.RetrieveModelMixin,
    viewsets.GenericViewSet
):
    queryset = Event.objects.all()

    filter_backends = [
        DjangoFilterBackend,
        SearchFilter,
        OrderingFilter,
    ]

    filterset_fields = ["location", "organizer"]

    search_fields = [
        "title",
        "location",
        "organizer"
    ]

    ordering_fields = [
        "start_date",
        "title",
        "max_members",
    ]

    def retrieve(self, request, *args, **kwargs):
        event = self.get_object()

        if event.organizer == request.user:
            serializer_class = EventOrganizerDetailSerializer
        else:
            serializer_class = PublicDetailEventSerializer

        serializer = serializer_class(
            event,
            context=self.get_serializer_context(),
        )

        return Response(serializer.data)

    def perform_create(self, serializer):
        serializer.save(organizer=self.request.user)

    def get_serializer_class(self):
        if self.action == "list":
            return EventListSerializer
        if self.action == "create":
            return CreateEventSerializer

        return PublicDetailEventSerializer

    def get_permissions(self):
        if self.action in ("list", "retrieve"):
            return [AllowAny()]

        return super().get_permissions()

    def get_queryset(self):
        return (
            Event.objects
            .filter(is_archived=False)
            .select_related("organizer")
            .prefetch_related("members")
            .annotate(members_count=Count("members"))
        )

    @action(detail=True, methods=["post"])
    def register(self, request, pk=None):
        event = self.get_object()

        if self.request.user == event.organizer:
            return Response(
                {"detail": "Organizer cannot register for their own event."},
                status=status.HTTP_403_BAD_REQUEST
            )

        if event.members.filter(pk=request.user.pk).exists():
            return Response(
                {"detail": "You are already registered for this event."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        if event.members.count() >= event.max_members:
            return Response(
                {"detail": "The event is full."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        if event.start_date <= timezone.now():
            return Response(
                {"detail": "Registration for this event is closed."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        event.members.add(request.user)

        return Response(
            {"detail": "Successfully registered for the event."},
            status=status.HTTP_201_CREATED,
        )

    @action(detail=True, methods=["delete"])
    def unregister(self, request, pk=None):
        event = self.get_object()

        if not event.members.filter(pk=request.user.pk).exists():
            return Response(
                {"detail": "You are not registered for this event."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        event.members.remove(request.user)

        return Response(status=status.HTTP_204_NO_CONTENT)
