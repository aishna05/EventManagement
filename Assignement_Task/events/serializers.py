from rest_framework import serializers
from django.contrib.auth import get_user_model
from .models import Event, RSVP, Review, UserProfile

User = get_user_model()


# -----------------------------
# USER PROFILE SERIALIZER
# -----------------------------
class UserProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserProfile
        fields = ["full_name", "bio", "location", "profile_picture"]


# -----------------------------
# USER SERIALIZER
# -----------------------------
class UserSerializer(serializers.ModelSerializer):
    profile = UserProfileSerializer(read_only=True)

    class Meta:
        model = User
        fields = ["id", "username", "email", "profile"]


# -----------------------------
# EVENT SERIALIZER
# -----------------------------
class EventSerializer(serializers.ModelSerializer):
    owner = UserSerializer(read_only=True)
    rsvp_count = serializers.IntegerField(source="rsvps.count", read_only=True)
    average_rating = serializers.SerializerMethodField()

    class Meta:
        model = Event
        fields = [
            "id", "owner", "title", "description", "location",
            "start_time", "end_time", "is_public",
            "created_at", "updated_at",
            "rsvp_count", "average_rating"
        ]

    def get_average_rating(self, obj):
        ratings = obj.reviews.all().values_list("rating", flat=True)
        return round(sum(ratings) / len(ratings), 2) if ratings else None

    # def create(self, validated_data):
    #     user = self.context["request"].user
    #     return Event.objects.create(owner=user, **validated_data)


# -----------------------------
# RSVP SERIALIZER
# -----------------------------
class RSVPSerializer(serializers.ModelSerializer):
    user = UserSerializer(read_only=True)

    class Meta:
        model = RSVP
        fields = ["id", "user", "event", "status", "created_at"]
        read_only_fields = ["event"]

    def create(self, validated_data):
        user = self.context["request"].user
        event = self.context["event"]
        rsvp, created = RSVP.objects.update_or_create(
            user=user,
            event=event,
            defaults=validated_data,  # e.g. {"status": "attending"}
        )
        return rsvp

# -----------------------------
# REVIEW SERIALIZER
# -----------------------------
class ReviewSerializer(serializers.ModelSerializer):
    user = UserSerializer(read_only=True)

    class Meta:
        model = Review
        fields = ["id", "user", "event", "rating", "comment", "created_at"]
        read_only_fields = ["event"]

    def create(self, validated_data):
        user = self.context["request"].user
        event = self.context["event"]
        return Review.objects.create(user=user, event=event, **validated_data)
from rest_framework import serializers
from django.contrib.auth import get_user_model

User = get_user_model()


class RegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, min_length=8)

    class Meta:
        model = User
        fields = ["id", "username", "email", "password"]

    def create(self, validated_data):
        # Use create_user so password is hashed
        password = validated_data.pop("password")
        user = User.objects.create_user(password=password, **validated_data)
        return user
