"""
Parts of this file are based on django-schedule
https://github.com/thauber/django-schedule/
Licensed under NewBSD

"""
import json
from itertools import islice
import urllib

from dateutil import rrule, relativedelta

from django.db import models
from django.conf import settings
from django.contrib.auth.models import User
from django.utils.translation import ugettext_lazy as _
from django.utils import timezone, formats
from django.core.mail import send_mail
from django.template.loader import render_to_string
import django.dispatch


RAW_FREQUENCIES = (
    ("YEARLY", (_("Yearly"), _('Years'), rrule.YEARLY, 'years')),
    ("MONTHLY", (_("Monthly"), _('Months'), rrule.MONTHLY, 'months')),
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
    rolling = True

    def __unicode__(self):
        return u'%s (%s %s)' % (self.subject, self.interval, self.frequency)

    @property
    def readable_frequency(self):
        return READABLE_FREQUENCIES_DICT[self.frequency]

    @property
    def subject_dummy(self):
        return self.format_string(self.subject)

    @property
    def body_dummy(self):
        return self.format_string(self.body)

    def format_string(self, template):
        return template.format(
            last_date=_('<last request date>'),
            date=_('<date of reminder>')
        )

    def next_date(self):
        try:
            return ReminderRequest.objects.filter(rule=self,
                start__gte=timezone.now()).order_by('start')[0]
        except IndexError:
            return None

    def get_rrule_object(self):
        if self.frequency:
            params = {}
            if self.interval:
                params['interval'] = self.interval
            return rrule.rrule(RRULE_FREQUENCY[self.frequency], dtstart=self.start, **params)

    def get_before(self, date):
        if self.frequency:
            key = dict(RAW_FREQUENCIES)[self.frequency][3]
            return self.start + relativedelta.relativedelta(**{key: -self.interval})
        return date

    def get_occurrence_dates(self, start, end=None):
        """
        returns a list of occurrences for this event from start to end.
        """
        if self.frequency:
            rule = self.get_rrule_object()
            if end is not None:
                o_starts = rule.between(start, end, inc=False)
                for o_start in o_starts:
                    yield o_start
            else:
                while True:
                    start = rule.after(start, inc=False)
                    yield start
        else:
            yield self.start

    def generate_request_reminders(self, start=None, count=1):
        if start is None:
            start = self.start
        for date in islice(self.get_occurrence_dates(start), 0, count):
            yield ReminderRequest(rule=self, start=date)

    def create_initial_reminder(self):
        return ReminderRequest.objects.create(rule=self, start=timezone.now())

    def get_email_form(self, post_data=None):
        from .forms import EmailSubscriptionForm
        if post_data:
            return EmailSubscriptionForm(self, post_data, prefix="email-%s" % self.pk)
        else:
            return EmailSubscriptionForm(self, prefix="email-%s" % self.pk)


class ReminderRequest(models.Model):
    rule = models.ForeignKey(ReminderRule)
    start = models.DateTimeField()
    request_url = models.CharField(max_length=255, blank=True)
    requested = models.BooleanField(default=False)
    request_date = models.DateTimeField(null=True, blank=True)
    previous = models.ForeignKey('self', null=True, blank=True,
        on_delete=models.SET_NULL)
    user = models.ForeignKey(User, null=True, blank=True)

    request_made = django.dispatch.Signal()

    def __unicode__(self):
        return u"%s (%s)" % (self.rule.subject, self.start)

    @property
    def subject(self):
        return self.format_string(self.rule.subject)

    @property
    def body(self):
        return self.format_string(self.rule.body)

    def format_string(self, template):
        return template.format(
            last_date=formats.date_format(
                self.get_last_date(), _("SHORT_DATE_FORMAT")
            ),
            date=formats.date_format(
                timezone.now(), _("SHORT_DATE_FORMAT")
            )
        )

    def get_last_date(self):
        if self.previous:
            return self.previous.request_date
        else:
            return self.rule.get_before(self.start)

    def get_date(self):
        return self.start

    def get_made_request_form(self):
        from .forms import MadeRequestForm
        return MadeRequestForm(self, prefix="made-%s" % self.pk)

    def create_next_reminder(self):
        start_date = self.start
        if self.rule.rolling and self.request_date:
            start_date = self.request_date
        gen = self.rule.generate_request_reminders(start=start_date)
        reminder = list(gen)[0]
        reminder.previous = self
        reminder.save()
        return reminder

    def get_make_request_url(self):
        subject = urllib.quote(self.subject.encode('utf-8'))
        body = urllib.quote(self.body.encode('utf-8'))
        return self.rule.foisite.pattern.format(
            url=self.rule.url,
            subject=subject,
            body=body
        )


class EmailReminder(models.Model):
    rule = models.ForeignKey(ReminderRule)
    email = models.EmailField()
    timestamp = models.DateTimeField()
    language = models.CharField(max_length=10, default='en')

    class Meta:
        unique_together = (("rule", "email"),)

    def __unicode__(self):
        return u"%s on %s" % (self.email, self.rule)

    def send_notification(self):
        from django.utils import translation
        translation.activate(self.language)
        # TODO: finish mail template
        send_mail(_("FOI Reminder: a request needs to be made"),
            _('Please follow this link'),
            settings.DEFAULT_FROM_EMAIL,
            [self.email]
        )
