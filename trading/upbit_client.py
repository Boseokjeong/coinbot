# upbit_client.py
import requests
from requests.auth import AuthBase
import jwt
import uuid
import logging
from requests.exceptions import RequestException
import websocket
import json

logger = logging.getLogger(__name__)


class UpbitAuth(AuthBase):
    def __init__(self, access_key, secret_key):
        self.access_key = access_key
        self.secret_key = secret_key

    def __call__(self, r):
        # nonce 값은 고유한 값으로 설정합니다 (예: UUID)
        nonce = str(uuid.uuid4())

        # 업비트에서 요구하는 토큰의 payload를 구성합니다.
        payload = {
            'access_key': self.access_key,
            'nonce': nonce,
            # 'query': ...  # 필요한 경우, 쿼리 파라미터를 포함시켜야 할 수도 있습니다.
        }

        # JWT 토큰을 생성합니다.
        jwt_token = jwt.encode(payload, self.secret_key)

        # Authorization 헤더에 JWT 토큰을 포함시킵니다.
        r.headers['Authorization'] = f'Bearer {jwt_token}'
        return r


class UpbitClient:
    def __init__(self, access_key, secret_key):
        self.auth = UpbitAuth(access_key, secret_key)
        self.base_url = 'https://api.upbit.com/v1'

    def get_account_info(self):
        """ 계좌 정보를 가져옵니다. """
        url = f"{self.base_url}/accounts"
        response = requests.get(url, auth=self.auth)
        return response.json()

    def place_order(self, market, order_type, volume, price, ord_type='limit'):
        """매수 또는 매도 주문을 실행합니다."""
        try:
            # 업비트 주문 API 엔드포인트를 사용하여 주문을 실행합니다.
            endpoint = '/orders'
            url = self.base_url + endpoint
            data = {
                'market': market,  # 예: 'KRW-BTC'
                'side': order_type,  # 'buy' 또는 'sell'
                'volume': volume,  # 주문 수량
                'price': price,  # 주문 가격
                'ord_type': ord_type,  # 주문 유형 ('limit'은 지정가 주문)
            }
            response = requests.post(url, auth=self.auth, json=data)
            response.raise_for_status()  # 200 OK 코드가 아닌 경우에 예외를 발생시킵니다.
            return response.json()  # 업비트 API 응답을 반환합니다.
        except RequestException as e:
            logger.error(f"주문 실행 중 오류 발생: {e}")
        return None