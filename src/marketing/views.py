from django.conf import settings
from django.contrib.messages.views import SuccessMessageMixin
from django.http import HttpResponse
from django.views.generic import UpdateView, View
from django.shortcuts import render, redirect

from .forms import MarketingPreferenceForm
from .mixins import CsrfExemptMixin
from .models import MarketingPreference
from .utils import Mailchimp
# Create your views here.
MAILCHIMP_EMAIL_LIST_ID     = getattr(settings, "MAILCHIMP_EMAIL_LIST_ID", None)

class MarketingPreferenceUpdateView(SuccessMessageMixin, UpdateView):
    form_class = MarketingPreferenceForm
    template_name = 'base/forms.html'
    success_url = '/settings/email/'
    success_message = "Your Email preferences has ben updated. Thank you."

    def dispatch(self, *args, **kwargs):
        user = self.request.user
        if not user.is_authenticated:
            return redirect("/login/?next=/settings/email/")  #HttpResponse("Not Allowed", status=400)
        return super(MarketingPreferenceUpdateView, self).dispatch( *args, **kwargs)

    def get_context_data(self, *args, **kwargs) :
        context = super(MarketingPreferenceUpdateView, self).get_context_data(*args, **kwargs)
        context['title'] = "Update Email Preferences"
        return context

    def get_object(self):
        user = self.request.user
        obj, created = MarketingPreference.objects.get_or_create(user=user) # get_absolute_url
        return obj
    

"""

method:POST
data[action]:unsub
data[email]:ct30111998@gmail.com
data[email_type]:html
data[id]:0528b16faf
data[ip_opt]:103.85.8.167
data[list_id]:7f4284774e
data[merges][ADDRESS]:
data[merges][BIRTHDAY]:
data[merges][EMAIL]:ct30111998@gmail.com
data[merges][FNAME]:chiarag
type:unsubscribe
"""

class MailchimpWebhookView(CsrfExemptMixin, View):
    def post(self, request, *args, **kwargs):
        data = request.POST
        list_id = data.get('data[list_id]') 
        if str(list_id) == str(MAILCHIMP_EMAIL_LIST_ID):
            hook_type = data.get('data[action]')
            email =  data.get('data[email]')
            responce_status, response = Mailchimp().check_subcription_status(email) 
            sub_status = response['status']
            is_subbed = None
            mailchimp_subscribed = None
            if sub_status == 'subscribed':
                is_subbed, mailchimp_subscribed = (True, True)
            elif sub_status == 'subscribed':
                is_subbed, mailchimp_subscribed = (False, False)
            if is_subbed is not None and mailchimp_subscribed is not None:
                qs = MarketingPreference.objects.filter(user__email__iexact=email)
                if qs.exists():
                    qs.update(subscribed=is_subbed, mailchimp_subscribed=mailchimp_subscribed, mailchimp_msg=str(data))

        return HttpResponse("Thank YOu", status=200)


# def mailchimp_webhook_view(request):
#     data = request.POST
#     list_id = data.get('data[list_id]') 
#     if str(list_id) == str(MAILCHIMP_EMAIL_LIST_ID):
#         hook_type = data.get('data[action]')
#         email =  data.get('data[email]')
#         responce_status, response = Mailchimp().check_subcription_status(email) 
#         sub_status = response['status']
#         is_subbed = None
#         mailchimp_subscribed = None
#         if sub_status == 'subscribed':
#             is_subbed, mailchimp_subscribed = (True, True)
#         elif sub_status == 'subscribed':
#             is_subbed, mailchimp_subscribed = (False, False)
#         if is_subbed is not None and mailchimp_subscribed is not None:
#             qs = MarketingPreference.objects.filter(user__email__iexact=email)
#             if qs.exists():
#                 qs.update(subscribed=is_subbed, mailchimp_subscribed=mailchimp_subscribed, mailchimp_msg=str(data))

#     return HttpResponse("Thank YOu", status=200)




