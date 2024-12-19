import requests
import time
from get_symbols import get_filtered_lines  # 匯入標的名稱

# LINE Notify 設定
line_notify_token = '2MMntGqT1ztd6IMYok3VRaT0At65YeLQNrT34mcGpMy'  # LINE Notify Access Token
line_notify_url = 'https://notify-api.line.me/api/notify'

# 參數設定
volume_threshold_high = 5  # 最高成交量
volume_threshold_low = 2   # 最低成交量
big_threshold = 5  # BTC 和 ETH 下跌幅度
other_drop_threshold = 2  # 其他標的下跌幅度

# # 獲取標的名稱並加上 USDT
filtered_lines = get_filtered_lines()
print("獲取標的：", filtered_lines)
symbols = [symbol + "USDT" for symbol in filtered_lines]

#手動輸入標的名稱
# symbols_input = input("請輸入標的名稱（以逗號分隔，例如：BTC,ETH）: ")
# symbols = [symbol.strip() + "USDT" for symbol in symbols_input.split(",")]
# print("標的名稱：", symbols)

# 發送 LINE 通知
def send_line_notify(message):
    headers = {'Authorization': f'Bearer {line_notify_token}'}
    payload = {'message': message}
    try:
        response = requests.post(line_notify_url, headers=headers, data=payload)
        if response.status_code != 200:
            print(f"LINE 通知發送失敗: {response.status_code}, {response.text}")
    except Exception as e:
        print(f"發送通知時出現錯誤: {e}")

# 比較成交量與下跌幅度
def check_volume(symbol):
    url = f'https://fapi.binance.com/fapi/v1/klines?symbol={symbol}&interval=15m&limit=2'
    try:
        response = requests.get(url)
        klines = response.json()
        if len(klines) < 2:
            return

        current_volume = float(klines[1][5])
        previous_volume = float(klines[0][5])
        current_open = float(klines[1][1])
        current_close = float(klines[1][4])
        drop_percentage = max(0, (current_open - current_close) / current_open * 100)

        # 超過5倍成交量，直接通知
        if current_volume > previous_volume * volume_threshold_high:
            send_line_notify(f"{symbol} 成交量: {current_volume / previous_volume:.2f} 倍")
            return

        # 成交量介於2到5倍之間，判斷下跌幅度
        if volume_threshold_low < current_volume / previous_volume <= volume_threshold_high:
            drop_threshold = big_threshold if symbol in ["BTCUSDT", "ETHUSDT"] else other_drop_threshold  #如是BTC或ETH，drop threshold為5%，其他標的為2%
            if drop_percentage >= drop_threshold:
                send_line_notify(f"{symbol} 下跌: -{drop_percentage:.2f}% (成交量: {current_volume / previous_volume:.2f} 倍)")

    except Exception as e:
        print(f"{symbol} 錯誤: {e}")

# 每5分鐘檢查一次
while True:
    for symbol in symbols:
        check_volume(symbol.strip())
    time.sleep(300)
