from django.db import models
from django.conf import settings
from django.db.models.signals import post_save, pre_save
from django.urls import reverse

from accounts.models import GuestEmail

import stripe
stripe.api_key = "sk_test_51NEnIUSHwg3JJjRdO6seL4Wx753kPcQxCDAKgNNkQ3sH0iOoHsEYCzZvm2qbdHd4WWGFPCIqDP1Jgo2KDQtHMtGY005V9CSVMY"

User = settings.AUTH_USER_MODEL
# Create your models here.

class BillingProfileManager(models.Manager):
    def new_or_get(self, request):
        user  = request.user
        guest_email_id = request.session.get('guest_email_id')
        created = False
        obj = None
        if user.is_authenticated:
            'logged in user checkout; remember payment stuff'
            obj, created = self.model.objects.get_or_create(
                            user=user, email = user.email)
        elif guest_email_id is not None:
            'guest user checkout; auto relods payment stuff'
            guest_email_obj = GuestEmail.objects.get(id=guest_email_id)
            obj, created = self.model.objects.get_or_create(email = guest_email_obj.email)
        else:
            pass
        return obj, created


class BillingProfile(models.Model):
    user        = models.OneToOneField(User, null=True, unique=True, blank=True, on_delete=models.CASCADE)
    email       = models.EmailField()
    active      = models.BooleanField(default=True)
    update      = models.DateTimeField(auto_now=True)
    timestamp   = models.DateTimeField(auto_now_add=True)
    customer_id = models.CharField(max_length=120, null=True, blank=True)

    objects     = BillingProfileManager() 

    def __str__(self):
        return self.email
    
    def charge(self, order_obj, card=None):
        return Charge.objects.do(self, order_obj, card)
    
    def get_cards(self):
        return self.card_set.all() # becouse of foragin key relation we using "card_set", in oentoonfield "card" is using
    
    def get_payment_method_url(self):
        return reverse('billing-payment-method')

    @property
    def has_card(self): # we can use this as instance.has_card
        card_qs = self.get_cards()
        return card_qs.exists()  # return True or false

    @property
    def default_card(self):
        default_cards = self.get_cards().filter(active=True, default=True)
        if default_cards.exists():
            return default_cards.first()
        return None
    
    def set_cards_inactive(self):
        cards_qs = self.get_cards()
        cards_qs.update(active=False)
        return cards_qs.filter(active=True).count()
    
def billing_profile_create_receiver(sender, instance,  *args, **kwargs):
    if not instance.customer_id and instance.email:
        print("Actual api request to stripe/braintree")
        customer = stripe.Customer.create(
            email = instance.email
        )
        print(customer)
        instance.customer_id = customer.id

pre_save.connect(billing_profile_create_receiver, sender=BillingProfile)

def user_created_receiver(sender, instance, created, *args, **kwargs):
    if created and instance.email:
        BillingProfile.objects.get_or_create(user=instance, email=instance.email)

post_save.connect(user_created_receiver, sender=User)


class CardManager(models.Manager):
    def all(self, *args, **kwargs):
        return self.get_queryset().filter(active=True)

    def add_new(self, billing_profile, token):
        if token:
            customer = stripe.Customer.retrieve(billing_profile.customer_id,expand=['sources'])
            stripe_card_response = customer.sources.create(source=token)
            new_card = self.model(
                    billing_profile=billing_profile,
                    stripe_id = stripe_card_response.id,
                    brand = stripe_card_response.brand,
                    country = stripe_card_response.country,
                    exp_month = stripe_card_response.exp_month,
                    exp_year = stripe_card_response.exp_year,
                    last4 = stripe_card_response.last4
                )
            new_card.save()
            return new_card
        return None


class Card(models.Model):
    billing_profile = models.ForeignKey(BillingProfile, on_delete=models.CASCADE)
    stripe_id       = models.CharField(max_length=120)
    brand           = models.CharField(max_length=120, null=True, blank=True)
    country         = models.CharField(max_length=20, null=True, blank=True)
    exp_month       = models.IntegerField(null=True, blank=True)
    exp_year        = models.IntegerField(null=True, blank=True)
    last4           = models.CharField(max_length=4, null=True, blank=True)
    default         = models.BooleanField(default=True)
    active          = models.BooleanField(default=True)
    timestamp       = models.DateTimeField(auto_now_add=True)

    objects = CardManager()

    def __str__(self):
        return f"{self.brand} {self.last4}"
    
def new_card_post_save_receiver(sender, instance, created, *args, **kwargs):
    if instance.default:
        billing_profile = instance.billing_profile
        qs = Card.objects.filter(billing_profile=billing_profile).exclude(pk=instance.pk)
        qs.update(default=False)

