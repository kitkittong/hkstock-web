import yfinance as yf
import json
from datetime import datetime
import pytz

# 定義要追蹤的港股清單
stock_list = {
    "0700.HK": "騰訊控股",
    "9988.HK": "阿里巴巴",
    "3690.HK": "美團",
    "0941.HK": "中國移動",
    "1299.HK": "友邦保險"
}

results = []

for code, name in stock_list.items():
    try:
        # 抓取最近一個月的歷史股價
        stock = yf.Ticker(code)
        hist = stock.history(period="1mo")
        if not hist.empty:
            close_price = round(hist['Close'].iloc[-1], 2)
            prev_close = round(hist['Close'].iloc[-2], 2)

            # 這裡示範簡單的量化邏輯 (您可以自由修改條件)
            if close_price > prev_close * 1.02:
                signal = "海龜突破"
                badge = "badge-red"
            elif close_price < prev_close * 0.98:
                signal = "RSI < 25"
                badge = "badge-green"
            else:
                signal = "均線震盪"
                badge = "badge-gray"

            symbol_code = code.split('.')[0]
            results.append({
                "code": code,
                "symbol": f"HKEX:{symbol_code}",
                "name": name,
                "price": close_price,
                "signal": signal,
                "badge": badge
            })
    except Exception as e:
        print(f"Error {code}: {e}")

# 取得現在的香港時間
hk_tz = pytz.timezone('Asia/Hong_Kong')
update_time = datetime.now(hk_tz).strftime('%Y-%m-%d %H:%M:%S')

data = {
    "update_time": update_time,
    "stocks": results
}

# 將最新數據儲存成 data.json 供網頁讀取
with open('data.json', 'w', encoding='utf-8') as f:
    json.dump(data, f, ensure_ascii=False, indent=4)

print("數據更新成功！")
