from rest_framework.permissions import BasePermission, SAFE_METHODS

class IsOrganizerOrReadOnly(BasePermission):
    """Only the event owner can edit/update/delete."""

    def has_object_permission(self, request, view, obj):
        if request.method in SAFE_METHODS:
            return True
        return obj.owner == request.user
class IsInvitedOrPublic(BasePermission):
    """Allow access only if event is public or user is invited."""

    def has_object_permission(self, request, view, obj):
        # If event is public, allow access
        if obj.is_public:
            return True

        # If not authenticated, deny private event
        if not request.user or not request.user.is_authenticated:
            return False

        # Check if user has RSVP (attending, maybe, etc.)
        return obj.rsvps.filter(user=request.user).exists()