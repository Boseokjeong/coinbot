# indexes =["coin_open_price"]#,"coin_high_price","coin_low_price","coin_trade_price","candle_acc_trade_volume"]

import pyupbit
import numpy as np
from sklearn.preprocessing import MinMaxScaler
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import LSTM, Dense
from tensorflow.keras.callbacks import EarlyStopping
import matplotlib.pyplot as plt


class CoinModel:
    def __init__(self, ticker, interval):
        self.ticker = ticker
        self.interval = interval

    def get_price_data(self):
        # 데이터 가져오기
        try:
            df = pyupbit.get_ohlcv(self.ticker, interval=self.interval, count=10001)

            # 데이터 유효성 검사
            if df is None or df.empty:
                print("반환된 데이터가 없습니다.")
                return None

            new_df = df[['close']].rename(columns={'close': 'price'})
            new_df['date'] = df.index
            new_df = new_df.sort_index(ascending=False)
            indexes = ['price']

            selected_df = new_df.iloc[:10000][indexes].reset_index(drop=True)
            return selected_df
        except Exception as e:
            print(f"Error in get_price_data: {e}")
            return None

    def create_model(self, df, model_name):
        # Load your dataframe with coin prices
        # Assuming you have a column 'price' containing the coin prices
        prices = df.values.reshape(-1, 1)

        # Normalize the data
        scaler = MinMaxScaler(feature_range=(0, 1))
        prices_scaled = scaler.fit_transform(prices)


        # Create sequences of 1000 values for input and corresponding target values
        def create_sequences(data, seq_length):
            X, y = [], []
            for i in range(len(data) - seq_length):
                seq = data[i:i + seq_length]
                label = data[i + seq_length]
                X.append(seq)
                y.append(label)
            return np.array(X), np.array(y)


        # Define the sequence length
        sequence_length = 1000

        # Create sequences and targets
        X, y = create_sequences(prices_scaled, sequence_length)

        # Split the data into training and testing sets
        train_size = int(len(X) * 0.8)
        X_train, X_test = X[:train_size], X[train_size:]
        y_train, y_test = y[:train_size], y[train_size:]

        # Reshape the input data for LSTM
        X_train = X_train.reshape((X_train.shape[0], X_train.shape[1], 1))
        X_test = X_test.reshape((X_test.shape[0], X_test.shape[1], 1))

        # Build the LSTM model
        model = Sequential()
        model.add(LSTM(100, input_shape=(X_train.shape[1], 1)))  # Increased LSTM units
        model.add(Dense(1))
        model.compile(optimizer='adam', loss='mean_squared_error')

        # Define early stopping callback
        early_stopping = EarlyStopping(monitor='val_loss', patience=3, restore_best_weights=True)

        # Train the model with early stopping
        model.fit(X_train, y_train, epochs=1, batch_size=32, validation_data=(X_test, y_test), callbacks=[early_stopping])

        # Evaluate the model
        train_loss = model.evaluate(X_train, y_train, verbose=0)
        test_loss = model.evaluate(X_test, y_test, verbose=0)
        print(f'Training Loss: {train_loss}, Testing Loss: {test_loss}')

        # Make predictions
        predicted_prices_scaled = model.predict(X_test)

        # Inverse transform the predicted values to get the original scale
        predicted_prices = scaler.inverse_transform(predicted_prices_scaled)
        actual_prices = scaler.inverse_transform(y_test.reshape(-1, 1))

        model.save(f'/Users/seok/Documents/coinbot/management/data/{model_name}.tf')

        return [predicted_prices, actual_prices]

    def create_graph(self, predicted_prices, actual_prices, graph_name):
        # Plotting actual vs predicted prices
        plt.figure(figsize=(12, 6))
        plt.plot(actual_prices, label='Actual Prices', color='blue')
        plt.plot(predicted_prices, label='Predicted Prices', color='red')
        plt.title('Actual vs Predicted Prices')
        plt.xlabel('Time')
        plt.ylabel('Price')
        plt.legend()
        plt.savefig(f'/Users/seok/Documents/coinbot/management/data/[{graph_name}] actual_vs_predicted_prices.png'
                    , format='png')
        plt.show()


if __name__ == '__main__':
    interval_time = "minute5"
    bitcoin = CoinModel("KRW-BTC", interval_time)
    minute_data = bitcoin.get_price_data()
    minute_model = bitcoin.create_model(minute_data, f"{interval_time}_model")
    # bitcoin.create_graph(minute_model[0], minute_model[1], f"{interval_time}_model")
