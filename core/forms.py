from django import forms

from core.models import Product


class EditProductForm(forms.ModelForm):
    class Meta:
        model = Product
        fields = '__all__'
