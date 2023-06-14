from django.conf import settings
from django.http import JsonResponse, HttpResponse
from django.shortcuts import render, redirect
from django.utils.http import url_has_allowed_host_and_scheme

# Create your views here.
from .models import BillingProfile, Card

import stripe
STRIPE_SECRET_KEY = getattr(settings,"STRIPE_SECRET_KEY","sk_test_51NEnIUSHwg3JJjRdO6seL4Wx753kPcQxCDAKgNNkQ3sH0iOoHsEYCzZvm2qbdHd4WWGFPCIqDP1Jgo2KDQtHMtGY005V9CSVMY") 
STRIPE_PUB_KEY = getattr(settings,"STRIPE_PUB_KEY","pk_test_51NEnIUSHwg3JJjRdOfRVAkFPlXfP5zA9rA7GZwTmLPa62xfxd24lk3SaXFzWStWnUexGdAcuhCmOU9UkJbnKQUbz00qfYaJrCa")
stripe.api_key = STRIPE_SECRET_KEY


def payment_method_view(request):
    # if request.user.is_authenticated:
        # this is need from stripe stuff
        # billing_profile = request.user.billingprofile
        # my_customer_id = billing_profile.my_customer_id
    billing_profile, billing_profile_created = BillingProfile.objects.new_or_get(request)
    if not billing_profile:
        return redirect("/cart")

    next_url = None
    next_ = request.GET.get('next')
    if url_has_allowed_host_and_scheme(next_, request.get_host()):
        next_url = next_
    return render(request, 'billing/payment-method.html', {"publish_key":STRIPE_PUB_KEY, "next_url":next_url})


def payment_method_createview(request):
    if request.method == "POST" and request.headers.get('x-requested-with') == 'XMLHttpRequest':
        billing_profile, billing_profile_created = BillingProfile.objects.new_or_get(request)
        if not billing_profile:
            return HttpResponse({"message":"can not find this user"}, status_code=401)
        token = request.POST.get("token")
        if token is not None:
            new_card_obj = Card.objects.add_new(billing_profile, token)
        return JsonResponse({"message": "Success! Your card was added."})
    return HttpResponse("error", status_code=401)

