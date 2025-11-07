from celery import shared_task
from django.utils import timezone
from datetime import timedelta
from ip_tracking.models import RequestLog, SuspiciousIP

@shared_task
def detect_anomalies():
    one_hour_ago = timezone.now() - timedelta(hours=1)
    logs = RequestLog.objects.filter(timestamp__gte=one_hour_ago)

    # Count requests per IP
    ip_counts = {}
    for log in logs:
        ip_counts[log.ip_address] = ip_counts.get(log.ip_address, 0) + 1

        # Check for sensitive paths
        if any(path in log.path for path in ['/admin', '/login']):
            SuspiciousIP.objects.get_or_create(
                ip_address=log.ip_address,
                defaults={'reason': f"Accessed sensitive path: {log.path}"}
            )

    # Check for excessive requests
    for ip, count in ip_counts.items():
        if count > 100:
            SuspiciousIP.objects.get_or_create(
                ip_address=ip,
                defaults={'reason': f"Excessive requests ({count}) in the last hour"}
            )

    print("Anomaly detection task completed.")
