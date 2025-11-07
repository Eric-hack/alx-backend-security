from django.test import TestCase, RequestFactory
from .middleware import IPLoggingMiddleware
from .models import RequestLog

class IPLoggingMiddlewareTest(TestCase):
    def test_logs_request(self):
        factory = RequestFactory()
        request = factory.get('/some-path')
        request.META['REMOTE_ADDR'] = '127.0.0.1'

        middleware = IPLoggingMiddleware(get_response=lambda req: None)
        middleware(request)

        self.assertTrue(RequestLog.objects.filter(path='/some-path', ip_address='127.0.0.1').exists())
