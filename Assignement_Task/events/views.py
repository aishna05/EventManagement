# Create your views here.
from django.shortcuts import get_object_or_404
from rest_framework import viewsets, status, filters
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.decorators import action
from django_filters.rest_framework import DjangoFilterBackend

from .models import Event, RSVP, Review
from .serializers import EventSerializer, RSVPSerializer, ReviewSerializer
from .permissions import IsOrganizerOrReadOnly, IsInvitedOrPublic

class EventViewSet(viewsets.ModelViewSet):
    queryset = Event.objects.all()
    serializer_class = EventSerializer

    # 🔍 Search + Filter + Sorting Support
    filter_backends = [filters.SearchFilter, DjangoFilterBackend, filters.OrderingFilter]
    search_fields = ["title", "location", "owner__username"]
    filterset_fields = ["is_public", "location"]
    ordering_fields = ["start_time", "title"]
    ordering = ["start_time"]
    permission_classes = [AllowAny]

    def get_permissions(self):

        # CREATE → must be authenticated
        if self.action == "create":
            return [IsAuthenticated()]

        # UPDATE/DELETE → only organizer
        if self.action in ["update", "partial_update", "destroy"]:
            return [IsAuthenticated(), IsOrganizerOrReadOnly()]

        # RETRIEVE → apply private-event visibility check
        if self.action == "retrieve":
            return [IsInvitedOrPublic()]

        # LIST → public events only
        if self.action == "list":
            return [AllowAny()]

        return [permission() for permission in self.permission_classes]
    
    def get_queryset(self):
        """Public list → show only public events"""
        if self.action == "list":
            return Event.objects.filter(is_public=True)
        return Event.objects.all()

    def perform_create(self, serializer):
        serializer.save(owner=self.request.user)

    # -------------------------
    # RSVP
    # -------------------------
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

    # -------------------------
    # REVIEWS FOR EVENT
    # -------------------------
    @action(detail=True, methods=["get"], permission_classes=[AllowAny])
    def reviews(self, request, pk=None):
        event = self.get_object()
        reviews = event.reviews.all()

        # Pagination enabled
        page = self.paginate_queryset(reviews)
        if page is not None:
            serializer = ReviewSerializer(page, many=True)
            return self.get_paginated_response(serializer.data)

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
        event = get_object_or_404(Event, id=event_id)
        
        #  Only allow users who have RSVPed to this event
        has_rsvp = event.rsvps.filter(user=request.user).exists()
        if not has_rsvp:
            return Response(
                {"detail": "You must RSVP to this event before leaving a review."},
                status=status.HTTP_403_FORBIDDEN,
            )
        serializer = ReviewSerializer(
            data=request.data,
            context={"request": request, "event": event}
        )
        serializer.is_valid(raise_exception=True)
        serializer.save()

        return Response(serializer.data, status=201)
from rest_framework import generics, permissions
from .serializers import RegisterSerializer


class RegisterView(generics.CreateAPIView):
    """
    POST /api/auth/register/ → create a new user account
    """
    serializer_class = RegisterSerializer
    permission_classes = [permissions.AllowAny]
