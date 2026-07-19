from rest_framework.permissions import BasePermission


class   Hr(BasePermission):
    def has_permission(self, request, view):
        return request.user.is_authenticated and request.user.role =='admin'
class ISDoctor(BasePermission):
    def has_permission(self, request, view):
        return request.user.is_authenticated and request.user.role =='doctor'
class AdminOrDoctor(BasePermission):
    def has_permission(self, request, view):
        return request.user.is_authenticated and request.user.role =='admin' or request.user.role =='doctor'
class IsUser(BasePermission):
    def has_permission(self, request, view):
        return request.user.is_authenticated and request.user.role =='user'

