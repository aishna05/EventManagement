from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import EventViewSet, RSVPViewSet, ReviewViewSet , RegisterView, home  

router = DefaultRouter()
router.register(r"events", EventViewSet, basename="event")
router.register(r"rsvp", RSVPViewSet, basename="rsvp")
router.register(r"reviews", ReviewViewSet, basename="review")

urlpatterns = [
    path("", include(router.urls)),
    path("home", home, name="home"),
    path("auth/register/", RegisterView.as_view(), name="register"),
]
