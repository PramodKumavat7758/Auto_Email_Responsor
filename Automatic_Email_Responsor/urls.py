
from django.contrib import admin
from django.urls import path, include
from django.views.generic import RedirectView

urlpatterns = [
    path('admin/', admin.site.urls),  # Admin route
    path('email-handler/', include("app.urls")),  # Include app-specific routes
    path('', RedirectView.as_view(url="/email-handler/google-auth")),  # Redirect root to email handler
]