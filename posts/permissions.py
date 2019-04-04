from rest_framework import permissions


class IsAuthorOrReadOnly(permissions.BasePermission):

  def has_object_permission(self, request, view, obj):
    # Read-only permissions are allowed for any request
    if request.method in permissions.SAFE_METHODS:
      return True
    return obj.author == request.user


class IsUserOrReadOnly(permissions.BasePermission):
	def has_object_permission(self, request, view, obj):
		if request.method in permissions.SAFE_METHODS:
			return True
		#print(obj)
		return obj == request.user