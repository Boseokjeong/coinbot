import asyncio
import json
import pathlib
import signal
import ssl
import uuid
from datetime import datetime
from functools import partial

import pytz
import websockets

ssl_context = ssl.SSLContext(ssl.PROTOCOL_TLSv1_2)
self_signed_cert = pathlib.Path(__file__).with_name("selfsigned.crt")
ssl_context.load_verify_locations(self_signed_cert)


class Ticker:

    def __init__(self, code, timestamp, open, high, low, close, volume):
        self.code = code
        self.timestamp = timestamp
        self.open = open
        self.high = high
        self.low = low
        self.close = close
        self.volume = volume

    @staticmethod
    def from_json(json):
        return Ticker(
            code=json['code'],
            timestamp=datetime.fromtimestamp(json['trade_timestamp'] / 1000, tz=pytz.timezone('Asia/Seoul')),
            open=json['opening_price'],
            high=json['high_price'],
            low=json['low_price'],
            close=json['trade_price'],
            volume=json['acc_trade_price']
        )

    def __repr__(self):
        return self.__str__()

    def __str__(self):
        return f'Ticker <code: {self.code}, timestamp: {self.timestamp.strftime("%Y-%m-%d %H:%M:%S")}, ' \
               f'open: {self.open}, high: {self.high}, ' \
               f'low: {self.low}, close: {self.close}, volume: {self.volume}>'


async def recv_ticker():
    uri = 'wss://api.upbit.com/websocket/v1'
    # markets = ['KRW-BTC', 'KRW-ETH']
    markets = ['KRW-BTC']

    async with websockets.connect(uri, ssl=ssl_context) as websocket:
        var = asyncio.Event()

        def sigint_handler(var, signal, frame):
            print(f'< recv SIG_INT')
            var.set()

        signal.signal(signal.SIGINT, partial(sigint_handler, var))

        req = [{
            'ticket': str(uuid.uuid4()),
        }, {
            'type': 'ticker',
            'codes': markets
        }]
        print(f"> {req}")
        await websocket.send(json.dumps(req))

        while not var.is_set():
            recv_data = await websocket.recv()
            res = Ticker.from_json(json.loads(recv_data))
            print(f"> {res}")


asyncio.get_event_loop().run_until_complete(recv_ticker())
