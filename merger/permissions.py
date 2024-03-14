from rest_framework import permissions


class IsOwner(permissions.BasePermission):
    """
    Object-level permission to only allow owners of an object to access it.
    """

    def has_object_permission(self, request, view, obj):
        return obj.user == request.user


class IsParentOwner(permissions.BasePermission):
    """
    Object-level permission to only allow owner of the parent object to access the object.
    """

    def has_object_permission(self, request, view, obj):
        return obj.order.user == request.user
