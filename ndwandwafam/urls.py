from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('admin/', admin.site.urls),
    path("", include("home.urls", namespace="home")),
    path("accounts/", include("accounts.urls", namespace="accounts")),
    path("campaigns/", include("campaigns.urls", namespace="campaigns")),
    path("events/", include("events.urls", namespace="events")),
    path("payments/", include("payments.urls", namespace="payments")),
    path("company/", include("company.urls", namespace="company")),
    path("listings/", include("business.urls", namespace="business")),
    path('tinymce/', include('tinymce.urls')),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
