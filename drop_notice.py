import os
import requests
import time
import datetime
import pandas as pd
from get_symbols import get_filtered_lines  # 匯入標的名稱
from draw import get_kline_data, plot_kline

# LINE Notify 設定
line_notify_token = ''
line_notify_url = ''

# 參數設定
volume_threshold_high = 5  # 最高成交量
volume_threshold_low = 2  # 最低成交量
big_threshold = 2  # BTC 和 ETH 下跌幅度
other_drop_threshold = 5  # 其他標的下跌幅度

# 變數設定
send_images = True  # 是否傳送圖片
auto_login = True  # 是否使用自動登入來獲取標的
image_save_path = "./images"  # 圖片儲存路徑
file_path = "data.xlsx"  # Excel 文件路徑

# 獲取標的名稱的方法
try:
    if auto_login:
        # 自動登入獲取標的
        filtered_lines = get_filtered_lines()
        filtered_lines = list(set(filtered_lines + ["BTC", "ETH"]))
        symbols = [symbol + "USDT" for symbol in filtered_lines]
    else:
        # 手動輸入標的名稱
        symbols_input = input("請輸入標的名稱（以逗號分隔，例如：BTC,ETH）: ")
        symbols_input += ",BTC,ETH"  # 直接添加 BTC 和 ETH
        symbols_input = symbols_input.replace(" ", "")  # 去除空格
        symbols_input_list = symbols_input.split(",")  # 將字串轉為列表
        symbols_input_list = list(set(symbols_input_list))  # 去重
        symbols = [symbol.strip() + "USDT" for symbol in symbols_input_list]  # 每個標的加上 USDT

    strong_symbols = [symbol for symbol in symbols if symbol not in ["BTCUSDT", "ETHUSDT"]]

    # 將標的存入 txt
    file_name = f"{datetime.date.today()}.txt"
    with open(file_name, "w", encoding="utf-8") as f:
        # 寫入大盤標的
        f.write("###大盤,BINANCE:BTCUSDT.P,BINANCE:ETHUSDT.P\n")
        # 寫入強勢標的
        f.write("###強勢,")
        for symbol in strong_symbols:
            f.write(f"BINANCE:{symbol}.P,")
except Exception as e:
    print(f"發生錯誤: {e}")

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

def save_to_excel(data, file_path, sheet_name):
    try:
        # 將 data 存入DataFrame(new_df)
        new_df = pd.DataFrame(data, columns=["Symbol", "Time", "Change(%)", "Volume", "Price"])

        if os.path.exists(file_path):
            # 文件存在，處理目標工作表
            with pd.ExcelWriter(file_path, engine="openpyxl", mode="a", if_sheet_exists="overlay") as writer:
                # 獲取所有工作表名稱
                workbook = writer.book
                sheet_names = workbook.sheetnames

                if sheet_name not in sheet_names:
                    # 如果目標工作表不存在，創建新的並將new_df數據保存
                    new_df.to_excel(writer, sheet_name=sheet_name, index=False)
                else:
                    # 如果工作表存在，加上新數據
                    existing_data = pd.read_excel(file_path, sheet_name=sheet_name)
                    combined_data = pd.concat([existing_data, new_df], ignore_index=True)
                    combined_data.to_excel(writer, sheet_name=sheet_name, index=False)
        else:
            # 文件不存在，直接創建文件和工作表
            with pd.ExcelWriter(file_path, engine="openpyxl") as writer:
                new_df.to_excel(writer, sheet_name=sheet_name, index=False)

        print(f"成功保存到 Excel")

    except Exception as e:
        print(f"保存到 Excel 時發生錯誤: {e}")

# 比較成交量與下跌幅度的函數
def check_volume(symbol, Notifiction, data):
    url = f'https://fapi.binance.com/fapi/v1/klines?symbol={symbol}&interval=15m&limit=2'
    try:
        response = requests.get(url)
        klines = response.json()
        if len(klines) < 2:
            return False

        current_time = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        current_volume = float(klines[1][5])
        previous_volume = float(klines[0][5])
        current_open = float(klines[1][1])
        current_close = float(klines[1][4])
        drop_percentage = max(0, (current_open - current_close) / current_open * 100)
        rise_percentage = max(0, (current_close - current_open) / current_open * 100)

        if current_volume > previous_volume * volume_threshold_high:
            price_change = f"+{rise_percentage:.2f}%" if current_close > current_open else f"-{drop_percentage:.2f}%"
            message = f"{symbol[:-4]} : {price_change}, {current_volume / previous_volume:.2f} 倍, {current_close}"
            Notifiction.append(message)
            data.append([symbol[:-4], current_time, price_change, f"{current_volume / previous_volume:.2f}", f"{current_close}"])
            return True

        if volume_threshold_low < current_volume / previous_volume <= volume_threshold_high:
            drop_threshold = big_threshold if symbol in ["BTCUSDT", "ETHUSDT"] else other_drop_threshold
            if drop_percentage >= drop_threshold:
                message = f"{symbol[:-4]} : (-{drop_percentage:.2f}%), {current_volume / previous_volume:.2f} 倍, {current_close}"
                Notifiction.append(message)
                data.append([symbol[:-4], current_time, f"-{drop_percentage:.2f}%", f"{current_volume / previous_volume:.2f}", f"{current_close}"])
                return True

        return False
    except Exception as e:
        print(f"{symbol} 錯誤: {type(e).__name__} - {e}")

# 主程式
if __name__ == "__main__":
    try:
        Notifiction = []
        data = []

        if auto_login:
            formatted_filtered_lines = sorted(set(filtered_lines))
            formatted_text = ", ".join(formatted_filtered_lines)
            send_line_notify(f"{datetime.date.today()} 強勢標的：\n{formatted_text}", line_notify_token)
        else:
            symbols_input_list = sorted(set(symbols_input_list))
            formatted_symbols = ", ".join(symbols_input_list)
            send_line_notify(f"{datetime.date.today()} 強勢標的：\n{formatted_symbols}", line_notify_token)

        # 檢查成交量和下跌幅度
        while True:
            try:
                for symbol in symbols:
                    if check_volume(symbol, Notifiction, data):
                        pass

                if Notifiction:
                    notification_message = f"{datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n" + "【名稱：漲跌幅, 成交量, 價格】\n" + "\n" + "\n".join(Notifiction)
                    send_line_notify(notification_message, line_notify_token)
                    save_to_excel(data, file_path, sheet_name="data")
                    
                    for symbol_message in Notifiction:
                        symbol = symbol_message.split()[0]
                        symbol += "USDT"
                        kline_data = get_kline_data(symbol)
                        if kline_data is not None and send_images:
                            image_file_path = os.path.join(image_save_path, f"{symbol}_kline.png")
                            plot_kline(kline_data, symbol, image_file_path)  # 繪製圖表
                            send_line_notify(f"{symbol} 的 K 線圖：", line_notify_token, image_file_path)

                    Notifiction.clear()  # 清空列表，避免重複通知

                time.sleep(300)  # 等待 5 分鐘
            except Exception as e:
                print(f"迴圈內發生錯誤: {e}")
                time.sleep(10)  # 等待 10 秒後繼續
    except Exception as e:
        print(f"主程式運行時出現錯誤: {e}")
