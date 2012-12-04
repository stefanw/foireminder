from django.utils import timezone

from .models import ReminderRequest, EmailReminder


def send_todays_notifications(self):
    today = timezone.now()
    reminders = ReminderRequest.objects.filter(
        start__year=today.year,
        start__month=today.month,
        start__day=today.da
    )
    for reminder in reminders:
        for subscriber in EmailReminder.objects.filter(rule=reminder.rule):
            subscriber.send_notification()
