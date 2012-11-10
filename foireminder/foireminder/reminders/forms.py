import floppyforms as forms
import requests
import re

from django.utils.translation import ugettext_lazy as _

from .models import FoiSite, READABLE_FREQUENCIES
from .widgets import FoiSiteURLWidget


def get_foisite_choices():
    # TODO: Call on request, not server start
    foisites = FoiSite.objects.all()
    return [('', '---')] + [(fs.pk, '%s (%s)' % (fs.name,
        fs.country)) for fs in foisites]


class NewReminderForm(forms.Form):
    interval = forms.IntegerField(widget=forms.NumberInput(
        attrs={
            'class': "input-mini"
        }
    ), initial=6)
    frequency = forms.ChoiceField(choices=READABLE_FREQUENCIES,
        widget=forms.Select(attrs={
            'class': 'input-small'
        }),
        initial='MONTHLY')
    subject = forms.CharField(label=_('Subject'))
    body = forms.CharField(widget=forms.Textarea)
    foisite = forms.ChoiceField(label=_('Select site and public body'),
        choices=get_foisite_choices())
    url = forms.CharField(widget=FoiSiteURLWidget(attrs={'class': 'span6'}))

    def clean(self):
        if 'url' in self.cleaned_data:
            url = self.cleaned_data['url']
            try:
                self.foisite = FoiSite.objects.get(pk=self.cleaned_data['foisite'])
            except FoiSite.DoesNotExist:
                raise forms.ValidationError(
                    _('The given FOI site does not exist in our database.'))
            if not re.match(self.foisite.url_pattern_make_request, url):
                raise forms.ValidationError(
                    _('The given URL does not seem to be a requesting page.'))
        return self.cleaned_data


class MadeRequestForm(forms.Form):
    url = forms.URLField(label=_('Please give the URL of this request.'),
        widget=forms.URLInput(
            attrs={'placeholder': 'http://'},
        ))

    def __init__(self, reminder, *args, **kwargs):
        self.reminder = reminder
        super(MadeRequestForm, self).__init__(*args, **kwargs)

    def clean_url(self):
        url = self.cleaned_data['url']
        if not re.match(self.reminder.rule.foisite.url_pattern, url):
            raise forms.ValidationError(
                _('The given site does not seem to be a valid request page for the FOI site.'))
        response = requests.get(url)
        if not self.reminder.subject in response.text:
            raise forms.ValidationError(
                _('The given site does not seem to contain the request text.'))
        return url

    def save(self):
        self.reminder.request_url = self.cleaned_data['url']
        self.reminder.requested = True
        self.reminder.save()
