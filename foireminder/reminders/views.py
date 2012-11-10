from datetime import timedelta

from django.shortcuts import render, get_object_or_404, redirect
from django.utils.translation import ugettext_lazy as _
from django.utils import timezone
from django.contrib import messages

from .models import ReminderRule, ReminderRequest
from .forms import NewReminderForm, MadeRequestForm


def index(request, new_reminder_form=None):
    start = timezone.now()
    after = start - timedelta(days=7)
    due_requests = (ReminderRequest.objects
        .filter(start__gte=after, start__lte=start)
        .exclude(requested=True)
        .select_related('rule', 'rule__foisite')
    )
    reminders = ReminderRule.objects.all()
    if new_reminder_form is None:
        new_reminder_form = NewReminderForm()
    return render(request, 'index.html', {
        'form': new_reminder_form,
        'requests': due_requests,
        'reminders': reminders
    })


def new(request):
    form = NewReminderForm(request.POST)
    if not form.is_valid():
        messages.add_message(request, messages.ERROR, '')
        return index(request, new_reminder_form=form)
    start = timezone.now().replace(hour=0, minute=0, second=0, microsecond=0)
    rule = ReminderRule(
        foisite=form.foisite,
        subject=form.cleaned_data['subject'],
        body=form.cleaned_data['body'],
        user=request.user if request.user.is_authenticated() else None,
        created=timezone.now(),
        start=start,
        frequency=form.cleaned_data['frequency'],
        interval=int(form.cleaned_data['interval']),
        url=form.cleaned_data['url'],
    )
    rule.save()
    for reminder in rule.generate_request_reminders():
        reminder.save()
    return redirect('index')


def request_made(request, pk):
    reminder = get_object_or_404(ReminderRequest, pk=int(pk))
    form = MadeRequestForm(reminder, request.POST, prefix="made-%s" % reminder.pk)
    if form.is_valid():
        form.save()
        messages.add_message(request, messages.SUCCESS, _('Thanks for making this request!'))
    else:
        messages.add_message(request, messages.ERROR, form.errors.values()[0][0])
    return redirect('index')
