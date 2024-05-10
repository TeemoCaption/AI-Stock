'''
時間序列機器學習(像是股票分析)：由於這種資料前後相鄰的資料相關性非常高，
為了不破壞這種連續性的特性，所以資料不是採取隨機抽取的作法，
而是將前面 75 天的資料作為訓練集，後面 25 天的樣本就是測試集。

基本上應用在股市這種時間序列資料的機器學習模型，大多全部都採用『前進式學習』
優點：比較貼近真實、減少過度擬合的問題發生
'''


import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from sklearn.preprocessing import MinMaxScaler
from keras.models import Sequential
from keras.layers import LSTM, Dropout, Dense
from keras.callbacks import Callback, EarlyStopping
from sklearn.metrics import mean_squared_error, mean_absolute_error
from keras.regularizers import l1_l2
from keras.losses import Huber


from keras.callbacks import Callback
from sklearn.metrics import mean_squared_error, mean_absolute_error

class MetricsHistory(Callback):
    def __init__(self, X_train, y_train, X_val, y_val):
        self.X_train = X_train
        self.y_train = y_train
        self.X_val = X_val
        self.y_val = y_val
        super().__init__()

    def on_train_begin(self, logs=None):
        self.train_rmse = []
        self.train_mae = []
        self.train_mse = []
        self.train_mape = []
        self.val_rmse = []
        self.val_mae = []
        self.val_mse = []
        self.val_mape = []

    def on_epoch_end(self, epoch, logs=None):
        train_pred = self.model.predict(self.X_train)
        val_pred = self.model.predict(self.X_val)
        
        # 計算RMSE、MAE等，取所有天數的平均
        train_rmse = np.sqrt(np.mean(np.square(self.y_train - train_pred)))
        val_rmse = np.sqrt(np.mean(np.square(self.y_val - val_pred)))
        train_mae = np.mean(np.abs(self.y_train - train_pred))
        val_mae = np.mean(np.abs(self.y_val - val_pred))
        train_mse = np.mean(np.square(self.y_train - train_pred))
        val_mse = np.mean(np.square(self.y_val - val_pred))
        
        # MAPE需要避免除以零的情況
        epsilon = 1e-8
        train_mape = np.mean(np.abs((self.y_train - train_pred) / (self.y_train + epsilon))) * 100
        val_mape = np.mean(np.abs((self.y_val - val_pred) / (self.y_val + epsilon))) * 100

        # 保存歷史記錄
        self.train_rmse.append(train_rmse)
        self.val_rmse.append(val_rmse)
        self.train_mae.append(train_mae)
        self.val_mae.append(val_mae)
        self.train_mse.append(train_mse)
        self.val_mse.append(val_mse)
        self.train_mape.append(train_mape)
        self.val_mape.append(val_mape)

# 讀取資料集
data_path = './original data/TSLA/TSLA_history01.csv'
stock_data = pd.read_csv(data_path).copy() # 建立原始資料的副本

# 選擇後面空值資料做處理
numeric_features = ['macd', 'macdsignal', 'macdhist', 'RSI', 'MOM', 'slowk', 'slowd']
stock_data_numeric = stock_data[numeric_features]
stock_data_numeric = stock_data_numeric.fillna(stock_data_numeric.rolling(5, min_periods=1).mean())
stock_data_numeric.fillna(method='bfill', inplace=True)

# 合併數據
stock_data_final = pd.concat([stock_data[['open', 'high', 'low', 'close', 'volume']], stock_data_numeric], axis=1)

# 資料縮放
scaler = MinMaxScaler()
X_scaled = scaler.fit_transform(stock_data_final)

# 創建時間序列數據集
def create_dataset(data, time_steps=30, future_days=5):
    X, y = [], []
    for i in range(len(data) - time_steps - future_days + 1):
        X.append(data[i:(i + time_steps), :-1])
        y.append(data[(i + time_steps):(i + time_steps + future_days), -1])  # 未來五天的收盤價
    return np.array(X), np.array(y)


