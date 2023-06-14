import random
import os
from django.db import models
from django.db.models import Q 
from django.db.models.query import QuerySet
from django.db.models.signals import pre_save, post_save
from django.urls import reverse

from ecommerce.utils import unique_slug_generator

def get_filename_ext(filepath):
    base_name = os.path.basename(filepath)
    name,ext = os.path.splitext(base_name)
    return name, ext

def upload_instance_path(instance, filename):
    new_filename = random.randint(1,3452204104)
    name, ext = get_filename_ext(filename)
    final_filename = f"{new_filename}{ext}"
    return  f"products/{new_filename}/{final_filename}"

# CUSTOM QUERYSET
class ProductQuerySet(models.QuerySet):
    def active(self):
        return self.filter(active=True)

    def featured(self):
        return self.filter(featured=True, active=True)
    
    def search(self, query):
        lookups = (
            Q(title__icontains=query) | 
            Q(description__icontains=query) |
            Q(price__icontains=query) |
            Q(tag__title__icontains = query)
            )
        return self.filter(lookups).distinct()

# MODEL MANAGER
class ProductManager(models.Manager):
    """
        over rite get_queryset method to use custome query sets
    """
    def get_queryset(self):
        return ProductQuerySet(self.model, using=self._db)
    
    def all(self):
        return self.get_queryset().active()
    
    def featured(self):
        return self.get_queryset().featured()

    def get_by_id(self, id):
        qs = self.get_queryset().filter(id=id)
        if qs.count() == 1:
            return qs.first()
        return None
    
    def search(self, query):
        return self.get_queryset().active().search(query)

# Create your models here.
class Product(models.Model):
    title           = models.CharField(max_length=120)
    slug            = models.SlugField(blank=True, unique=True)
    description     = models.TextField()
    price           = models.DecimalField(decimal_places=2, max_digits=20, default=39.99)
    image           = models.ImageField(upload_to=upload_instance_path, blank=True, null=True)
    featured        = models.BooleanField(default=False)
    active          = models.BooleanField(default=True)
    timestamp       = models.DateTimeField(auto_now_add=True)

    objects = ProductManager()

    def __str__(self):
        return self.title
    
    @property
    def name(self):
        self.title

    def get_absolute_url(self):
        # return f"/products/{self.slug}/"
        return reverse("products:detail", kwargs={"slug":self.slug})
    


def product_pre_save_receiver(sender, instance, *args, **kwargs):
    if not instance.slug:
        instance.slug = unique_slug_generator(instance)

pre_save.connect(product_pre_save_receiver, sender=Product)
