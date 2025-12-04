from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import EventViewSet, RSVPViewSet, ReviewViewSet

router = DefaultRouter()
router.register("events", EventViewSet, basename="events")
router.register("rsvp", RSVPViewSet, basename="rsvp")
router.register("reviews", ReviewViewSet, basename="reviews")

urlpatterns = [
    path("", include(router.urls)),
]
