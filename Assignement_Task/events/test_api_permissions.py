from django.urls import reverse
from rest_framework.test import APITestCase
from rest_framework import status
from django.contrib.auth import get_user_model

from events.models import Event, RSVP, Review

User = get_user_model()


class EventAPIPermissionsTests(APITestCase):
    def setUp(self):
        # Users
        self.owner = User.objects.create_user(
            username="owner", email="owner@example.com", password="pass1234"
        )
        self.invited = User.objects.create_user(
            username="invited", email="invited@example.com", password="pass1234"
        )
        self.stranger = User.objects.create_user(
            username="stranger", email="stranger@example.com", password="pass1234"
        )

        # Events
        self.public_event = Event.objects.create(
            owner=self.owner,
            title="Public Event",
            description="Public",
            location="Online",
            start_time="2025-01-01T10:00:00Z",
            end_time="2025-01-01T12:00:00Z",
            is_public=True,
        )

        self.private_event = Event.objects.create(
            owner=self.owner,
            title="Private Event",
            description="Private",
            location="Secret",
            start_time="2025-01-02T10:00:00Z",
            end_time="2025-01-02T12:00:00Z",
            is_public=False,
        )

        # RSVP: invited user is invited to private event
        self.rsvp_invited = RSVP.objects.create(
            user=self.invited,
            event=self.private_event,
            status="attending",
        )

    # -----------------------------
    # LIST: public events only
    # -----------------------------
    def test_list_events_public_only(self):
       url = reverse("event-list")
       response = self.client.get(url)

       self.assertEqual(response.status_code, status.HTTP_200_OK)

    # Handle both paginated and non-paginated responses
       data = response.data
       if isinstance(data, dict) and "results" in data:
           events = data["results"]
       else:
           events = data

       ids = [e["id"] for e in events]

       self.assertIn(self.public_event.id, ids)
       self.assertNotIn(self.private_event.id, ids)

    # -----------------------------
    # RETRIEVE: IsInvitedOrPublic
    # -----------------------------
    def test_retrieve_public_event_anonymous_allowed(self):
        url = reverse("event-detail", args=[self.public_event.id])
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_retrieve_private_event_anonymous_forbidden(self):
        url = reverse("event-detail", args=[self.private_event.id])
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
    def test_retrieve_private_event_invited_user_allowed(self):
        self.client.login(username="invited", password="pass1234")
        url = reverse("event-detail", args=[self.private_event.id])
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_retrieve_private_event_stranger_forbidden(self):
        self.client.login(username="stranger", password="pass1234")
        url = reverse("event-detail", args=[self.private_event.id])
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    # -----------------------------
    # UPDATE / DELETE: IsOrganizerOrReadOnly
    # -----------------------------
    def test_update_event_owner_allowed(self):
        self.client.login(username="owner", password="pass1234")
        url = reverse("event-detail", args=[self.public_event.id])
        data = {"title": "Updated Title"}
        response = self.client.patch(url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.public_event.refresh_from_db()
        self.assertEqual(self.public_event.title, "Updated Title")

    def test_update_event_non_owner_forbidden(self):
        self.client.login(username="stranger", password="pass1234")
        url = reverse("event-detail", args=[self.public_event.id])
        data = {"title": "Hacked Title"}
        response = self.client.patch(url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    # -----------------------------
    # CREATE: must be authenticated
    # -----------------------------
    def test_create_event_anonymous_forbidden(self):
        url = reverse("event-list")
        data = {
            "title": "New Event",
            "description": "desc",
            "location": "loc",
            "start_time": "2025-01-03T10:00:00Z",
            "end_time": "2025-01-03T12:00:00Z",
            "is_public": True,
        }
        response = self.client.post(url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_create_event_authenticated_allowed(self):
        self.client.login(username="owner", password="pass1234")
        url = reverse("event-list")
        data = {
            "title": "New Event",
            "description": "desc",
            "location": "loc",
            "start_time": "2025-01-03T10:00:00Z",
            "end_time": "2025-01-03T12:00:00Z",
            "is_public": True,
        }
        response = self.client.post(url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data["owner"]["username"], "owner")


class RSVPAndReviewTests(APITestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username="user", email="user@example.com", password="pass1234"
        )
        self.event = Event.objects.create(
            owner=self.user,
            title="Reviewable Event",
            description="desc",
            location="loc",
            start_time="2025-01-01T10:00:00Z",
            end_time="2025-01-01T12:00:00Z",
            is_public=True,
        )

    # -----------------------------
    # RSVP action on EventViewSet
    # -----------------------------
    def test_rsvp_requires_authentication(self):
        url = reverse("event-rsvp", args=[self.event.id])  # action name 'rsvp'
        response = self.client.post(url, {"status": "attending"}, format="json")
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_rsvp_authenticated_success(self):
        self.client.login(username="user", password="pass1234")
        url = reverse("event-rsvp", args=[self.event.id])
        response = self.client.post(url, {"status": "attending"}, format="json")
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data["user"]["username"], "user")

    # -----------------------------
    # Review creation
    # -----------------------------
    def test_create_review_invalid_event_returns_404(self):
        self.client.login(username="user", password="pass1234")
        url = reverse("review-list")  # router name 'review'
        response = self.client.post(
            url,
            {"event_id": 9999, "rating": 5, "comment": "Nice"},
            format="json",
        )
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_create_review_valid_event(self):
        self.client.login(username="user", password="pass1234")
        from events.models import RSVP
        RSVP.objects.create(user=self.user, event=self.event, status="attending")

        url = reverse("review-list")
        response = self.client.post(
            url,
            {"event_id": self.event.id, "rating": 4, "comment": "Good"},
            format="json",
        )
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Review.objects.count(), 1)
        review = Review.objects.first()
        self.assertEqual(review.user, self.user)
        self.assertEqual(review.event, self.event)
