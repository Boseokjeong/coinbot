from django.db import models
from django.contrib.auth.models import User
from django_cryptography.fields import encrypt


# 사용자의 코인 잔액
class Account(models.Model):
    user = models.ForeignKey('auth.User', on_delete=models.CASCADE)
    coin_balance = models.DecimalField(max_digits=10, decimal_places=2)  # 사용자 계좌의 잔액

# 사용자의 api_key 저장
class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    upbit_api_key = encrypt(models.CharField(max_length=100))
    upbit_secret_key = encrypt(models.CharField(max_length=100))


# 사용자의 거래 내역
class Trade(models.Model):
    account = models.ForeignKey(Account, on_delete=models.CASCADE)
    coin_type = models.CharField(max_length=10)  # 화폐의 종류
    coin_volume = models.DecimalField(max_digits=10, decimal_places=6)  # 거래량
    coin_price = models.DecimalField(max_digits=10, decimal_places=2)  # 거래 가격
    coin_trade_div = models.CharField(max_length=4)  # 거래 유형('buy' or 'sell')
    reg_id = models.IntegerField()
    reg_dtm = models.DateTimeField(auto_now_add=True)  # 거래가 생성된 시간
