from django.contrib import admin

from .models import FoiSite, ReminderRule, ReminderRequest

admin.site.register(FoiSite)
admin.site.register(ReminderRule)
admin.site.register(ReminderRequest)
