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
import requests
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.http import JsonResponse
import pyupbit



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


def search_view(request):
    url = "https://api.upbit.com/v1/market/all?isDetails=false"
    headers = {"accept": "application/json"}
    response = requests.get(url, headers=headers)
    data = response.json()

    search_query = request.GET.get('q')
    if search_query:
        data = [market for market in data if
                search_query.lower() in market.get('korean_name', '').lower() or
                search_query.lower() in market.get('english_name', '').lower()]

    # 페이징 처리
    paginator = Paginator(data, 10)  # 페이지당 10개 항목
    page = request.GET.get('page', 1)
    try:
        markets = paginator.page(page)
    except PageNotAnInteger:
        markets = paginator.page(1)
    except EmptyPage:
        markets = paginator.page(paginator.num_pages)

    if request.headers.get('x-requested-with') == 'XMLHttpRequest':
        # 필터링된 데이터를 JSON 형식으로 반환
        return JsonResponse({
            'markets': list(markets),  # 검색된 결과가 담긴 리스트
            'page': page,
            'num_pages': paginator.num_pages
        }, safe=False)

        # 일반 요청의 경우
    return render(request, 'search.html', {'markets': markets})

@login_required
def order_view(request):
    user_profile = UserProfile.objects.get(user=request.user)
    client = pyupbit.Upbit(user_profile.upbit_api_key, user_profile.upbit_secret_key)

    if request.method == 'POST':
        form = OrderForm(request.POST)
        if form.is_valid():
            market = form.cleaned_data['market']
            order_type = form.cleaned_data['order_type']
            volume = form.cleaned_data['volume']
            price = form.cleaned_data['price']
            order_div = form.cleaned_data['order_div']

            if order_type == 'bid':
                if order_div == 'limit':
                    result, error_message = client.buy_limit_order(market, price, volume)
                    if result is not None:
                        # 주문 성공 처리
                        return redirect('order_success')
                    else:
                        # 주문 실패 처리
                        return render(request, 'order_fail.html', {'error_message': error_message})
    else:
        form = OrderForm()

    return render(request, 'order_form.html', {'form': form})


@login_required
def order_view(request):
    user_profile = UserProfile.objects.get(user=request.user)
    client = pyupbit.Upbit(user_profile.upbit_api_key, user_profile.upbit_secret_key)

    if request.method == 'POST':
        form = OrderForm(request.POST)
        if form.is_valid():
            market = form.cleaned_data['market']
            order_type = form.cleaned_data['order_type']
            volume = form.cleaned_data['volume']
            price = form.cleaned_data['price']
            order_div = form.cleaned_data['order_div']

            if order_type == 'bid':
                if order_div == 'limit':
                    result, error_message = client.buy_limit_order(market, price, volume)
                    if result is not None:
                        # 주문 성공 처리
                        return redirect('order_success')
                    else:
                        # 주문 실패 처리
                        return render(request, 'order_fail.html', {'error_message': error_message})
    else:
        form = OrderForm()

    return render(request, 'order_form.html', {'form': form})

@login_required
def order_list_view(request):
    user_profile = UserProfile.objects.get(user=request.user)
    client = pyupbit.Upbit(user_profile.upbit_api_key, user_profile.upbit_secret_key)

    if request.method == 'POST':
        print(request.POST)
        coin = request.POST.get('coin', 'KRW-BTC')
        state = request.POST.get('state', 'wait')
    else:
        coin = 'KRW-BTC'
        state = 'wait'

    orders = client.get_order(coin, state=state) if coin else []

    context = {
        'orderss': orders,  # 현재 페이지의 주문
        'selected_coin': coin,  # 선택된 코인
        'selected_state': state  # 선택된 주문 상태
    }

    # 일반 요청의 경우
    return render(request, 'order_list.html', context)




