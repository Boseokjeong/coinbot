import numpy as np
from sklearn.preprocessing import MinMaxScaler
from tensorflow.keras.models import load_model
import pyupbit

def create_sequences(data, seq_length):
    X, y = [], []
    for i in range(len(data) - seq_length):
        seq = data[i:i + seq_length]
        label = data[i + seq_length]
        X.append(seq)
        y.append(label)
    return np.array(X), np.array(y)


def load_and_predict(new_data, model, sequence_length=1000):
    if len(new_data) < sequence_length:
        raise ValueError("Data length is less than the sequence length.")

    # Assuming you have a column 'price' containing the new data
    new_prices = new_data['price'].values.reshape(-1, 1)

    # Normalize the new data using the same scaler
    scaler = MinMaxScaler(feature_range=(0, 1))
    new_prices_scaled = scaler.fit_transform(new_prices)

    # Create sequences for input
    X_new, y_new = create_sequences(new_prices_scaled, sequence_length)

    # Reshape the input data for LSTM
    X_new = X_new.reshape((X_new.shape[0], X_new.shape[1], 1))

    # Make predictions
    predicted_prices_scaled = model.predict(X_new)

    # Inverse transform the predicted values to get the original scale
    predicted_prices = scaler.inverse_transform(predicted_prices_scaled)

    return predicted_prices


if __name__ == '__main__':
    model = load_model('/Users/seok/Documents/coinbot/management/data/minute1_model.tf')
    # 데이터 가져오기
    df = pyupbit.get_ohlcv("KRW-BTC", interval="minute1", count=1001)
    new_df = df[['close']].rename(columns={'close': 'price'})
    new_df['date'] = df.index
    new_df = new_df.sort_index(ascending=False)

    # Load the saved LSTM model
    a = load_and_predict(new_df, model)
    print(a)



    # 여기 new_df에다가 1000개짜리 데이터프레임을 넣으시면 모델이 돌아가서 다음 가격을 줄겁니다.
