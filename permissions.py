from rest_framework.permissions import BasePermission, SAFE_METHODS


class IsOwnerOrReadOnly(BasePermission):

    def has_object_permission(self, request, view, obj):
        if request.method in SAFE_METHODS:
            return True
        return obj.owner == request.user


class IsOwnerOrFollower(BasePermission):
    """
    Custom permission to only allow owners
    of an object or their followers to view it.
    """

    def has_object_permission(self, request, view, obj):
        if request.method in SAFE_METHODS:
            return (
                obj.owner == request.user
                or request.user.id in obj.followers.values_list(
                    "owner", flat=True
                )
                or request.user.id in obj.following.values_list(
                    "owner", flat=True
                )
            )
        return obj.owner == request.user
