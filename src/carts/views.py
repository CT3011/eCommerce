from django.conf import settings
from django.http import JsonResponse
from django.shortcuts import render, redirect

from accounts.forms import LoginForm, GuestForm
from accounts.models import GuestEmail
from addresses.forms import AddressFrom
from addresses.models import Adderss

from billing.models import BillingProfile
from orders.models import Order
from products.models import Product
from .models import Cart

import stripe
STRIPE_SECRET_KEY = getattr(settings,"STRIPE_SECRET_KEY","sk_test_51NEnIUSHwg3JJjRdO6seL4Wx753kPcQxCDAKgNNkQ3sH0iOoHsEYCzZvm2qbdHd4WWGFPCIqDP1Jgo2KDQtHMtGY005V9CSVMY") 
STRIPE_PUB_KEY = getattr(settings,"STRIPE_PUB_KEY","pk_test_51NEnIUSHwg3JJjRdOfRVAkFPlXfP5zA9rA7GZwTmLPa62xfxd24lk3SaXFzWStWnUexGdAcuhCmOU9UkJbnKQUbz00qfYaJrCa")
stripe.api_key = STRIPE_SECRET_KEY

# Create your views here.

def cart_detail_api_view(request):
    cart_obj, new_obj = Cart.objects.new_or_get(request)
    products = [
        {
            "id": x.id,
            "url": x.get_absolute_url(),
            "name": x.title, 
            "price": x.price
        } 
        for x in cart_obj.products.all()] # [<object>, <object>, <object>]
    # products_list = []
    # for x in cart_obj.products.all():
    #     products_list.append(
    #             {"name": x.name, "price": x.price}
    #         )
    cart_data  = {"products": products, "subtotal": cart_obj.subtotal, "total": cart_obj.total}
    return JsonResponse(cart_data)

def cart_home(request):
    cart_obj, new_obj= Cart.objects.new_or_get(request)
    template_name = "carts/home.html"
    context = {"cart": cart_obj}
    return render(request, template_name, context)


def cart_update(request):
    product_id = request.POST.get("product_id")
    if product_id is not None:
        try:
            product_obj = Product.objects.get(id=product_id)
        except Product.DoesNotExist:
            print("Product is gone.")
            return redirect("cart:home")
        cart_obj, new_obj= Cart.objects.new_or_get(request)
        if product_obj in cart_obj.products.all():
            cart_obj.products.remove(product_obj)
            added = False
        else:
            cart_obj.products.add(product_obj)
            added = True
        request.session["cart_items"] = cart_obj.products.count()
        # return redirect(product_obj.get_absolute_url())
        if request.headers.get('x-requested-with') == 'XMLHttpRequest':
            print("ajax request")
            json_data = {
                "added": added,
                "removed": not added,
                "cartItemsCount": cart_obj.products.count()
            }
            return JsonResponse(json_data, status=200)
            # return JsonResponse({"message":"Error 400"}, status=400)
    return redirect("cart:home")


def checkout_home(request):
    cart_obj, cart_created= Cart.objects.new_or_get(request)
    order_obj = None
    if cart_created or cart_obj.products.count() == 0:
        return redirect("cart:home")

    login_form = LoginForm()
    guest_form = GuestForm()    
    address_form = AddressFrom()
    billing_address_id = request.session.get("billing_address_id", None)
    shipping_address_id = request.session.get("shipping_address_id", None)
    
    billing_profile, billing_profile_created = BillingProfile.objects.new_or_get(request)
    
    address_qs = None
    has_card = False
    if billing_profile is not None:
        if request.user.is_authenticated:
            address_qs = Adderss.objects.filter(billing_profile=billing_profile)
        order_obj, order_obj_created = Order.objects.new_or_get(billing_profile, cart_obj)
        if shipping_address_id:
            order_obj.shipping_address = Adderss.objects.get(id=shipping_address_id) 
            del request.session["shipping_address_id"]
        if billing_address_id:
            order_obj.billing_address = Adderss.objects.get(id=billing_address_id)
            del request.session["billing_address_id"]
        if billing_address_id or shipping_address_id:
            order_obj.save()
        has_card = billing_profile.has_card


    if request.method == "POST":
        "Chack that order is done"
        is_prepared = order_obj.check_done()
        if is_prepared:
            did_charge, crg_msg = billing_profile.charge(order_obj)
            if did_charge:
                order_obj.mark_paid()
                request.session['cart_items'] = 0
                del request.session['cart_id']
                if not billing_profile.user:
                    billing_profile.set_cards_inactive()
                return redirect("cart:success")
            else:
                print(crg_msg)
                return redirect("cart:checkout")
    context = { 
                'object': order_obj,
                "billing_profile": billing_profile,
                "login_form":login_form,
                "guest_form":guest_form,
                "address_form":address_form,
                "address_qs": address_qs,
                "has_card": has_card,
                "publish_key": STRIPE_PUB_KEY,
            }
    return render(request, "carts/checkout.html", context)


def checkout_done_view(request):
    return render(request, "carts/checkout-done.html", {})