import os
import requests
import time
import datetime
from get_symbols import get_filtered_lines  # 匯入標的名稱
from draw import get_kline_data, plot_kline

# LINE Notify 設定
# 測試:ObJ7Be8NkZb8FPNaubCxELL8CXOkmVCRXuDpsv1BO37
# 正式:2MMntGqT1ztd6IMYok3VRaT0At65YeLQNrT34mcGpMy
line_notify_token = '2MMntGqT1ztd6IMYok3VRaT0At65YeLQNrT34mcGpMy'
line_notify_url = 'https://notify-api.line.me/api/notify'

# 參數設定
volume_threshold_high = 5  # 最高成交量
volume_threshold_low = 2   # 最低成交量
big_threshold = 2  # BTC 和 ETH 下跌幅度
other_drop_threshold = 5  # 其他標的下跌幅度

# 變數設定
send_images = True  # 是否傳送圖片
image_save_path = "./images"  # 圖片儲存路徑

# 獲取標的名稱的方法
try:
    # 自動登入獲取標的
    filtered_lines = get_filtered_lines()
    print("獲取標的：", filtered_lines)
    symbols = [symbol + "USDT" for symbol in filtered_lines]

    # 手動輸入標的名稱
    # symbols_input = input("請輸入標的名稱（以逗號分隔，例如：BTC,ETH）: ")
    # symbols = [symbol.strip() + "USDT" for symbol in symbols_input.split(",")]
    # print("標的名稱：", symbols)

    # 加入 BTC 和 ETH
    symbols = list(set(symbols + ["BTCUSDT", "ETHUSDT"]))

    # 將標的存入 txt
    with open(f"{datetime.date.today()}.txt", "w") as f:
        for symbol in symbols:
            f.write(f"BINANCE:{symbol}.P,")

except Exception as e:
    print(f"獲取標的時出現錯誤: {e}")

# 發送 LINE Notify 的函數
def send_line_notify(message, token, image_path=None):
    url = "https://notify-api.line.me/api/notify"
    headers = {"Authorization": f"Bearer {token}"}
    payload = {"message": message}

    try:
        if send_images and image_path:
            with open(image_path, "rb") as image_file:
                files = {"imageFile": image_file}
                response = requests.post(url, headers=headers, data=payload, files=files)
        else: 
            response = requests.post(url, headers=headers, data=payload)

        # 檢查回應狀態
        if response.status_code == 200:
            print("已成功傳送至 LINE Notify!")
        else:
            print(f"通知傳送失敗，錯誤代碼: {response.status_code}, 訊息: {response.text}")
    except Exception as e:
        print(f"發送通知時出現錯誤: {e}")

# 比較成交量與下跌幅度的函數
def check_volume(symbol):
    url = f'https://fapi.binance.com/fapi/v1/klines?symbol={symbol}&interval=15m&limit=2'
    try:
        response = requests.get(url)
        klines = response.json()
        if len(klines) < 2:
            return False

        current_volume = float(klines[1][5])
        previous_volume = float(klines[0][5])
        current_open = float(klines[1][1])
        current_close = float(klines[1][4])
        drop_percentage = max(0, (current_open - current_close) / current_open * 100)

        if current_volume > previous_volume * volume_threshold_high:
            send_line_notify(f"{symbol} 成交量: {current_volume / previous_volume:.2f} 倍", line_notify_token)
            return True

        if volume_threshold_low < current_volume / previous_volume <= volume_threshold_high:
            drop_threshold = big_threshold if symbol in ["BTCUSDT", "ETHUSDT"] else other_drop_threshold
            if drop_percentage >= drop_threshold:
                send_line_notify(f"{symbol} 下跌: -{drop_percentage:.2f}% (成交量: {current_volume / previous_volume:.2f} 倍)", line_notify_token)
                return True

        return False
    except Exception as e:
        print(f"{symbol} 錯誤: {e}")
        return False

# 主程式
if __name__ == "__main__":
    send_line_notify(f"{datetime.date.today()} 強勢標的：\n{symbols}", line_notify_token)
    while True:
        for symbol in symbols:
            if check_volume(symbol): 
                kline_data = get_kline_data(symbol)  # 獲取完整 K 線數據
                if kline_data is not None and send_images:  # 如果啟用傳送圖片功能
                    image_file_path = os.path.join(image_save_path, f"{symbol}_kline.png")
                    plot_kline(kline_data, symbol, image_file_path)  # 繪製圖表

                    # 發送文字與圖片通知
                    send_line_notify(f"{symbol} 的 K 線圖如下：", line_notify_token, image_file_path)

        time.sleep(300)