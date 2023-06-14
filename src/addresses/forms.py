from django import forms

from .models import Adderss

class AddressFrom(forms.ModelForm):
    class Meta:
        model = Adderss
        fields = [
            # 'billing_profile',
            # 'address_type',
            'address_line_1',
            'address_line_2',
            'city',
            'country',
            'state',
            'postal_code'
        ]

