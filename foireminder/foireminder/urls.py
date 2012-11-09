from django.conf.urls import patterns, include, url
from django.conf import settings
from django.contrib.staticfiles.urls import staticfiles_urlpatterns

# Uncomment the next two lines to enable the admin:
from django.contrib import admin
admin.autodiscover()

urlpatterns = patterns('',
    url(r'^$', 'reminders.views.index', name='index'),
    url(r'^new$', 'reminders.views.new', name='new'),
    url(r'^request-made/(?P<pk>\d+)$', 'reminders.views.request_made', name='request_made'),

    url(r'^admin/', include(admin.site.urls)),
)

if settings.DEBUG:
    urlpatterns += staticfiles_urlpatterns()
