from django.urls import path
from ip_tracking import views

urlpatterns = [
    path('anon-protected/', views.anonymous_sensitive_view, name='anon_protected'),
    path('auth-protected/', views.authenticated_sensitive_view, name='auth_protected'),
]
