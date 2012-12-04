from django.conf.urls import patterns, url

urlpatterns = patterns('',
    url(r'^new$', 'foireminder.reminders.views.new', name='new'),
    url(r'^request-made/(?P<pk>\d+)$', 'foireminder.reminders.views.request_made',
        name='request_made'),
   url(r'^subscribe/(?P<pk>\d+)$', 'foireminder.reminders.views.subscribe_email',
        name='subscribe_email'),
)