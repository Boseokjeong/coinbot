import pyupbit
from tensorflow.keras.models import load_model
import time
import threading
from management.model.gpt4 import load_and_predict


def handle(interval_time, model):
    # 데이터 가져오기
    df = pyupbit.get_ohlcv("KRW-BTC", interval=interval_time, count=1001)

    # dfrk None인 경우
    if df is None:
        print(f"데이터를 가져오는 데 실패했습니다. interval_time: {interval_time}")
        return  # 혹은 적절한 오류 처리

    new_df = df[['close']].rename(columns={'close': 'price'})
    new_df['date'] = df.index
    new_df = new_df.sort_index(ascending=False)

    # 첫 번째 현재 시간 출력
    now = time.strftime("%Y-%m-%d %H:%M:%S")
    print(now)
    print(f'현재 가격: {new_df.iloc[0].tolist()[0]}')
    print("---------------------------")

    predicted_price = load_and_predict(new_df[['price']], model)[0][0]

    now = time.strftime("%Y-%m-%d %H:%M:%S")
    print(now)
    print(f'예측 가격: {predicted_price}')
    print("---------------------------")
    # time.sleep(60)
    #
    # real_df = pyupbit.get_ohlcv("KRW-BTC", interval=interval_time, count=1)
    # real_price = real_df.iloc[0]['close']

    # 두 번째 현재 시간 출력 (업데이트된 시간)
    # now = time.strftime("%Y-%m-%d %H:%M:%S")
    # print()
    # print(now)
    # print(f"실제 가격: {real_price}")

    # 오차율 구하기
    # error_rate = abs((real_price - predicted_price) / real_price) * 100
    # print(f"오차율: {error_rate:.2f}%")

def run_model(interval_time, model_path):
    model = load_model(model_path)
    handle(interval_time, model)

if __name__ == '__main__':
    # 스레드 리스트 생성
    threads = []

    t1 = threading.Thread(target=run_model,
                          args=("minute1", '/Users/seok/Documents/coinbot/management/data/minute1_model.tf'))
    threads.append(t1)
    t1.start()

    t2 = threading.Thread(target=run_model,
                          args=("minute3", '/Users/seok/Documents/coinbot/management/data/minute3_model.tf'))
    threads.append(t2)
    t2.start()

    t3 = threading.Thread(target=run_model,
                          args=("minute5", '/Users/seok/Documents/coinbot/management/data/minute5_model.tf'))
    threads.append(t3)
    t3.start()

    # 모든 스레드가 종료될 때까지 기다림
    for thread in threads:
        thread.join()

    print("모든 모델 실행 완료")

