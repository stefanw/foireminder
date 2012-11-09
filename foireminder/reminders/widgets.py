import floppyforms as forms

from .models import FoiSite


class FoiSiteURLWidget(forms.URLInput):
    template_name = 'reminders/_foisiteurlwidget.html'

    def get_context(self, name, value, attrs=None):
        ctx = super(FoiSiteURLWidget, self).get_context(name, value, attrs)
        ctx['foisites'] = FoiSite.objects.all()
        return ctx
