from .models import RequestLog

class IPLoggingMiddleware:
    """
    Middleware to log client IP address and request path for every incoming request.
    """

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        # Resolve client IP (prefer X-Forwarded-For if present)
        xff = request.META.get("HTTP_X_FORWARDED_FOR")
        if xff:
            # X-Forwarded-For may contain a comma-separated list; client is the first
            ip_address = xff.split(",")[0].strip()
        else:
            ip_address = request.META.get("REMOTE_ADDR")

        # Create the RequestLog entry (timestamp auto-populated)
        try:
            RequestLog.objects.create(
                ip_address=ip_address or "0.0.0.0",
                path=request.path,
            )
        except Exception:
            # Fail-safe: do not break request processing if logging fails.
            # In production you might log this exception to Sentry or Django logging.
            pass

        return self.get_response(request)
