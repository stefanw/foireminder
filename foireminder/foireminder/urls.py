from django.conf.urls import patterns, include, url
from django.contrib.staticfiles.urls import staticfiles_urlpatterns

# Uncomment the next two lines to enable the admin:
from django.contrib import admin
admin.autodiscover()

urlpatterns = patterns('',
    url(r'^$', 'foireminder.reminders.views.index', name='index'),
    url(r'^new$', 'foireminder.reminders.views.new', name='new'),
    url(r'^request-made/(?P<pk>\d+)$', 'foireminder.reminders.views.request_made',
        name='request_made'),
    (r'^language/', include('django.conf.urls.i18n')),
    url(r'^admin/', include(admin.site.urls)),
)


urlpatterns += staticfiles_urlpatterns()
