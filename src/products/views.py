
from typing import Any, Dict
from django.http import Http404
from django.shortcuts import get_object_or_404, render

from django.views.generic.list import ListView
from django.views.generic.detail import DetailView

from analytics.mixins import ObjectViewedMixin
from carts.models import Cart

from .models import Product

# Create your views here.

class ProductFeaturedListView(ListView):
    # queryset = Product.objects.all()
    template_name = "products/list.html"

    def get_queryset(self, *args, **kwargs):
        request = self.request
        return Product.objects.all().featured()
    

class ProductFeaturedDetailedView(ObjectViewedMixin, DetailView):
    # model = Product
    queryset = Product.objects.all().featured()
    template_name = "products/featured-detailed.html"
    

class ProductListView(ListView):
    # queryset = Product.objects.all()
    template_name = "products/list.html"

    def get_context_data(self, *args,**kwargs):
        context = super(ProductListView, self).get_context_data(*args, **kwargs)
        cart_obj, new_obj= Cart.objects.new_or_get(self.request)
        context['cart'] = cart_obj
        return context

    def get_queryset(self, *args, **kwargs):
        request = self.request
        return Product.objects.all()
    # def get_context_data(self, *args, **kwargs):
    #     context=super(ProductListView, self).get_context_data(*args, **kwargs)
    #     print(context)
    #     return context
    
class ProductDetailedView(ObjectViewedMixin, DetailView):
    # model = Product
    template_name = "products/detailed.html"

    def get_context_data(self, *args,**kwargs):
        context = super(ProductDetailedView, self).get_context_data(*args,**kwargs)
        print(context)
        return context
    
    def get_object(self, *args, **kwargs):
        request = self.request
        pk = self.kwargs.get('pk')
        instance = Product.objects.get_by_id(pk)
        if instance is None:
            raise Http404("Product is not fined")
        return instance
    
    # def get_queryset(self, *args, **kwargs):
    #     request = self.request
    #     pk = self.kwargs.get('pk')
    #     return Product.objects.filter(pk=pk)


class ProductDetailedSlugView(ObjectViewedMixin, DetailView):
    model = Product
    template_name = "products/detailed.html"

    def get_context_data(self, *args,**kwargs):
        context = super(ProductDetailedSlugView, self).get_context_data(*args, **kwargs)
        cart_obj, new_obj= Cart.objects.new_or_get(self.request)
        context['cart'] = cart_obj
        return context

    def get_object(self, *args, **kwargs):
        request = self.request
        slug = self.kwargs.get('slug') 
        # instance = get_object_or_404(Product, slug=slug, active=True)
        try:
            instance = Product.objects.get(slug=slug, active=True)
        except Product.DoesNotExist:
            raise Http404("Not Found")
        except Product.MultipleObjectsReturned:
            qs = Product.objects.filter(slug=slug, active=True)
            instance = qs.filter()
        except:
            raise Http404("uhmmm")
        
        # object_viewed_signal.send(instance.__class__, instance=instance, request=request)
        return instance
