from django.http import JsonResponse
from django.contrib.auth.decorators import login_required
from ratelimit.decorators import ratelimit
from django.conf import settings

# Example sensitive view (e.g., login, or API)
@ratelimit(key='ip', rate=settings.RATE_LIMIT_ANON, block=True)
def anonymous_sensitive_view(request):
    return JsonResponse({"message": "Anonymous access allowed"})


@login_required
@ratelimit(key='ip', rate=settings.RATE_LIMIT_AUTH, block=True)
def authenticated_sensitive_view(request):
    return JsonResponse({"message": "Authenticated access allowed"})
