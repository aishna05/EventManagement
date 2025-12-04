from django.db import models
from django.conf import settings
from django.core.validators import MinValueValidator, MaxValueValidator

User = settings.AUTH_USER_MODEL


# ---------------------------------------------------------
# 1. USER PROFILE MODEL
# ---------------------------------------------------------
class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name="profile")
    full_name = models.CharField(max_length=255)
    bio = models.TextField(blank=True)
    location = models.CharField(max_length=255, blank=True)
    profile_picture = models.ImageField(upload_to="profiles/", blank=True, null=True)

    def __str__(self):
        return self.full_name


# ---------------------------------------------------------
# 2. EVENT MODEL
# ---------------------------------------------------------
class Event(models.Model):
    owner = models.ForeignKey(User, related_name='events', on_delete=models.CASCADE)
    title = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    location = models.CharField(max_length=255, blank=True)
    start_time = models.DateTimeField()
    end_time = models.DateTimeField()
    is_public = models.BooleanField(default=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-start_time']

    def __str__(self):
        return f"{self.title} ({self.start_time})"


# ---------------------------------------------------------
# 3. RSVP MODEL
# ---------------------------------------------------------
class RSVP(models.Model):
    ATTENDING = 'attending'
    MAYBE = 'maybe'
    NOT_GOING = 'not_going'

    STATUS_CHOICES = [
        (ATTENDING, 'Going'),
        (MAYBE, 'Maybe'),
        (NOT_GOING, 'Not Going'),
    ]

    user = models.ForeignKey(User, related_name='rsvps', on_delete=models.CASCADE)
    event = models.ForeignKey(Event, related_name='rsvps', on_delete=models.CASCADE)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default=MAYBE)

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('user', 'event')
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.user} -> {self.event} : {self.status}"


# ---------------------------------------------------------
# 4. REVIEW MODEL
# ---------------------------------------------------------
class Review(models.Model):
    user = models.ForeignKey(User, related_name='reviews', on_delete=models.CASCADE)
    event = models.ForeignKey(Event, related_name='reviews', on_delete=models.CASCADE)
    rating = models.PositiveSmallIntegerField(
        validators=[MinValueValidator(1), MaxValueValidator(5)]
    )
    comment = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('user', 'event')  # User can review event only once
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.user} rated {self.event} => {self.rating}"
