from django.http import HttpResponseForbidden
from .models import RequestLog, BlockedIP
from django.utils.deprecation import MiddlewareMixin
from django_ip_geolocation.middleware import IpGeolocationMiddleware
from django.core.cache import cache

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

        
class IPGeolocationLoggingMiddleware(MiddlewareMixin):
    def process_request(self, request):
        ip_address = self.get_client_ip(request)
        if not ip_address:
            return

        # Check if cached
        cached_data = cache.get(ip_address)
        if cached_data:
            country, city = cached_data
        else:
            # Get geolocation info
            IpGeolocationMiddleware().process_request(request)
            country = getattr(request, "geo_country_name", "")
            city = getattr(request, "geo_city", "")
            # Cache for 24 hours
            cache.set(ip_address, (country, city), 60 * 60 * 24)

        # Log the request
        RequestLog.objects.create(
            ip_address=ip_address,
            country=country,
            city=city,
            path=request.path
        )

    def get_client_ip(self, request):
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            return x_forwarded_for.split(',')[0]
        return request.META.get('REMOTE_ADDR')