# 使用30天的數據作為回測時間
time_steps = 30
future_days = 5
X_series, y_series = create_dataset(X_scaled, time_steps, future_days)

# 分割數據集
train_val_size = int(len(X_series) * 0.90)
val_size = int(train_val_size * 0.15)

X_train_val, X_test = X_series[:train_val_size], X_series[train_val_size:]
y_train_val, y_test = y_series[:train_val_size], y_series[train_val_size:]

X_train, X_val = X_train_val[:-val_size], X_train_val[-val_size:]
y_train, y_val = y_train_val[:-val_size], y_train_val[-val_size:]

# 建立LSTM模型
model = Sequential([
    LSTM(512, return_sequences=True, input_shape=(X_train.shape[1], X_train.shape[2])),
    Dropout(0.3),
    LSTM(256, return_sequences=True),
    Dropout(0.3),
    LSTM(128),
    Dropout(0.3),
    Dense(32, activation='relu'),
    # 添加輸出層
    Dense(5, activation='linear')  # 輸出層使用linear，這個激活函數適合迴歸問題
])

#顯示模型摘要資訊
model.summary()  

# 編譯模型
model.compile(optimizer='adam', loss=Huber())

# 設定早停機制
early_stopping = EarlyStopping(monitor='val_loss', patience=10, verbose=1)

# 在模型訓練時傳入回調，用於在Keras模型訓練過程中記錄性能指標
metrics_history = MetricsHistory(X_train, y_train, X_val, y_val)

history = model.fit(X_train, y_train, epochs=150, batch_size=16, validation_data=(X_val, y_val), callbacks=[early_stopping, metrics_history])

model.save("backend/py/model.keras")

# 繪製訓練和驗證的損失曲線
plt.figure(figsize=(10, 5))
plt.plot(history.history['loss'], label='Train loss')
plt.plot(history.history['val_loss'], label='Validation loss')
plt.title('Train and Validation history loss')
plt.xlabel('Epoch')
plt.ylabel('Loss')
plt.legend()
plt.show()

# 繪製RMSE, MAE, MSE, MAPE
plt.figure(figsize=(14, 10))
plt.subplot(2, 2, 1)
plt.plot(metrics_history.train_rmse, label='Train RMSE')
plt.plot(metrics_history.val_rmse, label='Validation RMSE', linestyle='--')
plt.title('Train and Validation RMSE')
plt.legend()

plt.subplot(2, 2, 2)
plt.plot(metrics_history.train_mae, label='Train MAE')
plt.plot(metrics_history.val_mae, label='Validation MAE', linestyle='--')
plt.title('Train and Validation MAE')
plt.legend()

plt.subplot(2, 2, 3)
plt.plot(metrics_history.train_mse, label='Train MSE')
plt.plot(metrics_history.val_mse, label='Validation MSE', linestyle='--')
plt.title('Train and Validation MSE')
plt.legend()

plt.subplot(2, 2, 4)
plt.plot(metrics_history.train_mape, label='Train MAPE')
plt.plot(metrics_history.val_mape, label='Validation MAPE', linestyle='--')
plt.title('Train and Validation MAPE')
plt.legend()

plt.tight_layout()
plt.show()

# 預測未來五天收盤價
y_pred_test = model.predict(X_test)

# 計算每天的MSE、MAE等，並取平均值
mse = np.mean([mean_squared_error(y_test[:, i], y_pred_test[:, i]) for i in range(y_test.shape[1])])
mae = np.mean([mean_absolute_error(y_test[:, i], y_pred_test[:, i]) for i in range(y_test.shape[1])])
rmse = np.sqrt(mse)  # 基於MSE計算RMSE

# 計算MAPE
mape = np.mean([np.mean(np.abs((y_test[:, i] - y_pred_test[:, i]) / y_test[:, i])) * 100 for i in range(y_test.shape[1])])

print(f"Test MSE: {mse:.4f}")
print(f"Test RMSE: {rmse:.4f}")
print(f"Test MAE: {mae:.4f}")
print(f"Test MAPE: {mape:.4f}%")