post_save.connect(new_card_post_save_receiver, sender=Card)


# stripe.Charge.create(
#   amount=2000,
#   currency="usd",
#   customer = BillingProfile.objects.filter(email='chirag@gmail.com').first().stripe_id,
#   source="tok_amex",
#   description="My First Test Charge (created for API docs at https://www.stripe.com/docs/api)",
# )


class ChargeManager(models.Manager):
    def do(self, billing_profile, order_obj, card=None):  # Charge.objects.do()
        card_obj = card
        if card_obj is None:
            cards = billing_profile.card_set.filter(default=True)
            if cards.exists():
                card_obj = cards.first()
        if card_obj is None:
            return False, "No cards available"
        
        # if billing_profile.country == "India" and order_obj.currency != "INR":
        #     return False, "Non-INR transactions in India require shipping/billing address outside India."

        stripe.api_key = stripe.api_key  # Replace with your Stripe API key

        customer_name = "abc"  # Get the customer's full name
        print(billing_profile, "___________________________________________________")
        customer_address = {
            'line1': "21 main strite",
            'line2': "near ring road",
            'city': "ahmedabad",
            'state': "gujarat",
            'postal_code': "382415",
            'country': "india",
        }

        payment_intent = stripe.PaymentIntent.create(
            amount=int(order_obj.total * 100),
            currency='inr',
            customer=billing_profile.customer_id,
            payment_method=card_obj.stripe_id,
            off_session=True,
            confirm=True,
            description='Export Transaction',
            metadata={"order_id": order_obj.order_id},
            shipping={
                'name': customer_name,
                'address': customer_address,
            },
        )
        print(payment_intent)
        outcome = getattr(payment_intent, 'outcome', {})
        outcome_type = outcome.get('type')
        seller_message = outcome.get('seller_message')
        risk_level = outcome.get('risk_level')

        new_charge_obj = self.model(
            billing_profile=billing_profile,
            stripe_id=payment_intent.id,
            paid=payment_intent.status == 'succeeded',
            refunded=False,
            outcome=outcome,
            outcome_type=outcome_type,
            seller_message=seller_message,
            risk_level=risk_level,
        )
        new_charge_obj.save()

        return new_charge_obj.paid, new_charge_obj.seller_message
    

class Charge(models.Model):
    billing_profile = models.ForeignKey(BillingProfile, on_delete=models.CASCADE)
    stripe_id       = models.CharField(max_length=120)
    paid            = models.BooleanField(default=False)
    refunded        = models.BooleanField(default=False)
    outcome         = models.TextField(null=True, blank=True)
    outcome_type    = models.CharField(max_length=120, null=True, blank=True)
    seller_message  = models.CharField(max_length=120, null=True, blank=True)
    risk_level      = models.CharField(max_length=120, null=True, blank=True)

    objects = ChargeManager()

    def __str__(self):
        return f"{self.stripe_id} {self.paid}"



# {
#   "amount": 17876,
#   "amount_capturable": 0,
#   "amount_details": {
#     "tip": {}
#   },
#   "amount_received": 17876,
#   "application": null,
#   "application_fee_amount": null,
#   "automatic_payment_methods": null,
#   "canceled_at": null,
#   "cancellation_reason": null,
#   "capture_method": "automatic",
#   "client_secret": "pi_3NFwzeSHwg3JJjRd0QVRsYwH_secret_N1RpXc66MqTIB5GqTQiQO2GIT",
#   "confirmation_method": "automatic",
#   "created": 1686046802,
#   "currency": "inr",
#   "customer": "cus_O0t44Hq3Re6Nka",
#   "description": "Export Transaction",
#   "id": "pi_3NFwzeSHwg3JJjRd0QVRsYwH",
#   "invoice": null,
#   "last_payment_error": null,
#   "latest_charge": "ch_3NFwzeSHwg3JJjRd0xGoqaVF",
#   "livemode": false,
#   "metadata": {
#     "order_id": "9s4gk04cfq"
#   },
#   "next_action": null,
#   "object": "payment_intent",
#   "on_behalf_of": null,
#   "payment_method": "card_1NFrMZSHwg3JJjRdKzs7eCB1",
#   "payment_method_options": {
#     "card": {
#       "installments": null,
#       "mandate_options": null,
#       "network": null,
#       "request_three_d_secure": "automatic"
#   "source": null,
#   "statement_descriptor": null,
#   "statement_descriptor_suffix": null,
#   "status": "succeeded",
#   "transfer_data": null,
#   "transfer_group": null
# }