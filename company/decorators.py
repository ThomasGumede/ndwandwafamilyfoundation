from django.contrib import messages
from django.shortcuts import redirect, render, get_object_or_404

def user_not_superuser_or_staff(function=None, redirect_url='/'):
    """
    Decorator for views that checks that the user is NOT logged in, redirecting
    to the homepage if necessary by default.
    """
    def decorator(view_func):
        def _wrapped_view(request, *args, **kwargs):
            if not request.user.is_staff and not request.user.is_superuser:
                messages.warning(request, "You are not part of our staff members")
                return redirect(redirect_url)
                
            return view_func(request, *args, **kwargs)

        return _wrapped_view

    if function:
        return decorator(function)

    return decorator