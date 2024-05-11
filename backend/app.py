from flask import Flask, jsonify, request
from sklearn.preprocessing import MinMaxScaler

from py.getstock import StockData  # 導入取得股價資訊的類別程式
from datetime import datetime, timedelta
from tensorflow.keras.models import load_model
import pandas as pd
import numpy as np


# 創建時間序列數據集
def create_dataset(data, time_steps=30, future_days=5):
    X, y = [], []
    for i in range(len(data) - time_steps - future_days + 1):
        X.append(data[i:(i + time_steps), :-1])
        y.append(data[(i + time_steps):(i + time_steps + future_days), -1])  # 未來五天的收盤價
    return np.array(X), np.array(y)

app = Flask(__name__)

@app.route("/<stock_code>/getcurrent")
def get_stock_data(stock_code):
    stock_data = StockData(stock_code)  # 每次請求都實例化新的股票數據對象
    current_data = stock_data.fetch_current_data()  # 獲取當前股票資訊
    return jsonify({"stock_code": stock_code, "current_data": current_data})

@app.route("/<stock_code>/gethistory")
def get_history_data(stock_code):
    start_date = request.args.get('start_date')
    end_date = request.args.get('end_date')
    stock_data = StockData(stock_code)
    
    # 獲取歷史股票資訊
    historical_data = stock_data.fetch_historical_data(start_date, end_date)
    
    # 檢查是否收到有效的數據
    if historical_data is None or historical_data.empty:
        return jsonify({"error": "No data received"}), 400

    # 將 pandas DataFrame 轉為 dict，然後自動轉換為 JSON
    return jsonify({
        "stock_code": stock_code,
        "historical_data": historical_data.to_dict('records')
    })
    
@app.route("/<stock_code>/getpredict")
def get_predict_data(stock_code):
    end_date = datetime.now().strftime('%Y-%m-%d')  # 獲取今天的日期
    start_date = (datetime.now() - timedelta(days=90)).strftime('%Y-%m-%d')  # 獲取90天前的日期
    stock_data = StockData(stock_code)
    
    # 獲取近90天股票資訊
    data = stock_data.fetch_historical_data(start_date, end_date)
    data.index = pd.to_datetime(data['date'])
    data = stock_data.add_technical_indicators(data)
    data.bfill(inplace=True);  # 使用向後填充處理缺失值
    # 儲存處理後的數據集到CSV
    pd.DataFrame(data).to_csv('TSLA_history_cleaned.csv', index=True)
    
    model = load_model('../backend/py/model.h5')  # 載入模型檔
    
    # 選擇特徵
    features = ['open', 'high', 'low', 'close', 'volume', 'macdhist', 'RSI', 'MOM', 'slowk', 'slowd']
    X = data[features]
    
    # 初始化MinMaxScaler並擬合數據
    scaler = MinMaxScaler()
    data = scaler.fit_transform(X)

    # 創建時間序列數據集
    X_series, _ = create_dataset(data, time_steps=30, future_days=5)

    # 使用最後一個時間窗口的數據進行預測
    predictions = model.predict(X_series[-1].reshape(1, -1, X_series.shape[-1]))

    # 確保predictions是二維數組
    predictions = predictions.reshape(-1, 1)

    # 如果預測的是多個特徵，創建一個足夠大的數組用於反標準化
    full_predictions = np.zeros((predictions.shape[0], len(features)))

    # 將預測值填充到相應的特徵位置，假設預測的是第四個特徵
    full_predictions[:, 3] = predictions.flatten()

    # 反正規化預測結果
    predictions = scaler.inverse_transform(full_predictions)[:, 3].tolist()

    # 將預測結果轉為 dict，然後自動轉換為 JSON
    return jsonify({
        "stock_code": stock_code,
        "predict_data": predictions
    })


if __name__ == "__main__":
    app.run(debug=True)
