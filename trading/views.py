from django.shortcuts import render, redirect
from .models import Account, Trade
from django.contrib.auth.decorators import login_required
from django.urls import reverse_lazy
from django.views.generic.edit import CreateView
from django.views.generic.edit import UpdateView
from django.contrib.auth.forms import UserCreationForm
from django.utils.decorators import method_decorator
from .forms import UpbitAPIKeyForm
from .upbit_client import UpbitClient
from .models import UserProfile
from .forms import OrderForm

def ticker_view(request):
    return render(request, 'ticker.html')


@login_required
def trade_view(request):
    trades = Trade.objects.filter(account__user=request.user).order_by('-reg_dtm')
    return render(request, 'trades.html', {'trades': trades})



class SignUpView(CreateView):
    form_class = UserCreationForm
    success_url = reverse_lazy('login')
    template_name = 'signup.html'


@method_decorator(login_required, name='dispatch')
class UpbitAPIKeyUpdateView(UpdateView):
    model = UserProfile
    form_class = UpbitAPIKeyForm
    success_url = reverse_lazy('ticker')  # 성공 시 리디렉션할 페이지
    template_name = 'api_key_form.html'

    def get_object(self):
        return UserProfile.objects.get_or_create(user=self.request.user)[0]


@login_required
def account_info_view(request):
    user_profile = UserProfile.objects.get(user=request.user)
    client = UpbitClient(user_profile.upbit_api_key, user_profile.upbit_secret_key)
    account_info = client.get_account_info()
    return render(request, 'account_info.html', {'account_info': account_info})


@login_required
def order_view(request):
    user_profile = UserProfile.objects.get(user=request.user)
    client = UpbitClient(user_profile.upbit_api_key, user_profile.upbit_secret_key)

    if request.method == 'POST':
        form = OrderForm(request.POST)
        if form.is_valid():
            market = form.cleaned_data['market']
            order_type = form.cleaned_data['order_type']
            volume = form.cleaned_data['volume']
            price = form.cleaned_data['price']

            result = client.place_order(market, order_type, volume, price)
            if result and result.get('error') is None:
                # 주문 성공 처리
                return redirect('order_success')
            else:
                # 주문 실패 처리
                return redirect('order_fail')
    else:
        form = OrderForm()

    return render(request, 'order_form.html', {'form': form})
