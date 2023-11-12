from django.urls import path
from django.views.generic import TemplateView
from .views import (trade_view, SignUpView,
                    UpbitAPIKeyUpdateView, ticker_view, account_info_view, order_view)
from django.conf import settings
from django.conf.urls.static import static
from django.contrib.auth.views import LoginView
from django.contrib.auth.views import LogoutView


urlpatterns = [
    path('', ticker_view, name='ticker'),
    path('account-info/', account_info_view, name='account_info'),
    path('trades/', trade_view, name='trades'),
    path('signup/', SignUpView.as_view(), name='signup'),
    path('login', LoginView.as_view(template_name='login.html', success_url='/'), name='login'),
    path('api-key/', UpbitAPIKeyUpdateView.as_view(), name='api_key_update'),
    path('logout/', LogoutView.as_view(next_page='login'), name='logout'),
    path('order/', order_view, name='order'),
    path('order/success/', TemplateView.as_view(template_name='order_success.html'), name='order_success'),
    path('order/fail/', TemplateView.as_view(template_name='order_fail.html'),name='order_fail'),

              ] + static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
