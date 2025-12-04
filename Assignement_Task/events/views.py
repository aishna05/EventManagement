from django.shortcuts import render

# Create your views here.
from rest_framework import viewsets, status
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.decorators import action

from .models import Event, RSVP, Review
from .serializers import EventSerializer, RSVPSerializer, ReviewSerializer
from .permissions import IsOrganizerOrReadOnly


# -----------------------------------
# EVENT VIEWSET
# -----------------------------------
class EventViewSet(viewsets.ModelViewSet):
    queryset = Event.objects.filter(is_public=True)
    serializer_class = EventSerializer

    def get_permissions(self):
        if self.action in ["create"]:
            return [IsAuthenticated()]
        elif self.action in ["update", "partial_update", "destroy"]:
            return [IsAuthenticated(), IsOrganizerOrReadOnly()]
        return [AllowAny()]

    def perform_create(self, serializer):
        serializer.save(owner=self.request.user)


    # -----------------------------
    # CUSTOM ACTION FOR RSVP
    # -----------------------------
    @action(detail=True, methods=["post"], permission_classes=[IsAuthenticated])
    def rsvp(self, request, pk=None):
        event = self.get_object()
        serializer = RSVPSerializer(
            data=request.data,
            context={"request": request, "event": event}
        )
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data, status=201)

    # -----------------------------
    # LIST REVIEWS FOR EVENT
    # -----------------------------
    @action(detail=True, methods=["get"], permission_classes=[AllowAny])
    def reviews(self, request, pk=None):
        event = self.get_object()
        reviews = event.reviews.all()
        serializer = ReviewSerializer(reviews, many=True)
        return Response(serializer.data)


# -----------------------------------
# RSVP UPDATE VIEW
# -----------------------------------
class RSVPViewSet(viewsets.ModelViewSet):
    queryset = RSVP.objects.all()
    serializer_class = RSVPSerializer
    permission_classes = [IsAuthenticated]

    http_method_names = ["patch"]  # Only update allowed

    def get_queryset(self):
        return RSVP.objects.filter(user=self.request.user)


# -----------------------------------
# REVIEW VIEWSET
# -----------------------------------
class ReviewViewSet(viewsets.ModelViewSet):
    queryset = Review.objects.all()
    serializer_class = ReviewSerializer
    permission_classes = [IsAuthenticated]
    http_method_names = ["post"]

    def create(self, request, *args, **kwargs):
        event_id = request.data.get("event_id")
        event = Event.objects.get(id=event_id)

        serializer = ReviewSerializer(
            data=request.data,
            context={"request": request, "event": event}
        )
        serializer.is_valid(raise_exception=True)
        serializer.save()

        return Response(serializer.data, status=201)
