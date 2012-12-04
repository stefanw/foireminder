from django.dispatch import receiver

from .models import ReminderRequest


@receiver(ReminderRequest.request_made,
        dispatch_uid="request_made_create_next_reminder")
def request_made_create_next_reminder(sender, **kwargs):
    sender.create_next_reminder()
