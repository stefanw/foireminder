from django.contrib import admin

from .models import (FoiSite, ReminderRule, ReminderRequest,
    EmailReminder)

admin.site.register(FoiSite)
admin.site.register(ReminderRule)
admin.site.register(ReminderRequest)
admin.site.register(EmailReminder)
