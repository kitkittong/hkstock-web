import yfinance as yf
import json
from datetime import datetime
import pytz
import pandas as pd

# 定義要追蹤的港股清單，加入所屬板塊與名稱
stock_list = {
    "0700.HK": {"name": "騰訊控股", "sector": "科技互聯網"},
    "9988.HK": {"name": "阿里巴巴-SW", "sector": "科技互聯網"},
    "3690.HK": {"name": "美團-W", "sector": "科技互聯網"},
    "01888.HK": {"name": "建滔積層板", "sector": "電子/PCB"},
    "00489.HK": {"name": "飛榮達", "sector": "電子/PCB"},
    "0883.HK": {"name": "中國海洋石油", "sector": "能源/石油"},
    "03750.HK": {"name": "寧德時代", "sector": "新能源汽車"},
    "01211.HK": {"name": "比亞迪股份", "sector": "新能源汽車"},
    "0005.HK": {"name": "匯豐控股", "sector": "金融銀行"},
    "0939.HK": {"name": "建設銀行", "sector": "金融銀行"}
}

results = []
sector_momentum = {}

# 1. 獲取大盤 (恒生指數 HSI) 數據
try:
    hsi = yf.Ticker("^HSI")
    hsi_hist = hsi.history(period="5d")
    hsi_close = round(hsi_hist['Close'].iloc[-1], 2)
    hsi_change_pct = round(((hsi_close - hsi_hist['Close'].iloc[-2]) / hsi_hist['Close'].iloc[-2]) * 100, 2)
    hsi_data = {"price": hsi_close, "change_pct": hsi_change_pct}
except:
    hsi_data = {"price": "N/A", "change_pct": 0}

# 2. 獲取個股數據與計算技術指標
for code, info in stock_list.items():
    try:
        stock = yf.Ticker(code)
        hist = stock.history(period="1mo")
        
        if not hist.empty and len(hist) >= 20:
            close_price = round(hist['Close'].iloc[-1], 2)
            prev_close = round(hist['Close'].iloc[-2], 2)
            ma5 = hist['Close'].tail(5).mean()
            ma20 = hist['Close'].tail(20).mean()
            
            # 計算動能：5MA 高於 20MA 視為強勢
            momentum_score = ((ma5 - ma20) / ma20) * 100
            
            # 統計板塊動能
            sector = info['sector']
            if sector not in sector_momentum:
                sector_momentum[sector] = []
            sector_momentum[sector].append(momentum_score)

            # 產生訊號
            if momentum_score > 2 and close_price > prev_close:
                signal = "強勢突破"
                badge = "badge-red" # 港股習慣紅升綠跌
            elif momentum_score < -2:
                signal = "弱勢探底"
                badge = "badge-green"
            else:
                signal = "區間震盪"
                badge = "badge-gray"

            symbol_code = code.split('.')[0]
            # 去除前導零以符合 TradingView 格式 (例如 0700 -> 700)
            tv_symbol = str(int(symbol_code)) 
            
            results.append({
                "code": symbol_code,
                "symbol": f"HKEX:{tv_symbol}",
                "name": info['name'],
                "sector": sector,
                "price": close_price,
                "signal": signal,
                "badge": badge
            })
    except Exception as e:
        print(f"Error {code}: {e}")

# 3. 計算各板塊平均動能，找出轉強板塊
strong_sectors = []
for sector, scores in sector_momentum.items():
    avg_score = sum(scores) / len(scores)
    if avg_score > 0:
        strong_sectors.append({"sector": sector, "score": round(avg_score, 2)})

# 按分數排序，取前三名轉強板塊
strong_sectors = sorted(strong_sectors, key=lambda x: x['score'], reverse=True)[:3]

hk_tz = pytz.timezone('Asia/Hong_Kong')
update_time = datetime.now(hk_tz).strftime('%Y-%m-%d %H:%M:%S')

data = {
    "update_time": update_time,
    "hsi": hsi_data,
    "strong_sectors": strong_sectors,
    "stocks": results
}

with open('data.json', 'w', encoding='utf-8') as f:
    json.dump(data, f, ensure_ascii=False, indent=4)

print("專業版數據更新成功！")
