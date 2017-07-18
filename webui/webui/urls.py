from django.conf.urls import include, url
from django.contrib import admin
from django.core.urlresolvers import reverse_lazy
from django.views.generic import RedirectView

urlpatterns = [
    url(r'^$', RedirectView.as_view(
        url=reverse_lazy('list_index'),
        permanent=True)),
    url(r'^postorius/', include('postorius.urls')),
    url(r'^hyperkitty/', include('hyperkitty.urls')),
    url(r'', include('django_mailman3.urls')),
    url(r'^accounts/', include('allauth.urls')),
    # Django admin
    url(r'^admin/', include(admin.site.urls)),
]
