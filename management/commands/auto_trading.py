import pandas as pd
from django.core.management.base import BaseCommand
import pyupbit
from trading.gpt4 import load_and_predict
from tensorflow.keras.models import load_model


model = load_model('/Users/seok/Documents/coinbot/trading/ai_model/lstm_model.h5')

class Command(BaseCommand):

    def handle(self, *args, **options):
        ticker = "KRW-BTC"
        # 데이터 가져오기
        df = pyupbit.get_ohlcv(ticker, interval="minute1", count=1001)
        new_df = df[['close']].rename(columns={'close': 'price'})
        new_df['date'] = df.index
        print(new_df.iloc[-1].tolist())
        # after_price = load_and_predict(new_df[['price']])
        # print("-------------")
        # print(after_price[0][0], new_df['date'].iloc[-1] + pd.Timedelta(minutes=1))
            # 이동 평균 계산
            # short_moving_average = get_moving_average(df, short_n=5)
            # long_moving_average = get_moving_average(df, long_n=20)
            #
        # # 골든 크로스/데드 크로스 판단
        # golden_cross_timestamp = df["timestamp"].loc[get_golden_cross(df, short_n=5, long_n=20)]
        # dead_cross_timestamp = df["timestamp"].loc[get_dead_cross(df, short_n=5, long_n=20)]
        #
        # # 매수/매도 주문
        # if golden_cross_timestamp is not None:
        #     upbit.buy_limit_order("KRW-BTC", 1000000, get_close(df, golden_cross_timestamp))
        # elif dead_cross_timestamp is not None:
        #     upbit.sell_limit_order("KRW-BTC", 1000000, get_close(df, dead_cross_timestamp))
        #
        # # 다음 주기를 위해 반복
        # while True:
        #     time.sleep(60 * 60)
        #     df = upbit.get_ohlcv("KRW-BTC", "1day")
        #     short_moving_average = get_moving_average(df, short_n=5)
        #     long_moving_average = get_moving_average(df, long_n=20)
        #     golden_cross_timestamp = df["timestamp"].loc[get_golden_cross(df, short_n=5, long_n=20)]
        #     dead_cross_timestamp = df["timestamp"].loc[get_dead_cross(df, short_n=5, long_n=20)]
        #     if golden_cross_timestamp is not None:
        #         upbit.buy_limit_order("KRW-BTC", 1000000, get_close(df, golden_cross_timestamp))
        #     elif dead_cross_timestamp is not None:
        #         upbit.sell_limit_order("KRW-BTC", 1000000, get_close(df, dead_cross_timestamp))
        #

if __name__ == '__main__':
    Command().handle()