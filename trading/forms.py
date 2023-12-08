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
    order_type = forms.ChoiceField(choices=[('bid', '매수'), ('ask', '매도')], label='주문 종류')
    order_div = forms.ChoiceField(choices=[('limit','지정가'),('price','시장가(매수)'),('market','시장가(매도)')], label='주문 타입')
    market = forms.CharField(max_length=10, label='코인심볼', help_text='예시: KRW-BTC')
    volume = forms.CharField(max_length=20, label='주문량')
    price = forms.CharField(max_length=20, label='주문가격')