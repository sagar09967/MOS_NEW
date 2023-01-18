from django.contrib import admin
from django.urls import path, include
from django.conf.urls.static import static
from django.conf import settings

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/', include('api.purchaseurls')),
    path('', include('api.urls')),
    path('', include('api.salesurls')),
    path('api-auth/', include('rest_framework.urls')),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT) + static('post_images/',document_root=settings.POST_IMAGES_ROOT)
