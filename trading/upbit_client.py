# upbit_client.py
import requests
from requests.auth import AuthBase
import jwt
import uuid
import logging
from requests.exceptions import RequestException
from urllib.parse import urlencode, unquote
import hashlib


logger = logging.getLogger(__name__)


class UpbitAuth(AuthBase):
    def __init__(self, access_key, secret_key):
        self.access_key = access_key
        self.secret_key = secret_key
        self.query_hash = None

    def set_query_hash(self, query_hash):
        self.query_hash = query_hash

    def __call__(self, r):
        # 업비트에서 요구하는 토큰의 payload를 구성합니다.
        payload = {
            'access_key': self.access_key,
            'nonce': str(uuid.uuid4()),
        }

        if self.query_hash:
            payload.update({
                'query_hash': self.query_hash,
                'query_hash_alg': 'SHA512',
            })

        jwt_token = jwt.encode(payload, self.secret_key)
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

    def place_order(self, market, order_type, volume, price, order_div='limit'):
        """매수 또는 매도 주문을 실행합니다."""
        try:
            # 업비트 주문 API 엔드포인트를 사용하여 주문을 실행합니다.
            url = f"{self.base_url}/orders"
            params = {
                'market': f'{market}',  # 예: 'KRW-BTC'
                'side': f'{order_type}',  # 'bid(매수)' 또는 'ask(매도)'
                'volume': f'{volume}',  # 주문 수량
                'price': f'{price}',  # 주문 가격
                'ord_type': f'{order_div}',  # 주문 유형 ('limit'은 지정가 주문)
            }

            query_string = unquote(urlencode(params)).encode("utf-8")
            m = hashlib.sha512()
            m.update(query_string)
            query_hash = m.hexdigest()

            # UpbitAuth 객체에 query_hash 설정
            self.auth.set_query_hash(query_hash)

            response = requests.post(url, auth=self.auth, data=params)
            response.raise_for_status()  # 200 OK 코드가 아닌 경우에 예외를 발생시킵니다.
            return response.json()  # 업비트 API 응답을 반환합니다.
        except RequestException as e:
            logger.error(f"주문 실행 중 오류 발생: {e}")
        finally:
            # 다음 요청을 위해 query_hash를 초기화
            self.auth.set_query_hash(None)
        return None
