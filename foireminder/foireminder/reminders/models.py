"""
Parts of this file are based on django-schedule
https://github.com/thauber/django-schedule/
Licensed under NewBSD

"""
import json
from dateutil import rrule
from itertools import islice
import urllib

from django.db import models
from django.contrib.auth.models import User
from django.utils.translation import ugettext_lazy as _
from django.utils import timezone


RAW_FREQUENCIES = (
    ("YEARLY", (_("Yearly"), _('Years'), rrule.YEARLY)),
    ("MONTHLY", (_("Monthly"), _('Months'), rrule.MONTHLY)),
)
FREQUENCIES = [(f[0], f[1][0]) for f in RAW_FREQUENCIES]
READABLE_FREQUENCIES = [(f[0], f[1][1]) for f in RAW_FREQUENCIES]
READABLE_FREQUENCIES_DICT = dict(READABLE_FREQUENCIES)
RRULE_FREQUENCY = dict([(f[0], f[1][2]) for f in RAW_FREQUENCIES])


class FoiSite(models.Model):
    name = models.CharField(max_length=255)
    country = models.CharField(max_length=255, blank=True, default='')
    language = models.CharField(max_length=10, default='en')
    timezone = models.CharField(max_length=10, default='UTC')
    slug = models.SlugField()
    url = models.URLField()
    url_pattern = models.CharField(max_length=255, default='.*',
        help_text=_('Regular Expression to match request pages of this FOI site'))
    url_pattern_make_request = models.CharField(max_length=255, default='.*',
        help_text=_('Regular Expression to match requesting page of this FOI site'))
    pattern = models.CharField(max_length=255,
        help_text=_('String format pattern including {url}, {subject} and {body}'))
    list_url = models.CharField(max_length=255, blank=True, default='')
    tutorial = models.TextField(default='', blank=True)
    example_url = models.CharField(max_length=255, blank=True, default='')
    secret = models.CharField(max_length=255, blank=True)

    def __unicode__(self):
        return self.name

    def as_json(self):
        return json.dumps({
            'name': self.name,
            'url': self.url,
            'list_url': self.list_url,
            'tutorial': self.tutorial,
            'example_url': self.example_url
        })


class ReminderRule(models.Model):
    foisite = models.ForeignKey(FoiSite)
    subject = models.CharField(max_length=255)
    body = models.TextField()
    created = models.DateTimeField()
    user = models.ForeignKey(User, null=True)
    start = models.DateTimeField()
    frequency = models.CharField(choices=FREQUENCIES, max_length=10, blank=True)
    interval = models.IntegerField(null=True, default=6)
    url = models.URLField(blank=True, default='')

    def __unicode__(self):
        return u'%s (%s %s)' % (self.subject, self.interval, self.frequency)

    @property
    def readable_frequency(self):
        return READABLE_FREQUENCIES_DICT[self.frequency]

    def next_date(self):
        return ReminderRequest.objects.filter(rule=self,
            start__gte=timezone.now())[0]

    def get_rrule_object(self):
        if self.frequency:
            params = {}
            if self.interval:
                params['interval'] = self.interval
            return rrule.rrule(RRULE_FREQUENCY[self.frequency], dtstart=self.start, **params)

    def get_occurrence_dates(self, start, end=None):
        """
        returns a list of occurrences for this event from start to end.
        """
        if self.frequency:
            rule = self.get_rrule_object()
            if end is not None:
                o_starts = rule.between(start, end, inc=True)
                for o_start in o_starts:
                    yield o_start
            else:
                first = True
                while True:
                    next = rule.after(start, inc=first)
                    yield next
                    if first:
                        first = False
                        start = next
        else:
            yield self.start

    def generate_request_reminders(self, start=None, count=5):
        if start is None:
            start = self.start
        for date in islice(self.get_occurrence_dates(start), 0, count):
            yield ReminderRequest(rule=self, start=date)


class ReminderRequest(models.Model):
    rule = models.ForeignKey(ReminderRule)
    start = models.DateTimeField()
    request_url = models.CharField(max_length=255, blank=True)
    requested = models.BooleanField(default=False)
    user = models.ForeignKey(User, null=True)

    def __unicode__(self):
        return u"%s (%s)" % (self.rule.subject, self.start)

    @property
    def subject(self):
        return self.rule.subject

    @property
    def body(self):
        return self.rule.body.format()

    def get_made_request_form(self):
        from .forms import MadeRequestForm
        return MadeRequestForm(self, prefix="made-%s" % self.pk)

    def get_request_url(self):
        subject = urllib.quote(self.subject.encode('utf-8'))
        body = urllib.quote(self.body.encode('utf-8'))
        return self.rule.foisite.pattern.format(
            url=self.rule.url,
            subject=subject,
            body=body
        )
