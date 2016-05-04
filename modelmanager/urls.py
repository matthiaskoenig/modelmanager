from django.conf.urls import include, url
from django.contrib import admin

from django.conf import settings
from django.conf.urls.static import static
from django.views.generic.base import RedirectView
admin.autodiscover()

urlpatterns = [
    url(r'^admin/', include(admin.site.urls)),
    url(r'^simapp/', include('simapp.urls', namespace="simapp", app_name='simapp')),
    
    # handle static files
    url(r'^$', RedirectView.as_view(url=r'simapp', permanent=False)),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

