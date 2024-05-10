from flask import Flask, jsonify, request

from py.getstock import StockData  # 導入取得股價資訊的類別程式

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
    start_date = request.args.get('start_date')
    end_date = request.args.get('end_date')
    stock_data = StockData(stock_code)
    
    # 獲取近十天股票資訊
    predict_data = stock_data.fetch_historical_data(start_date, end_date)
    
    # 將 pandas DataFrame 轉為 dict，然後自動轉換為 JSON
    return jsonify({
        "stock_code": stock_code,
        "predict_data": predict_data.to_dict('records')
    })

if __name__ == "__main__":
    app.run(debug=True)
