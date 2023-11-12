import asyncio
import json
import websockets
from channels.generic.websocket import AsyncWebsocketConsumer
from datetime import datetime
import pytz
import uuid
import ssl
import os

# 현재 실행 중인 파일의 경로를 기준으로 인증서 파일 경로를 설정
current_dir = os.path.dirname(os.path.abspath(__file__))
cert_path = os.path.join(current_dir, 'selfsigned.crt')
key_path = os.path.join(current_dir, 'selfsigned.key')

# SSLContext 생성 및 인증서 파일 로드
ssl_context = ssl.create_default_context(ssl.Purpose.CLIENT_AUTH)
ssl_context.load_cert_chain(certfile=cert_path, keyfile=key_path)


class TickerConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        # if self.scope["user"].is_authenticated:
            # 사용자가 인증된 경우, 그룹에 추가 (예: 'ticker_updates')
        await self.channel_layer.group_add('ticker_updates', self.channel_name)
        await self.accept()
            # Upbit 웹소켓 API로부터 데이터 수신 시작
        asyncio.create_task(self.recv_ticker())
        # else:
            # 인증되지 않은 사용자는 연결 거부
            # await self.close()

    async def disconnect(self, close_code):
        # 그룹에서 제거
        # if self.scope["user"].is_authenticated:
        await self.channel_layer.group_discard('ticker_updates', self.channel_name)

    async def receive(self, text_data):
        # 클라이언트로부터 오는 메시지 처리 (여기서는 필요하지 않을 수 있음)
        pass

    async def send_ticker_data(self, data):
        # 티커 데이터를 그룹의 모든 사용자에게 전송
        await self.channel_layer.group_send(
            'ticker_updates',
            {
                'type': 'ticker.message',
                'message': data
            }
        )

    # 커스텀 메시지 핸들러
    async def ticker_message(self, event):
        # 실제 메시지를 클라이언트에게 보내는 부분
        await self.send(text_data=json.dumps(event['message']))

    async def recv_ticker(self):
        uri = 'wss://api.upbit.com/websocket/v1'
        markets = ['KRW-BTC']
        reconnect_attempts = 0
        while True:
            try:
                # 웹소켓 연결 시도
                async with websockets.connect(uri, ssl=ssl_context) as websocket:
                    req = [{
                        'ticket': str(uuid.uuid4()),
                    }, {
                        'type': 'ticker',
                        'codes': markets
                    }]
                    await websocket.send(json.dumps(req))

                    while True:
                        data = await websocket.recv()
                        await self.process_data(data)

            except websockets.exceptions.ConnectionClosed as e:
                # 연결이 끊어졌을 때 재연결 로직
                reconnect_attempts += 1
                await asyncio.sleep(min(reconnect_attempts * 2, 60))  # 점진적으로 지연 증가
                continue  # 재연결 시도
            except Exception as e:
                # 다른 예외 처리 로직
                print(f"Exception: {e}")
                break  # 심각한 예외 발생시 루프 종료

    async def process_data(self, raw_data):
        # 웹소켓으로부터 수신한 데이터를 처리하는 메서드
        data = json.loads(raw_data)
        ticker_data = {
            'code': data['code'],
            'timestamp': datetime.fromtimestamp(
                data['trade_timestamp'] / 1000,
                tz=pytz.timezone('Asia/Seoul')
            ).isoformat(),  # datetime 객체를 ISO 형식 문자열로 변환
            'open': data['opening_price'],
            'high': data['high_price'],
            'low': data['low_price'],
            'close': data['trade_price'],
            'volume': data['acc_trade_price']
        }
        # 받은 데이터를 채널 레이어를 통해 그룹에 전송
        await self.send_ticker_data(ticker_data)
