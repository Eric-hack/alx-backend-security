from django.http import HttpResponseForbidden
from .models import RequestLog, BlockedIP

class IPLoggingMiddleware:
    """
    Middleware that logs IPs and blocks blacklisted ones.
    """

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        # Extract IP (supporting proxies)
        xff = request.META.get("HTTP_X_FORWARDED_FOR")
        if xff:
            ip_address = xff.split(",")[0].strip()
        else:
            ip_address = request.META.get("REMOTE_ADDR")

        # Check blacklist first
        if BlockedIP.objects.filter(ip_address=ip_address).exists():
            return HttpResponseForbidden("Access denied: your IP is blocked.")

        # Log the request if not blocked
        try:
            RequestLog.objects.create(
                ip_address=ip_address or "0.0.0.0",
                path=request.path,
            )
        except Exception:
            pass  # never block request if logging fails

        return self.get_response(request)
