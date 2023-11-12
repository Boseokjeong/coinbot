# forms.py
from django import forms
from .models import UserProfile


class UpbitAPIKeyForm(forms.ModelForm):
    class Meta:
        model = UserProfile
        fields = ['upbit_api_key', 'upbit_secret_key']
        widgets = {
            'upbit_api_key': forms.TextInput(attrs={'class': 'form-control'}),
            'upbit_secret_key': forms.TextInput(attrs={'class': 'form-control'}),
        }
        labels = {
            'upbit_api_key': '업비트 API Key',
            'upbit_secret_key': '업비트 Secret Key',
        }


class OrderForm(forms.Form):
    order_type = forms.ChoiceField(choices=[('buy', '매수'), ('sell', '매도')])
    market = forms.CharField(max_length=10)
    volume = forms.DecimalField(max_digits=15, decimal_places=8)
    price = forms.DecimalField(max_digits=15, decimal_places=8)