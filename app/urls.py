

from django.urls import path
from app import views

urlpatterns = [
    path('google-auth/', views.google_auth, name="google_auth"),
    path('google-auth/callback/', views.google_auth_callback, name="google_auth_callback"),
    path('read-emails/', views.read_emails, name="read_emails"),
    path('view-mails/',views.fetch_google_emails,name="view-mails")
]
