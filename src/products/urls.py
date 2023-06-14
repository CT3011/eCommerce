from django.urls import path

from .views import (
    ProductListView,
    ProductDetailedSlugView,
)

app_name='products'

urlpatterns = [
    path("", ProductListView.as_view(), name="list"),
    path("<str:slug>/", ProductDetailedSlugView.as_view(), name="detail"),
]