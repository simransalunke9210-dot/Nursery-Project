from rest_framework.permissions import BasePermission
from django.contrib.auth.models import User
from .models import Admin


class IsAdminUser(BasePermission):

    message = "Only admin users are allowed to access this API."

    def has_permission(self, request, view):

        # User must have a valid JWT
        if not request.user or not request.user.is_authenticated:
            return False

        # Check whether logged-in Django User has an Admin account
        return Admin.objects.filter(
            email=request.user.email
        ).exists()