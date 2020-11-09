from gallery_showroom import settings
from . import views
from django.contrib import admin
from django.urls import path
from django.contrib.staticfiles.urls import staticfiles_urlpatterns, static


urlpatterns = [
    path('overview/', views.api_overview, name='overview'),
    path('gallery/', views.galleries, name='galleries'),
    path('gallery/<str:gallery>/', views.gallery_detail, name='gallery_detail'),
    path('gallery/<str:gallery>/<str:image>', views.delete_image_from_galery, name='gallery_delete_image'),
    path('images/<int:w>x<int:h>/<str:image>', views.generate_image_view, name='gallery_delete_image'),
]

if settings.DEBUG:
    urlpatterns += staticfiles_urlpatterns()
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

